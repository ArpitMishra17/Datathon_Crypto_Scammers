from backend.faiss_rag import StockAnalysisRAG
import os

# Initialize with your configurations
FAISS_INDEX_PATH = "stock_index.faiss"

# Create analyzer instance
analyzer = StockAnalysisRAG(FAISS_INDEX_PATH)

# Get analysis for a specific stock
symbol = "AAPL"  # Example stock symbol
prices, analysis = analyzer.get_stock_insights(symbol)

print(f"\nMonthly Average Prices for {symbol}:")
print(prices)
print("\nStock Analysis:")
print(analysis)

# stock_data = analyzer.debug_data("AAPL")
# print("\nAttempting monthly averages...")
# monthly_data = analyzer.get_monthly_averages("AAPL")
# print("\nMonthly averages:", monthly_data.head())