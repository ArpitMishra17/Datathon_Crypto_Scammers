from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, field_serializer
from typing import Dict, List, Union, Optional
from faiss_rag import StockAnalysisRAG
from typing import Dict, Any
import os


# Initialize FastAPI app
app = FastAPI(
    title="Stock Analysis API",
    description="API for stock price analysis using FAISS RAG",
    version="1.0.0"
)

# Initialize analyzer
FAISS_INDEX_PATH = "stock_index.faiss"
analyzer = StockAnalysisRAG(FAISS_INDEX_PATH)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)