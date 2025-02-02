import yfinance as yf
import pandas as pd

# Sectors and companies
sectors = {
    "Technology & Communication Services": [
        "AAPL", "NVDA"
    ],
    "Healthcare": [
        "JNJ", "PFE"
    ],
    "Financials & Real Estate": [
        "JPM", "BAC"
    ],
    "Consumer Goods": [
        "AMZN", "WMT"
    ],
    "Industrials & Energy": [
        "XOM", "CVX"
    ]
}

# Function to fetch stock price data
def fetch_stock_data(symbol):
    stock = yf.Ticker(symbol)
    # Fetch historical data for the last 5 years
    hist = stock.history(period="2y")

    hist['Symbol'] = symbol  # Add the stock symbol as a column

    weekly_data = hist.resample('W-FRI').agg({
        'Open': 'first',       
        'High': 'max',         
        'Low': 'min',          
        'Close': 'last',       
        'Volume': 'sum',       
        'Dividends': 'sum',   
        'Stock Splits': 'sum'  
    })
    
    weekly_data.reset_index(inplace=True)
    
    weekly_data['Symbol'] = symbol
    
    return weekly_data[['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']]

# Main function to fetch stock data for all companies
def fetch_stock_data_for_all_companies(sectors):
    all_stock_data = []

    for sector, companies in sectors.items():
        print(f"Fetching data for sector: {sector}")
        for symbol in companies:
            print(f"Fetching stock data for {symbol}")
            stock_data = fetch_stock_data(symbol)
            all_stock_data.append(stock_data)

    # Combine all stock data into one DataFrame
    combined_stock_data = pd.concat(all_stock_data, ignore_index=True)

    # Rounding 6 decimal places to 3
    for i in list(combined_stock_data.columns.values):
        combined_stock_data[i] = combined_stock_data[i].round(3)

    return combined_stock_data

# # Fetch stock data for all companies
# stock_data = fetch_stock_data_for_all_companies(sectors)

# # Save the stock data to a CSV file
# stock_data.to_csv('./Data/stock_data.csv', index=False)

# print("Stock data fetching completed and saved to 'stock_data.csv'.")

class PostData:
    def __init__(self, symbol: str):
        self.sym = symbol

    def fetch_stock_data(self) -> pd.DataFrame:
        stock = yf.Ticker(self.sym)
        # Fetch historical data for the last 2 years
        hist = stock.history(period="2y")
        hist.reset_index(inplace=True)
        hist['Symbol'] = self.sym  # Add the stock symbol as a column
        weekly_data = hist.resample('W-FRI').agg({
        'Open': 'first',       
        'High': 'max',         
        'Low': 'min',          
        'Close': 'last',       
        'Volume': 'sum',       
        'Dividends': 'sum',   
        'Stock Splits': 'sum'  
    })
    
        weekly_data.reset_index(inplace=True)
        
        weekly_data['Symbol'] = self.sym
        
        return weekly_data[['Date', 'Symbol', 'Open', 'High', 'Low', 'Close', 'Volume', 'Dividends', 'Stock Splits']]

    def get_data(self) -> pd.DataFrame:
        stock_data = []
        
        print(f"Fetching data for Company: {self.sym}")
        data = fetch_stock_data(self.sym)
        stock_data.append(data)
        combined_stock_data = pd.concat(stock_data, ignore_index=True)

        # Rounding 6 decimal places to 3
        for i in list(combined_stock_data.columns.values):
            combined_stock_data[i] = combined_stock_data[i].round(3)

        return combined_stock_data
    
    def save_data(self):
        data = self.get_data()
        data.to_csv(f'./Data/{self.sym}_data.csv', index=False)
        print(f"Stock data for {self.sym} saved to './Data/{self.sym}_data.csv'.")

# Example usage
post = PostData("AMD")
post.save_data()