
import os
import pandas as pd
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_mistralai import ChatMistralAI, MistralAIEmbeddings
from src.core.config import settings
from src.rag.chain import get_rag_agent

# 1. Setup Mistral for Ragas
mistral_llm = ChatMistralAI(
    model="mistral-large-latest",
    api_key=settings.MISTRAL_API_KEY,
    temperature=0
)
mistral_embeddings = MistralAIEmbeddings(
    model="mistral-embed",
    api_key=settings.MISTRAL_API_KEY
)

ragas_llm = LangchainLLMWrapper(mistral_llm)
ragas_embeddings = LangchainEmbeddingsWrapper(mistral_embeddings)

# Ragas expects specific metric configuration if not using OpenAI
# We inject the llm/embeddings into the metrics or the evaluate function (depending on Ragas version, newer versions use `llm=` in evaluate)

def evaluate_rag():
    print("Initializing RAG Agent...")
    agent = get_rag_agent()
    
    # Define Evaluation Dataset (Simple & Complex)
    test_questions = [
        # Simple RAG (Vector)
        "What are the rules regarding goaltending?",
        # Simple SQL
        "How many points did Lebron James average in 2023?",
        # Complex Hybrid
        "Compare the average points of Curry with the rule about 3-point lines."
    ]
    
    ground_truths = [
        ["Goaltending allows the defense to not touch the ball while it's on downward flight."],
        ["LeBron James averaged X points."],
        ["Curry averaged Y. The 3-point line is at Z distance."]
    ]
    
    results = {
        "question": [],
        "answer": [],
        "contexts": [],
        "ground_truth": []
    }
    
    print("Running Generation...")
    for i, q in enumerate(test_questions):
        print(f"Resolving: {q}")
        try:
            response = agent.invoke({"input": q})
            answer = response["output"]
        except Exception as e:
            print(f"Error resolving query '{q}': {e}")
            answer = "Error generating answer."
            response = {} # Empty response to trigger no context

        
        # Extract contexts from intermediate steps
        contexts = []
        if "intermediate_steps" in response:
            for params, tool_output in response["intermediate_steps"]:
                # tool_output is usually the tool result (string or list of Docs)
                if hasattr(tool_output, 'content'): # LangChain Document
                    contexts.append(tool_output.content)
                elif isinstance(tool_output, str):
                    contexts.append(tool_output)
                elif isinstance(tool_output, list): # List of Documents
                     for doc in tool_output:
                         if hasattr(doc, 'page_content'):
                             contexts.append(doc.page_content)
                         else:
                             contexts.append(str(doc))
        
        if not contexts:
            contexts = ["No context retrieved"] 
        
        results["question"].append(q)
        results["answer"].append(answer)
        results["contexts"].append(contexts)
        results["ground_truth"].append(ground_truths[i])

    dataset = Dataset.from_dict(results)
    
    print("Running Evaluation with Ragas...")
    metrics = [faithfulness, answer_relevancy, context_precision]
    
    # Configure metrics with Mistral (if supported by installed Ragas version, otherwise defaults to OpenAI and might fail)
    # For newer Ragas, pass llm to evaluate()
    
    scores = evaluate(
        dataset,
        metrics=metrics,
        llm=ragas_llm,
        embeddings=ragas_embeddings
    )
    
    print("Evaluation Scores:", scores)
    df = scores.to_pandas()
    df.to_csv("evaluation_results.csv", index=False)
    print("Results saved to evaluation_results.csv")

if __name__ == "__main__":
    evaluate_rag()
