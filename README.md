# CMP - AI Query Optimizer

A full-stack application for optimizing database queries using AI.

## Project Structure
- `AI_Query_Optimizer/main.py`: The FastAPI backend API.
- `AI_Query_Optimizer/app.py`: The Streamlit frontend UI.
- `AI_Query_Optimizer/database.py`: Database connection and utilities.
- `AI_Query_Optimizer/generate_workload.py`: Script to generate sample database workloads.

## Setup Instructions
1. Install requirements.
2. Run backend: `uvicorn main:app --host 127.0.0.1 --port 8000`
3. Run frontend: `streamlit run app.py`
