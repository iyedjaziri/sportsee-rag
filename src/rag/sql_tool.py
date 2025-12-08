from langchain.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_mistralai import ChatMistralAI
from langchain.agents.agent_types import AgentType
from src.core.config import settings

def get_sql_tool(llm=None):
    """
    Creates a LangChain SQL Agent tool.
    """
    db = SQLDatabase.from_uri(settings.DATABASE_URL)
    
    if llm is None:
        llm = ChatMistralAI(
            model="mistral-large-latest", # Use capable model for SQL generation
            temperature=0,
            api_key=settings.MISTRAL_API_KEY
        )

    # We can return the agent executor itself as a tool-like object
    # or wrap it. For now, let's return the agent executor.
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=None, # We can pass specific toolkit if needed, but create_sql_agent handles it with db
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        agent_executor_kwargs={"handle_parsing_errors": True}
    )
    
    return agent_executor

def query_stats(query: str):
    """
    Direct function to query stats, useful for testing.
    """
    agent = get_sql_tool()
    return agent.invoke(query)
