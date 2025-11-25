from langchain.utilities import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from src.core.config import settings

def get_sql_tool(llm=None):
    """
    Creates a LangChain SQL Agent tool.
    """
    db = SQLDatabase.from_uri(settings.DATABASE_URL)
    
    if llm is None:
        llm = ChatOpenAI(
            model="gpt-3.5-turbo", # Or gpt-4o if available/configured
            temperature=0,
            api_key=settings.OPENAI_API_KEY
        )

    # We can return the agent executor itself as a tool-like object
    # or wrap it. For now, let's return the agent executor.
    agent_executor = create_sql_agent(
        llm=llm,
        toolkit=None, # We can pass specific toolkit if needed, but create_sql_agent handles it with db
        db=db,
        agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        handle_parsing_errors=True
    )
    
    return agent_executor

def query_stats(query: str):
    """
    Direct function to query stats, useful for testing.
    """
    agent = get_sql_tool()
    return agent.invoke(query)
