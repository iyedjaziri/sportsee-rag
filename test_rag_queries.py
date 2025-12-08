import logging
import asyncio
import logfire
from src.rag.chain import get_rag_agent
from src.core.config import settings

# Setup simple logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_rag")

if settings.LOGFIRE_TOKEN:
    logfire.configure(token=settings.LOGFIRE_TOKEN)
    # logfire.instrument_pydantic()
    # logfire.instrument_langchain() # Optional if supported, but pydantic is key
    print("Logfire configured for test script.")


async def test_rag():
    logger.info("Initializing RAG agent...")
    agent_executor = get_rag_agent()
    
    # Test 1: Qualitative (Vector Store)
    query_text = "What are the main complaints about ankle injuries in the reddit threads?"
    logger.info(f"--- Query: {query_text} ---")
    try:
        response = await agent_executor.ainvoke({"input": query_text})
        print(f"Response: {response['output']}\n")
    except Exception as e:
        logger.error(f"Error in vector query: {e}")

    # Test 2: Quantitative (SQL)
    query_stats = "Who has the highest 3PM in the database?"
    logger.info(f"--- Query: {query_stats} ---")
    try:
        response = await agent_executor.ainvoke({"input": query_stats})
        print(f"Response: {response['output']}\n")
    except Exception as e:
        logger.error(f"Error in SQL query: {e}")

if __name__ == "__main__":
    asyncio.run(test_rag())
