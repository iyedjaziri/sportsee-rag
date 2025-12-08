from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_mistralai import ChatMistralAI
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.core.config import settings
from src.rag.sql_tool import get_sql_tool
from src.rag.vector_store import get_retriever

def get_rag_agent():
    """
    Creates a Hybrid RAG Agent (SQL + Vector).
    """
    # Use Mistral Large or Small depending on availability
    llm = ChatMistralAI(
        model="mistral-large-latest", 
        temperature=0, 
        api_key=settings.MISTRAL_API_KEY
    )
    
    tools = []
    
    # 1. SQL Tool
    sql_agent = get_sql_tool(llm) # Pass mistral llm
    
    # Wrap SQL Agent as a Tool
    from langchain.tools import Tool
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
    
    # Use generic tool calling agent which works with Mistral
    agent = create_tool_calling_agent(llm, tools, prompt)
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        return_intermediate_steps=True,
        handle_parsing_errors=True
    )
    
    return agent_executor
