import logging
from fastapi import APIRouter, HTTPException,status ,Depends ,UploadFile
from fastapi.responses import JSONResponse
from typing import List ,Optional
from controllers import DataController
from helper import get_settings, Settings
from langchain.document_loaders import TextLoader, PyPDFLoader
import aiofiles


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
    
    unique_file_path = data_controller.generate_unique_filepath(project_id, file.filename)

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
        content={"status": "file_upload_success", "message": "File uploaded successfully."}
    )



    # # Here you would typically save the file and process it as needed

    # if file.content_type == "application/pdf":
    #     loader = PyPDFLoader(file_path)
    # else:
    #     loader = TextLoader(file_path)
    # documents = loader.load()

    # # load the file in chunks and save to database file_path
    # for i, doc in enumerate(documents):
    #     chunk_file_path = f"{file_path}_chunk_{i}.txt"
    #     with open(chunk_file_path, "w", encoding="utf-8") as chunk_file:
    #         chunk_file.write(doc.page_content)
    #     # Here you would typically save the chunk_file_path to your database
    #     data_controller.save_chunk_to_db(project_id, chunk_file_path)
            

    # return {"filename": file.filename, "content_type": file.content_type}

