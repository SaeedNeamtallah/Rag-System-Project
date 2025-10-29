from .BaseContoller import BaseController
from models.db_schemas import DataChunk, Project
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json
import logging

logger = logging.getLogger(__name__)

class NLPController(BaseController):
    def __init__(self,vector_client ,generation_client,embedding_client,templete_parser):
        super().__init__()
        self.vector_client = vector_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.templete_parser = templete_parser


    def create_collection_name(self, project_id: str):
        collection_name = f"collection_{project_id}".strip()
        logger.info(f"Collection name for project {project_id}: {collection_name}")
        return collection_name
    
    def reset_vector_db_collection(self,project: Project):
        collection_name = self.create_collection_name(project.project_id)
        self.vector_client.delete_collection(collection_name)
        self.vector_client.create_collection(collection_name, embedding_size=self.embedding_client.embedding_size)

    def get_vector_db_collection_info(self,project: Project):
        collection_name = self.create_collection_name(project.project_id)
        collection_info = self.vector_client.get_collection_info(collection_name)

        return json.loads(json.dumps(collection_info, default=lambda o: o.__dict__))

    def index_into_vector_db(self,project: Project, chunks: List[DataChunk],chunk_ids: List[int],do_reset: bool = False):
        collection_name = self.create_collection_name(project.project_id)
        vectors = []
        ids = []
        metadatas = []
        
        # Check if collection exists and validate embedding size
        if self.vector_client.is_collection_existed(collection_name):
            try:
                collection_info = self.vector_client.get_collection_info(collection_name)
                existing_size = collection_info.config.params.vectors.size
                expected_size = self.embedding_client.embedding_size
                
                if existing_size != expected_size:
                    error_msg = f"Collection '{collection_name}' exists with dimension {existing_size}, but current embedding model uses {expected_size}. Please use do_reset=true to recreate the collection."
                    logger.error(error_msg)
                    raise ValueError(error_msg)
            except AttributeError:
                # If we can't get the size, just log a warning and continue
                logger.warning(f"Could not validate embedding dimensions for collection '{collection_name}'")
        
        # Create collection if not exists (will skip if already exists)
        _ = self.vector_client.create_collection(collection_name, embedding_size=self.embedding_client.embedding_size)
        
        for chunk,chunk_id in zip(chunks,chunk_ids):
            embedding = self.embedding_client.embed_text(chunk.chunk_text,document_type=DocumentTypeEnum.DOCUMENT.value)
            vectors.append(embedding)
            ids.append(chunk_id)
            metadatas.append({
                "chunk_project_id": str(project.project_id),
                "chunk_text": chunk.chunk_text,
                "chunk_order": chunk.chunk_order,
                "chunk_metadata": chunk.chunk_metadata
            })
        # step4: insert into vector db
        _ = self.vector_client.insert_many(
            collection_name=collection_name,
            texts=chunks,
            metadata=metadatas,
            vectors=vectors,
            record_ids=chunk_ids,
        )
        return {
            "indexed_count": len(chunks)
        }
    
    def search_vector_db(self,project: Project,text: str,limit: int =5):
        collection_name = self.create_collection_name(project.project_id)
        query_embedding = self.embedding_client.embed_text(text,document_type=DocumentTypeEnum.QUERY.value)
        search_results = self.vector_client.search_by_vector(
            collection_name=collection_name,
            vector=query_embedding,
            limit=limit,
        )
        return search_results
    
    def answer_rag_question(self,project: Project,query: str,limit: int =5):
        # step1: search vector db
        search_results = self.search_vector_db(project,query,limit)
        if not search_results:
            return None,None,None
        
        # step2: construct llm prompt
        system_prompt = self.templete_parser.get("rag","system_prompt")
        logger.info(f"System prompt: {system_prompt[:100]}...")
        
        # Extract text from Qdrant ScoredPoint results
        documents_prompt = "\n".join(
            self.templete_parser.get("rag","document_prompt",{
                "doc_num": idx + 1,
                "chunk_text": doc.payload.get("chunk_text", ""),
            }) for idx, doc in enumerate(search_results)
        )
        logger.info(f"Documents prompt length: {len(documents_prompt)}")

        footer_prompt = self.templete_parser.get("rag","footer_prompt",{"query": query})
        logger.info(f"Footer prompt: {footer_prompt}")

        # Construct chat history as list with system message
        system_message = self.generation_client.construct_prompt(
            prompt=system_prompt,
            role=self.generation_client.enums.SYSTEM.value,
        )
        logger.info(f"System message: {system_message}")
        
        chat_history = [system_message]

        full_prompt = "\n".join([documents_prompt, footer_prompt])
        logger.info(f"Full prompt preview: {full_prompt[:200]}...")
        logger.info(f"Full prompt length: {len(full_prompt)}")
        
        # Log the complete message structure
        user_message_preview = full_prompt[:300] + "..." if len(full_prompt) > 300 else full_prompt
        logger.info(f"Will send to LLM - System: {system_message.get('content', '')[:100]}... | User: {user_message_preview}")

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history,
        )

        return answer, full_prompt, chat_history

