import pandas as pd
import numpy as np
import faiss
from datetime import datetime
from groq import Groq
import os
from typing import Dict, Tuple, List
import logging
import dotenv

dotenv.load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_TOKEN")
PATH = "./Data/stock_data.csv"
# print(GROQ_API_KEY)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StockAnalysisRAG:
    def __init__(self, faiss_index_path: str):
        self.index = faiss.read_index(faiss_index_path)
        self.client = Groq(api_key=GROQ_API_KEY)
        self.data = pd.read_csv(PATH)  # Load your original data

    def get_monthly_averages(self, symbol: str) -> pd.DataFrame:
        # Filter data for symbol
        stock_data = self.data[self.data['Symbol'] == symbol].copy()
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
        
        # Calculate monthly averages
        monthly_avg = stock_data.groupby(
            [stock_data['Date'].dt.year.rename('Year'), 
             stock_data['Date'].dt.month.rename('Month')]
        ).agg({
            'Open': 'mean',
            'High': 'mean',
            'Low': 'mean',
            'Close': 'mean',
            'Volume': 'mean'
        })
        
        # Convert index to proper datetime
        monthly_avg = monthly_avg.reset_index()
        monthly_avg['Date'] = pd.to_datetime(
            monthly_avg['Year'].astype(str) + '-' + 
            monthly_avg['Month'].astype(str) + '-01'
        )
        
        return monthly_avg[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]
    
    def get_quarterly_averages(self, symbol: str) -> pd.DataFrame:
        # Filter data for symbol
        stock_data = self.data[self.data['Symbol'] == symbol].copy()
        stock_data['Date'] = pd.to_datetime(stock_data['Date'])
        
        # Calculate quarterly averages
        quarterly_avg = stock_data.groupby(
            [stock_data['Date'].dt.year.rename('Year'), 
             stock_data['Date'].dt.quarter.rename('Quarter')]
        ).agg({
            'Open': 'mean',
            'High': 'mean',
            'Low': 'mean',
            'Close': 'mean',
            'Volume': 'mean'
        })
        
        # Convert index to proper datetime using quarter start dates
        quarterly_avg = quarterly_avg.reset_index()
        quarterly_avg['Month'] = quarterly_avg['Quarter'].map({1: '01', 2: '04', 3: '07', 4: '10'})
        quarterly_avg['Date'] = pd.to_datetime(
            quarterly_avg['Year'].astype(str) + '-' + 
            quarterly_avg['Month'] + '-01'
        )
        
        return quarterly_avg[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']]

    def analyze_stock(self, symbol: str, price_data: pd.DataFrame) -> str:
        """Generate stock analysis using ChatGroq"""
        prompt = f"""
        Analyze the following stock data for {symbol}:
        
        Latest price: ${price_data['Close'].iloc[-1]:.2f}
        Average volume: {price_data['Volume'].mean():.0f}
        Price range: ${price_data['Low'].min():.2f} - ${price_data['High'].max():.2f}
        
        Please provide an in-detail analysis covering:
        1. Overall stock performance and behavior
        2. Volatility assessment
        3. Whether it's better suited for long-term or short-term investment
        4. Key observations about price movements
        Limit the response to 500 words.
        """

        response = self.client.chat.completions.create(
            messages=[{
                "role": "user",
                "content": prompt
            }],
            model="llama-3.1-8b-instant",
            temperature=0.3,
        )
        
        return response.choices[0].message.content

    def get_stock_insights(self, symbol: str) -> Tuple[pd.DataFrame, str]:
        """Main function to get stock analysis and price data"""
        try:
            monthly_prices = self.get_quarterly_averages(symbol)
            analysis = self.analyze_stock(symbol, monthly_prices)
            return monthly_prices, analysis
            
        except Exception as e:
            logger.error(f"Error analyzing stock {symbol}: {str(e)}")
            raise
