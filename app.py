from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator, field_serializer
from typing import Dict, List, Union, Optional
from faiss_rag import StockAnalysisRAG
from typing import Dict, Any
import os
import pandas as pd

# Initialize FastAPI app
app = FastAPI(
    title="Stock Analysis API",
    description="API for stock price analysis using FAISS RAG",
    version="1.0.0"
)

# Initialize analyzer
FAISS_INDEX_PATH = "stock_index.faiss"
analyzer = StockAnalysisRAG(FAISS_INDEX_PATH)

class StockResponse(BaseModel):
    symbol: str
    pricesDF: dict 
    analysis: str

@app.get("/analyze/{symbol}", response_model=StockResponse)
async def analyze_stock(symbol: str):
    try:
        # Get stock analysis
        prices, analysis = analyzer.get_stock_insights(symbol)
        prices = prices.to_dict()

        return StockResponse(
            symbol=symbol,
            pricesDF=prices,
            analysis=analysis
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing stock {symbol}: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)