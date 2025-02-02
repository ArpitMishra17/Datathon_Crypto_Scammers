import yfinance as yf
from datetime import date
import requests
from datetime import datetime, timedelta, date
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
HF_API_TOKEN = os.getenv("HF_API_KEY")

# Query parameters
company_name = "Tesla"

# Infer the ticker symbol manually or via an LLM (for now, we'll hardcode it)
# ticker_symbol = "NVDA"

from huggingface_hub import InferenceClient

# Initialize Hugging Face client
client = InferenceClient(api_key=HF_API_TOKEN)

def infer_ticker_symbol(company_name):
    prompt = (
        f"You are an expert in finance. Given the company name '{company_name}', "
        "provide its stock ticker symbol ."
        "Return only the ticker symbol."
    )
    try:
        response = client.text_generation(
            model="google/gemma-2-9b-it",
            prompt=prompt,
            max_new_tokens=10,
            temperature=0.1,
        )
        ticker_symbol = response.strip().upper()
        return ticker_symbol
    except Exception as e:
        print(f"Error during ticker inference: {e}")
        raise ValueError("Failed to infer ticker symbol")

# Infer the ticker symbol
ticker_symbol = infer_ticker_symbol(company_name)
print(f"Inferred Ticker Symbol: {ticker_symbol}")

# Fetch financial data using yfinance
def fetch_financial_data(ticker_symbol):
    # Initialize the Ticker object
    company = yf.Ticker(ticker_symbol)

    # Get the income statement (annual data)
    income_statement = company.financials

    # Check if the required fields exist
    if "Total Revenue" not in income_statement.index or "Net Income" not in income_statement.index:
        raise ValueError("Financial data (revenue or profit) not available for the given ticker symbol.")

    # Extract revenue and net income for the last 2 years
    revenue = income_statement.loc["Total Revenue"].iloc[:2].to_dict()
    net_income = income_statement.loc["Net Income"].iloc[:2].to_dict()

    # Format the data
    financial_data = {
        "revenue": {str(year.date()): value for year, value in revenue.items()},
        "net_income": {str(year.date()): value for year, value in net_income.items()}
    }
    return financial_data

# Fetch and print financial data
try:
    financial_data = fetch_financial_data(ticker_symbol)
    print(f"Financial Data for {company_name} ({ticker_symbol}):")
    print("Revenue:")
    for year, value in financial_data["revenue"].items():
        print(f"  {year}: ${value / 1e9:.2f}B")  # Convert to billions for readability

    print("\nNet Income (Profit):")
    for year, value in financial_data["net_income"].items():
        print(f"  {year}: ${value / 1e9:.2f}B")  # Convert to billions for readability

except Exception as e:
    print(f"Error fetching financial data: {e}")





