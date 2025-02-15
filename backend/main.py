from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from datetime import datetime, timedelta, date
from huggingface_hub import InferenceClient
from groq import Groq 
import os
from dotenv import load_dotenv
import yfinance as yf
import math
import fastapi.middleware.cors as cors
# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Apply CORS middleware correctly
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# API keys
HF_API_TOKEN = os.getenv("HF_API_KEY")
GROQ_API_TOKEN = os.getenv("GROQ_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# NewsProcessor class to handle news-related tasks
class NewsProcessor:
    def __init__(self, groq_api_token, news_api_key):
        self.client = Groq(api_key=groq_api_token)
        self.news_api_key = news_api_key

    def fetch_articles(self, company_name: str):
        yesterday_date = (date.today() - timedelta(days=2)).isoformat()
        current_date = date.today().isoformat()
        url = f"https://newsapi.org/v2/everything?q={company_name}&language=en&from={yesterday_date}&to={current_date}&sortBy=relevancy&pageSize=20&apiKey={self.news_api_key}"
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Failed to fetch articles from NewsAPI")
        return response.json().get("articles", [])

    def filter_articles_by_title(self, articles, company_name):
        filtered_articles = [
            article for article in articles
            if company_name.lower() in (article.get("title", "") or "").lower()
        ]
        return filtered_articles

    def preprocess_articles(self, articles):
        processed_articles = []
        for article in articles:
            processed_article = {
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "url": article.get("url", ""),
                "publishedAt": article.get("publishedAt", "")
            }
            processed_articles.append(processed_article)
        return processed_articles

    def evaluate_relevance_batch(self, batch):
        prompt = (
            "You are an expert financial analyst. Your task is to evaluate the relevance of the following news articles "
            "for making investment decisions. Consider factors such as financial performance, market trends, strategic announcements, "
            "regulatory changes, or other material information that could impact the company's stock price. "
            "Provide a relevance score between 0 and 1 for each article, separated by commas.\n\n"
        )
        for i, article in enumerate(batch, 1):
            prompt += f"Article {i}:\n"
            prompt += f"Title: {article['title']}\n"
            prompt += f"Description: {article['description']}\n"
            prompt += f"Content: {article['content']}\n\n"
        prompt += "Relevance Scores (comma-separated):"

        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=50,
            )
            scores = [float(score.strip()) for score in response.choices[0].message.content.split(",")]
        except Exception as e:
            print(f"Error during evaluation: {e}")
            scores = [0.0] * len(batch)
        return scores

    def get_top_articles(self, company_name: str):
        # Fetch articles
        articles = self.fetch_articles(company_name)

        # Filter articles by title
        filtered_articles = self.filter_articles_by_title(articles, company_name)

        # Preprocess articles
        processed_articles = self.preprocess_articles(filtered_articles)

        # Evaluate relevance in batches
        batch_size = 5
        for i in range(0, len(processed_articles), batch_size):
            batch = processed_articles[i:i + batch_size]
            scores = self.evaluate_relevance_batch(batch)
            for j, article in enumerate(batch):
                article["relevance_score"] = scores[j]

        # Sort articles by relevance score
        sorted_articles = sorted(processed_articles, key=lambda x: x.get("relevance_score", 0.0), reverse=True)

        # Select the top 5 articles
        top_articles = sorted_articles[:5]
        return top_articles


# FinancialProcessor class to handle financial data fetching and ticker inference
class FinancialProcessor:
    def __init__(self, groq_api_token):
        self.client = Groq(api_key=groq_api_token)

    def infer_ticker_symbol(self,company_name):
        prompt = (
            f"You are an expert in finance. Given the company name '{company_name}', "
            "provide its stock ticker symbol ."
            "Return only the ticker symbol."
        )
        try:
            response = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Groq model name
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=10,
            )
            ticker_symbol = response.choices[0].message.content.strip().upper()
            return ticker_symbol
        except Exception as e:
            print(f"Error during ticker inference: {e}")
            raise ValueError("Failed to infer ticker symbol")

    def get_financial_data(self, ticker_symbol: str):
        """Fetch financial data for a given ticker symbol using yfinance."""
        try:
            company = yf.Ticker(ticker_symbol)
            income_statement = company.financials

            # Check if required fields exist
            if "Total Revenue" not in income_statement.index or "Net Income" not in income_statement.index:
                raise ValueError("Financial data (revenue or profit) not available for the given ticker symbol.")

            # Extract revenue and net income for the last 5 years
            revenue = income_statement.loc["Total Revenue"].iloc[:5].to_dict()
            net_income = income_statement.loc["Net Income"].iloc[:5].to_dict()

            # Replace NaN values with None (or 0)
            def replace_nan(value):
                return value if not math.isnan(value) else None

            revenue = {str(year): replace_nan(value) for year, value in revenue.items()}
            net_income = {str(year): replace_nan(value) for year, value in net_income.items()}

            # Format the data
            financial_data = {
                "revenue": revenue,
                "net_income": net_income
            }
            return financial_data
        except Exception as e:
            logger.error(f"Error in get_financial_data: {e}")
            raise HTTPException(status_code=500, detail=str(e))


