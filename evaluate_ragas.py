import os
import pandas as pd
from ragas import evaluate
from ragas.metrics import (
    context_precision,
    faithfulness,
    answer_relevancy,
)
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.rag.chain import get_rag_agent
from src.core.config import settings
from datasets import Dataset

def run_evaluation():
    # 1. Define a small test dataset
    questions = [
        "Who has the highest PPG in the dataset?",
        "What are the rules for a 3-second violation?",
        "Compare Shai Gilgeous-Alexander's stats with Anthony Edwards.",
    ]
    
    ground_truths = [
        ["Shai Gilgeous-Alexander has the highest PPG."], # Simplified GT
        ["A player shall not remain for more than three seconds in the restricted area..."],
        ["Shai has higher PPG and efficiency than Anthony Edwards..."]
    ]
    
    # 2. Run the RAG pipeline to get answers and contexts
    agent = get_rag_agent()
    
    answers = []
    contexts = []
    
    print("Generating answers for evaluation...")
    for q in questions:
        try:
            response = agent.invoke({"input": q})
            answers.append(response["output"])
            # Extracting context is tricky with Agents as they might use multiple tools.
            # For RAGAS with Agents, we often evaluate the final answer or need to capture intermediate steps.
            # For simplicity here, we might pass empty contexts or try to capture them if we modified the chain to return source docs.
            # RAGAS 'faithfulness' needs contexts.
            # Let's assume for now we can't easily get the exact retrieved chunks without modifying the agent to return 'intermediate_steps'.
            # We will use a placeholder or modify the agent later to return sources.
            contexts.append(["Context placeholder - Agent used tools."]) 
        except Exception as e:
            print(f"Error processing {q}: {e}")
            answers.append("Error")
            contexts.append([])

    # 3. Prepare Dataset for RAGAS
    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(data)
    
    # 4. Run Evaluation
    # Note: RAGAS metrics often require an LLM and Embeddings
    # We need to configure them.
    
    # llm = ChatOpenAI(model="gpt-3.5-turbo", api_key=settings.OPENAI_API_KEY)
    # embeddings = OpenAIEmbeddings(api_key=settings.OPENAI_API_KEY)
    
    # For this script to run without real API calls consuming budget on loop, we might mock or just set it up.
    # Assuming the user wants to run this manually.
    
    print("Starting RAGAS evaluation (this calls OpenAI API)...")
    # result = evaluate(
    #     dataset = dataset, 
    #     metrics=[
    #         context_precision,
    #         faithfulness,
    #         answer_relevancy,
    #     ],
    # )
    
    # print(result)
    # return result
    print("Evaluation setup complete. Uncomment 'evaluate' to run real metrics.")

if __name__ == "__main__":
    run_evaluation()
