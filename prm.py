import pandas as pd
import numpy as np
import requests

# FastAPI Endpoint
FASTAPI_URL = "http://localhost:8000//analyze/AAPL"

# Fetch Quarterly Earnings Data from RAG
response = requests.get(FASTAPI_URL)
if response.status_code == 200:
    data = response.json()
    df = pd.DataFrame(data["pricesDF"])  # Convert to Pandas DataFrame
    # Run Bayesian Inference (reuse previous steps)
else:
    print("Error: Unable to fetch data from RAG")

print(df.head())

# Add debug print before processing
print("Available columns:", df.columns.tolist())

# Handle potential case differences in column names
df.columns = df.columns.str.strip().str.title()

num_quarters = len(df)
try:
    price_increase_quarters = df[df["Close"] > df["Open"]]
    price_drop_quarters = df[df["Close"] < df["Open"]]

    P_price_increase = len(price_increase_quarters) / num_quarters
    P_price_drop = len(price_drop_quarters) / num_quarters

    # Step 2: Compute Likelihoods based on Trading Volume
    median_volume = df["Volume"].median()
    high_volume_quarters = df[df["Volume"] > median_volume]

    P_high_vol_given_price_increase = len(price_increase_quarters[price_increase_quarters["Volume"] > median_volume]) / len(price_increase_quarters) if len(price_increase_quarters) > 0 else 0
    P_high_vol_given_price_drop = len(price_drop_quarters[price_drop_quarters["Volume"] > median_volume]) / len(price_drop_quarters) if len(price_drop_quarters) > 0 else 0

    P_high_volume = len(high_volume_quarters) / num_quarters

    # Step 3: Compute Posterior Probability using Bayes' Theorem
    if P_high_volume > 0:
        P_price_increase_given_high_vol = (P_high_vol_given_price_increase * P_price_increase) / P_high_volume
        P_price_drop_given_high_vol = (P_high_vol_given_price_drop * P_price_drop) / P_high_volume
    else:
        P_price_increase_given_high_vol = 0
        P_price_drop_given_high_vol = 0

except KeyError as e:
    print(f"Column not found: {e}")
    print("Please ensure your DataFrame contains 'Close', 'Open', and 'Volume' columns")
# Display Results
print(f"P(Price Increase): {P_price_increase:.2f}")
print(f"P(Price Drop): {P_price_drop:.2f}")
print(f"P(High Volume | Price Increase): {P_high_vol_given_price_increase:.2f}")
print(f"P(High Volume | Price Drop): {P_high_vol_given_price_drop:.2f}")
print(f"P(Price Increase | High Volume): {P_price_increase_given_high_vol:.2f}")
print(f"Probability of Price Increase given High Volume: {P_price_drop_given_high_vol:.2f}")

