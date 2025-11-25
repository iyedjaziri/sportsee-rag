# SportSee Basketball RAG System

## Overview
A production-grade Hybrid RAG (Text + SQL) application for basketball analytics.

## Tech Stack
- **API**: FastAPI
- **LLM**: OpenAI + LangChain
- **Monitoring**: Pydantic Logfire + Evidently AI
- **Infrastructure**: Docker + GitHub Actions

## Setup
1. Install dependencies:
   ```bash
   pip install poetry
   poetry install
   ```
2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```
3. Run the API:
   ```bash
   poetry run uvicorn src.api.main:app --reload
   ```
