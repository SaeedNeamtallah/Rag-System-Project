from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from .schemas.nlp import PushRequest, SearchRequest
import logging

from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers.NLPController import NLPController

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["nlp"]
)

@router.post("/push/{project_id}")
async def push_endpoint(project_id: str, req: Request, payload: PushRequest):
    project_model = await ProjectModel.create_instance(db=req.app.state.db)
    chunk_model = await ChunkModel.create_instance(db=req.app.state.db)

    project = await project_model.get_or_create(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project with id {project_id} not found."}
        )

    # 3) NLP controller
    nlp_controller = NLPController(
        vector_client=req.app.state.vector_db_client,
        generation_client=req.app.state.generation_client,
        embedding_client=req.app.state.embedding_client
    )

    # 4) reset 
    if payload.do_reset:
        nlp_controller.reset_vector_db_collection(project=project)
        logger.info("Reset vector DB collection for project %s", project.id)

    # 5) paginate + index all pages
    page_no = max(payload.page or 1, 1)
    page_size = max(min(payload.page_size or 100, 1000), 1)
    total_indexed = 0

    while True:
        # اعمل جلب صفحة
        chunk_list = await chunk_model.get_project_chunks_paginated(
            project_object_id=project.id,
            page=page_no,
            page_size=page_size
        )

        # 
        if not chunk_list:
            if total_indexed == 0 and page_no == max(payload.page or 1, 1):
                return JSONResponse(
                    status_code=status.HTTP_404_NOT_FOUND,
                    content={"message": f"No chunks found for project {project_id}"}
                )
            break

        chunk_ids = [str(chunk.id) for chunk in chunk_list]

        index_result = nlp_controller.index_into_vector_db(
            project=project,
            chunks=chunk_list,
            chunk_ids=chunk_ids,
            do_reset=False
        )

        indexed_now = int(index_result.get("indexed_count", 0)) if index_result else 0
        if indexed_now == 0:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": f"Indexing failed for project {project_id}"}
            )

        total_indexed += indexed_now
        logger.info(
            "Indexed %s chunks (page=%s, page_size=%s) into vector DB for project %s",
            indexed_now, page_no, page_size, project.id
        )
        #next page
        page_no += 1

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": "Push successful",
            "project_id": project_id,
            "indexed_count": total_indexed
        }
    )




@router.get("/index/info/{project_id}")
async def get_index_info_endpoint(project_id: str, req: Request):
    project_model = await ProjectModel.create_instance(db=req.app.state.db)

    project = await project_model.get_or_create(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project with id {project_id} not found."}
        )

    nlp_controller = NLPController(
        vector_client=req.app.state.vector_db_client,
        generation_client=req.app.state.generation_client,
        embedding_client=req.app.state.embedding_client
    )

    try:
        collection_info = nlp_controller.get_vector_db_collection_info(project=project)
        if collection_info is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": f"Vector DB collection for project {project_id} not found."}
            )
    except Exception as e:
        logger.error("Error getting collection info for project %s: %s", project_id, e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Failed to retrieve collection info: {str(e)}"}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "project_id": project_id,
            "collection_info": collection_info
        }
    )



@router.post("/search/{project_id}")
async def search_endpoint(project_id: str, req: Request, payload: SearchRequest):
    project_model = await ProjectModel.create_instance(db=req.app.state.db)

    project = await project_model.get_or_create(project_id=project_id)
    if not project:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": f"Project with id {project_id} not found."}
        )

    nlp_controller = NLPController(
        vector_client=req.app.state.vector_db_client,
        generation_client=req.app.state.generation_client,
        embedding_client=req.app.state.embedding_client
        
    )

    try:
        search_results = nlp_controller.search_vector_db(
            project=project,
            text=payload.text,
            limit=payload.limit or 5
        )

        if search_results is None:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": f"No results found or collection doesn't exist for project {project_id}"}
            )

        # Serialize Qdrant search results
        serialized_results = [
            {
                "id": str(result.id),
                "score": result.score,
                "payload": result.payload
            }
            for result in search_results
        ]

    except Exception as e:
        logger.error("Error searching in project %s: %s", project_id, e)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": f"Search failed: {str(e)}"}
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "project_id": project_id,
            "query": payload.text,
            "results_count": len(serialized_results),
            "results": serialized_results
        }
    )




