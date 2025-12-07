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
from src.core.logging import logger
from datasets import Dataset
import logging

# Configure structured logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def get_test_cases():
    """
    Returns a dictionary of test cases categorized by complexity.
    """
    return {
        "SIMPLE": {
            "questions": [
                "Who has the highest PPG in the dataset?",
                "What is a 3-second violation?",
            ],
            "ground_truths": [
                ["Shai Gilgeous-Alexander has the highest PPG."],
                ["A player shall not remain for more than three seconds in the restricted area..."],
            ]
        },
        "COMPLEX": {
            "questions": [
                "Compare Shai Gilgeous-Alexander's stats with Anthony Edwards.",
                "List all players with more than 20 PPG and 5 APG.",
            ],
            "ground_truths": [
                ["Shai has higher PPG and efficiency than Anthony Edwards..."],
                ["Luka Doncic, Shai Gilgeous-Alexander, Trae Young..."],
            ]
        },
        "NOISY": {
            "questions": [
                "Who is the best player in terms of points per game? (typo: pnts)",
                "Tell me about the rule for 3 secs in the paint.",
            ],
            "ground_truths": [
                ["Shai Gilgeous-Alexander has the highest PPG."],
                ["A player shall not remain for more than three seconds in the restricted area..."],
            ]
        }
    }

def run_evaluation_for_category(category_name, questions, ground_truths, agent):
    """
    Runs evaluation for a specific category of questions.
    """
    logger.info(f"--- Starting Evaluation for Category: {category_name} ---")
    
    answers = []
    contexts = []
    
    for q in questions:
        try:
            logger.info(f"Processing query: {q}")
            response = agent.invoke({"input": q})
            answers.append(response["output"])
            # Placeholder for context retrieval
            contexts.append(["Context placeholder - Agent used tools."]) 
        except Exception as e:
            logger.error(f"Error processing {q}: {e}")
            answers.append("Error")
            contexts.append([])

    data = {
        "question": questions,
        "answer": answers,
        "contexts": contexts,
        "ground_truth": ground_truths
    }
    dataset = Dataset.from_dict(data)
    
    # Uncomment below to run evaluation.
    # result = evaluate(
    #     dataset = dataset, 
    #     metrics=[context_precision, faithfulness, answer_relevancy],
    # )
    # return result
    
    logger.info(f"Completed generation for {category_name}. (Metrics calculation skipped in demo)")
    return dataset

def run_full_evaluation():
    """
    Main function to run the full evaluation pipeline.
    """
    logger.info("Initializing RAG Agent...")
    try:
        agent = get_rag_agent()
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return

    test_cases = get_test_cases()
    
    results = {}
    
    for category, data in test_cases.items():
        results[category] = run_evaluation_for_category(
            category, 
            data["questions"], 
            data["ground_truths"], 
            agent
        )
        
    logger.info("All evaluations completed successfully.")

if __name__ == "__main__":
    run_full_evaluation()
