import logging
from fastapi import APIRouter, HTTPException, status, Depends, UploadFile
from fastapi.responses import JSONResponse
from typing import List, Optional
from .schemas.dataproces_schemas import ProcessFileRequest 
from controllers import DataController, ProcessControllers
from helper import get_settings, Settings
from langchain.document_loaders import TextLoader, PyPDFLoader
import aiofiles
import os


datarouter= APIRouter(
    prefix="/api/v1/data",
    tags=["data"],
)

@datarouter.post("/upload/{project_id}")
async def process_data(project_id: str, file: UploadFile):

    data_controller = DataController()
    is_valid, response_status = data_controller.validate_file(file)
    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"status": response_status.value, "message": "File validation failed."}
        )

    unique_file_path , unique_filename = data_controller.generate_unique_filepath(project_id, file.filename)

    try:
        async with aiofiles.open(unique_file_path, 'wb') as out_file:
            content = await file.read()  # async read
            await out_file.write(content)  # async write
    except Exception as e:
        logging.error(f"Error saving file: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "file_upload_failed", "message": "Failed to upload file."}
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"status": "file_upload_success", 
                 "file_path": f"{unique_file_path}",
                 "file_id": f"{unique_filename}"
                 }
    )



@datarouter.post("/processall/{project_id}")
async def process_all_files(project_id: str):
    data_controller = DataController()
    process_controller = ProcessControllers()

    project_path = data_controller.get_project_path(project_id)
    if not project_path:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "project_not_found", "message": "Project not found."}

        )
    all_files = [f for f in os.listdir(project_path) if os.path.isfile(os.path.join(project_path, f))]
    if not all_files:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "no_files_found", "message": "No files found in the project."}
        )
    
    all_chunks = []
    failed_files = []
    for file_name in all_files:
        file_path = data_controller.get_file_path(project_id, file_name)
        try:
            chunks = process_controller.process_document(file_path)
            all_chunks.extend(chunks)
        except Exception as e:
            logging.error(f"Error processing file {file_name}: {e}")
            failed_files.append({"file": file_name, "error": str(e)})
            continue  # Skip files that cause errors
    
    if not all_chunks:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "processing_failed", 
                "message": "Failed to process any files. All files are either empty or invalid.",
                "failed_files": failed_files
            }
        )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "processing_success", 
            "total_files": len(all_files),
            "processed_files": len(all_files) - len(failed_files),
            "failed_files": len(failed_files),
            "total_chunks": len(all_chunks),
            "failed_file_details": failed_files if failed_files else [],
            "chunks": [ {"page_content": chunk.page_content, "metadata": chunk.metadata} for chunk in all_chunks ]

        }
    )

@datarouter.post("/processone/{project_id}")
async def process_one_file(project_id: str, request: ProcessFileRequest):
    file_name = request.file_id  # file_id is actually the filename
    chunk_size = request.chunk_size
    overlap_size = request.overlap_size
    do_reset = request.do_reset

    
    logging.info(f"Processing one file request for project_id: {project_id}, file_name: {file_name}")
    data_controller = DataController()
    process_controller = ProcessControllers()

    project_path = data_controller.get_project_path(project_id)
    if not project_path:
        logging.warning(f"Project path not found for project_id: {project_id}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "project_not_found", "message": "Project not found."}

        )
    
    file_path = data_controller.get_file_path(project_id, file_name)
    if not os.path.exists(file_path):
        logging.warning(f"File not found at path: {file_path}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"status": "file_not_found", "message": f"File {file_name} not found in the project."}
        )
    
    try:
        logging.info(f"Starting to process document: {file_path}")
        chunks = process_controller.process_document(file_path, chunk_size, overlap_size)
    except Exception as e:
        logging.error(f"Error processing file {file_name}: {e}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "processing_failed", 
                "message": f"Failed to process file {file_name}. It may be empty or invalid.",
                "error": str(e)
            }
        )
    
    if not chunks:
        logging.warning(f"No chunks were created from file: {file_name}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "status": "processing_failed", 
                "message": f"Failed to process file {file_name}. It may be empty or invalid."
            }
        )
    
    logging.info(f"Successfully processed file {file_name}, created {len(chunks)} chunks.")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "status": "processing_success", 
            "file_name": file_name,
            "total_chunks": len(chunks),
            "chunks": [ {"page_content": chunk.page_content, "metadata": chunk.metadata} for chunk in chunks ]
        }
    )



