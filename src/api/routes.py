from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from src.rag.chain import get_rag_agent
from src.rag.classifier import QueryClassifier
from src.core.logging import logger
from src.core.config import settings
from langchain_mistralai import ChatMistralAI
import time

router = APIRouter()
classifier = QueryClassifier()
chat_llm = ChatMistralAI(model="mistral-large-latest", api_key=settings.MISTRAL_API_KEY, temperature=0.7)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    processing_time: float
    mode: str = "unknown"

@router.post("/chat", response_model=QueryResponse)
async def chat_endpoint(request: QueryRequest):
    """
    Main endpoint. Routes to RAG Agent or Simple Chat based on intent.
    """
    start_time = time.time()
    try:
        logger.info(f"Received query: {request.query}")
        
        # 1. Classify Intent
        needs_rag, confidence, reason = classifier.needs_rag(request.query)
        logger.info(f"Classification: RAG={needs_rag} (Conf={confidence:.2f}, Reason={reason})")
        
        mode = "RAG" if needs_rag else "CHAT"
        answer = ""
        
        if needs_rag:
            # Initialize Agent (RAG + SQL)
            agent = get_rag_agent()
            result = await agent.ainvoke({"input": request.query})
            answer = result["output"]
        else:
            # Simple Chat interaction
            messages = [("system", "You are a helpful assistant for SportSee."), ("user", request.query)]
            response = await chat_llm.ainvoke(messages)
            answer = response.content
        
        duration = time.time() - start_time
        logger.info(f"Request processed in {duration:.2f}s (Mode: {mode})")
        
        return QueryResponse(answer=answer, processing_time=duration, mode=mode)
        
    except Exception as e:
        logger.exception("Error processing query")
        raise HTTPException(status_code=500, detail=str(e))
