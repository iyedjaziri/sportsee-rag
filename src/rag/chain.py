from langchain.agents import create_openai_tools_agent, AgentExecutor
from langchain_openai import ChatOpenAI
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.core.config import settings
from src.rag.sql_tool import get_sql_tool
from src.rag.vector_store import get_retriever

def get_rag_agent():
    """
    Creates a Hybrid RAG Agent (SQL + Vector).
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY)
    
    tools = []
    
    # 1. SQL Tool (wrapped as a tool for the main agent)
    # The SQL Agent is itself an agent, so we might need to wrap it or just expose the DB tool directly.
    # For simplicity in this hybrid setup, let's use the SQLDatabaseToolkit tools directly if possible,
    # or wrap the sql agent executor as a tool.
    # A cleaner way for Hybrid is to give the main agent a "StatsQuery" tool.
    
    from langchain.tools import Tool
    
    sql_agent = get_sql_tool(llm)
    
    sql_tool = Tool(
        name="NBA_Stats_DB",
        func=sql_agent.invoke,
        description="Useful for querying quantitative NBA stats, player averages, game scores, etc. Input should be a natural language question about stats."
    )
    tools.append(sql_tool)
    
    # 2. Vector Retriever Tool
    retriever = get_retriever()
    if retriever:
        retriever_tool = create_retriever_tool(
            retriever,
            "NBA_Rules_and_Discussions",
            "Searches for qualitative info, rules, fan discussions, and context about the NBA."
        )
        tools.append(retriever_tool)
    
    # 3. Create Main Agent
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful NBA Assistant. Use the NBA_Stats_DB tool for stats and numbers. Use the NBA_Rules_and_Discussions tool for opinions, rules, and text context. Combine both if needed."),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])
    
    agent = create_openai_tools_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
    
    return agent_executor
