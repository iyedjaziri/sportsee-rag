from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from src.rag.chain import get_rag_agent
from src.core.logging import logger
import time

router = APIRouter()

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    processing_time: float

@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """
    Main RAG endpoint. Accepts a natural language query and returns an answer.
    """
    start_time = time.time()
    try:
        logger.info(f"Received query: {request.query}")
        
        # Initialize Agent
        # Note: In production, you might want to cache the agent or use a dependency injection
        # to avoid recreating it on every request if initialization is heavy.
        agent = get_rag_agent()
        
        # Invoke Agent
        result = await agent.ainvoke({"input": request.query})
        answer = result["output"]
        
        duration = time.time() - start_time
        logger.info(f"Query processed in {duration:.2f}s")
        
        return QueryResponse(answer=answer, processing_time=duration)
        
    except Exception as e:
        logger.exception("Error processing query")
        raise HTTPException(status_code=500, detail=str(e))