# Instantiate the classes
news_processor = NewsProcessor(GROQ_API_TOKEN, NEWS_API_KEY)
financial_processor = FinancialProcessor(GROQ_API_TOKEN)

# Define request models for the API
class CompanyRequest(BaseModel):
    company_name: str


class FinancialRequest(BaseModel):
    ticker_symbol: str


# API endpoint for top articles
@app.post("/get-top-articles/")
async def get_top_articles_endpoint(request: CompanyRequest):
    company_name = request.company_name.strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name cannot be empty")

    try:
        top_articles = news_processor.get_top_articles(company_name)
        return {"top_articles": top_articles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# API endpoint for financial data
@app.post("/get-financial-data/")
async def get_financial_data_endpoint(request: CompanyRequest):
    company_name = request.company_name.strip()
    print(company_name)
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name cannot be empty")

    try:
        # Infer the ticker symbol using the FinancialProcessor
        ticker_symbol = financial_processor.infer_ticker_symbol(company_name)

        # Fetch financial data using the FinancialProcessor
        financial_data = financial_processor.get_financial_data(ticker_symbol)
        return {"ticker_symbol": ticker_symbol, "financial_data": financial_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    





# from fastapi import FastAPI, HTTPException
# from pydantic import BaseModel
# import requests
# from datetime import datetime, timedelta, date
# from huggingface_hub import InferenceClient
# import os
# from dotenv import load_dotenv
# import yfinance as yf
# from faiss_rag import StockAnalysisRAG
# import pandas as pd

# # Load environment variables
# load_dotenv()

# # Initialize FastAPI app
# app = FastAPI()

# # API keys
# HF_API_TOKEN = os.getenv("HF_API_KEY")
# NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# # Pydantic Stuff
# class StockResponse(BaseModel):
#     symbol: str
#     pricesDF: dict 
#     analysis: str
#     narrative: str

# # Initialize analyzer
# FAISS_INDEX_PATH = "stock_index.faiss"
# analyzer = StockAnalysisRAG(FAISS_INDEX_PATH)
# # NewsProcessor class to handle news-related tasks
# class NewsProcessor:
#     def _init_(self, hf_api_token, news_api_key):
#         self.client = InferenceClient(api_key=hf_api_token)
#         self.news_api_key = news_api_key

#     def fetch_articles(self, company_name: str):
#         yesterday_date = (date.today() - timedelta(days=2)).isoformat()
#         current_date = date.today().isoformat()
#         url = f"https://newsapi.org/v2/everything?q={company_name}&language=en&from={yesterday_date}&to={current_date}&sortBy=relevancy&pageSize=20&apiKey={self.news_api_key}"
#         response = requests.get(url)
#         if response.status_code != 200:
#             raise Exception("Failed to fetch articles from NewsAPI")
#         return response.json().get("articles", [])

#     def filter_articles_by_title(self, articles, company_name):
#         filtered_articles = [
#             article for article in articles
#             if company_name.lower() in (article.get("title", "") or "").lower()
#         ]
#         return filtered_articles

#     def preprocess_articles(self, articles):
#         processed_articles = []
#         for article in articles:
#             processed_article = {
#                 "title": article.get("title", ""),
#                 "description": article.get("description", ""),
#                 "content": article.get("content", ""),
#                 "url": article.get("url", ""),
#                 "publishedAt": article.get("publishedAt", "")
#             }
#             processed_articles.append(processed_article)
#         return processed_articles

#     def evaluate_relevance_batch(self, batch):
#         prompt = (
#             "You are an expert financial analyst. Your task is to evaluate the relevance of the following news articles "
#             "for making investment decisions. Consider factors such as financial performance, market trends, strategic announcements, "
#             "regulatory changes, or other material information that could impact the company's stock price. "
#             "Provide a relevance score between 0 and 1 for each article, separated by commas.\n\n"
#         )
#         for i, article in enumerate(batch, 1):
#             prompt += f"Article {i}:\n"
#             prompt += f"Title: {article['title']}\n"
#             prompt += f"Description: {article['description']}\n"
#             prompt += f"Content: {article['content']}\n\n"
#         prompt += "Relevance Scores (comma-separated):"

#         try:
#             response = self.client.text_generation(
#                 model="mistralai/Mistral-7B-Instruct-v0.3",
#                 prompt=prompt,
#                 max_new_tokens=50,
#                 temperature=0.1,
#             )
#             scores = [float(score.strip()) for score in response.split(",")]
#         except Exception as e:
#             print(f"Error during evaluation: {e}")
#             scores = [0.0] * len(batch)
#         return scores

#     def get_top_articles(self, company_name: str):
#         # Fetch articles
#         articles = self.fetch_articles(company_name)

#         # Filter articles by title
#         filtered_articles = self.filter_articles_by_title(articles, company_name)

#         # Preprocess articles
#         processed_articles = self.preprocess_articles(filtered_articles)

#         # Evaluate relevance in batches
#         batch_size = 5
#         for i in range(0, len(processed_articles), batch_size):
#             batch = processed_articles[i:i + batch_size]
#             scores = self.evaluate_relevance_batch(batch)
#             for j, article in enumerate(batch):
#                 article["relevance_score"] = scores[j]

#         # Sort articles by relevance score
#         sorted_articles = sorted(processed_articles, key=lambda x: x.get("relevance_score", 0.0), reverse=True)

#         # Select the top 5 articles
#         top_articles = sorted_articles[:5]
#         return top_articles


# # FinancialProcessor class to handle financial data fetching and ticker inference
# class FinancialProcessor:
#     def _init_(self, hf_api_token):
#         self.client = InferenceClient(api_key=hf_api_token)

#     def infer_ticker_symbol(self,company_name):
#         prompt = (
#             f"You are an expert in finance. Given the company name '{company_name}', "
#             "provide its stock ticker symbol ."
#             "Return only the ticker symbol."
#         )
#         try:
#             response = self.client.text_generation(
#                 model="google/gemma-2-9b-it",
#                 prompt=prompt,
#                 max_new_tokens=10,
#                 temperature=0.1,
#             )
#             ticker_symbol = response.strip().upper()
#             return ticker_symbol
#         except Exception as e:
#             print(f"Error during ticker inference: {e}")
#             raise ValueError("Failed to infer ticker symbol")

#     def get_financial_data(self, ticker_symbol: str):
#         # Fetch the company's financial data using yfinance
#         company = yf.Ticker(ticker_symbol)

#         # Get the income statement (annual data)
#         income_statement = company.financials

#         # Check if the required fields exist
#         if "Total Revenue" not in income_statement.index or "Net Income" not in income_statement.index:
#             raise ValueError("Financial data (revenue or profit) not available for the given ticker symbol.")


#         # Extract revenue and net income for the last 2 years
#         revenue = income_statement.loc["Total Revenue"].iloc[:5].to_dict()
#         net_income = income_statement.loc["Net Income"].iloc[:5].to_dict()

#         # Format the data
#         financial_data = {
#             "revenue": {str(year): value for year, value in revenue.items()},
#             "net_income": {str(year): value for year, value in net_income.items()}
#         }
#         return financial_data


# # Instantiate the classes
# news_processor = NewsProcessor(HF_API_TOKEN, NEWS_API_KEY)
# financial_processor = FinancialProcessor(HF_API_TOKEN)

# # Define request models for the API
# class CompanyRequest(BaseModel):
#     company_name: str


# class FinancialRequest(BaseModel):
#     ticker_symbol: str


# # API endpoint for top articles
# @app.post("/get-top-articles/")
# async def get_top_articles_endpoint(request: CompanyRequest):
#     company_name = request.company_name.strip()
#     if not company_name:
#         raise HTTPException(status_code=400, detail="Company name cannot be empty")

#     try:
#         top_articles = news_processor.get_top_articles(company_name)
#         return {"top_articles": top_articles}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# # API endpoint for financial data
# @app.post("/get-financial-data/")
# async def get_financial_data_endpoint(request: CompanyRequest):
#     company_name = request.company_name.strip()
#     if not company_name:
#         raise HTTPException(status_code=400, detail="Company name cannot be empty")

#     try:
#         # Infer the ticker symbol using the FinancialProcessor
#         ticker_symbol = financial_processor.infer_ticker_symbol(company_name)

#         # Fetch financial data using the FinancialProcessor
#         financial_data = financial_processor.get_financial_data(ticker_symbol)
#         return {"ticker_symbol": ticker_symbol, "financial_data": financial_data}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @app.get("/analyze/{symbol}", response_model=StockResponse)
# async def analyze_stock(symbol: str):
#     try:
#         # Get stock analysis
#         prices, analysis, narrative = analyzer.get_stock_insights(symbol)
#         prices = prices.to_dict()

#         return StockResponse(
#             symbol=symbol,
#             pricesDF=prices,
#             analysis=analysis,
#             narrative= narrative
#         )
#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error analyzing stock {symbol}: {str(e)}"
#         )