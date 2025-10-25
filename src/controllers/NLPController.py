from .BaseContoller import BaseController
from models.db_schemas import ProjectSchema ,ChunkSchema
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List


class NLPController(BaseController):
    def __init__(self,vector_client ,generation_client,embedding_client,templete_parser):
        super().__init__()
        self.vector_client = vector_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.templete_parser = templete_parser


    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self,project: ProjectSchema):
        collection_name = self.create_collection_name(project.id)
        self.vector_client.delete_collection(collection_name)
        self.vector_client.create_collection(collection_name, embedding_size=self.embedding_client.embedding_size)

    def get_vector_db_collection_info(self,project: ProjectSchema):
        collection_name = self.create_collection_name(project.id)
        collection_info = self.vector_client.get_collection_info(collection_name)
        return collection_info

    def index_into_vector_db(self,project: ProjectSchema, chunks: List[ChunkSchema],chunk_ids: List[int],do_reset: bool = False):
        collection_name = self.create_collection_name(project.id)
        vectors = []
        ids = []
        metadatas = []
        #create collection if not exists
        _= self.vector_client.create_collection(collection_name,embedding_size=self.embedding_client.embedding_size)
        for chunk,chunk_id in zip(chunks,chunk_ids):
            embedding = self.embedding_client.embed_text(chunk.chunk_text,document_type=DocumentTypeEnum.DOCUMENT.value)
            vectors.append(embedding)
            ids.append(chunk_id)
            metadatas.append({
                "chunk_project_id": str(project.id),
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
    
    def search_vector_db(self,project: ProjectSchema,text: str,limit: int =5):
        collection_name = self.create_collection_name(project.id)
        query_embedding = self.embedding_client.embed_text(text,document_type=DocumentTypeEnum.QUERY.value)
        search_results = self.vector_client.search_by_vector(
            collection_name=collection_name,
            vector=query_embedding,
            limit=limit,
        )
        return search_results
    
    def answer_rag_question(self,project: ProjectSchema,query: str,limit: int =5):
        # step1: search vector db
        search_results = self.search_vector_db(project,query,limit)
        if not search_results:
            return None,None,None
        
        # step2: construct llm prompt
        system_prompt = self.templete_parser.get("rag","system_prompt")
        
        # Extract text from Qdrant ScoredPoint results
        documents_prompt = "\n".join(
            self.templete_parser.get("rag","document_prompt",{
                "doc_num": idx + 1,
                "chunk_text": doc.payload.get("chunk_text", ""),
            }) for idx, doc in enumerate(search_results)
        )

        footer_prompt = self.templete_parser.get("rag","footer_prompt",{"query": query})

        # Construct chat history as list with system message
        chat_history = [
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]

        full_prompt = "\n".join([documents_prompt, footer_prompt])

        answer = self.generation_client.generate_text(
            prompt=full_prompt,
            chat_history=chat_history,
        )

        return answer, full_prompt, chat_history

