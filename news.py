import requests
from datetime import datetime, timedelta, date
from huggingface_hub import InferenceClient
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API keys
HF_API_TOKEN = os.getenv("HF_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# Initialize Hugging Face client
client = InferenceClient(api_key=HF_API_TOKEN)

# Query parameters
company_name = "Nvidia"
yesterday_date = (date.today() - timedelta(days=2)).isoformat()
current_date = date.today().isoformat()

# Fetch articles from NewsAPI
url = f"https://newsapi.org/v2/everything?q={company_name}&language=en&from={yesterday_date}&to={current_date}&sortBy=relevancy&pageSize=20&apiKey={NEWS_API_KEY}"
response = requests.get(url)
articles = response.json().get("articles", [])

# Filter articles by title
def filter_articles_by_title(articles, company_name):
    filtered_articles = [
        article for article in articles
        if company_name.lower() in (article.get("title", "") or "").lower()
    ]
    return filtered_articles

filtered_articles = filter_articles_by_title(articles, company_name)

# Preprocess articles
def preprocess_articles(articles):
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

processed_articles = preprocess_articles(filtered_articles)

# Evaluate relevance in batches
def evaluate_relevance_batch(batch):
    # Construct the prompt for batch processing
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

    # Use the Hugging Face Inference API to get the response
    try:
        response = client.text_generation(
            model="mistralai/Mistral-7B-Instruct-v0.3",  # Replace with your chosen model
            prompt=prompt,
            max_new_tokens=50,  # Adjust based on the number of articles
            temperature=0.1,    # Lower temperature for deterministic output
        )
        # Parse the response into a list of relevance scores
        scores = [float(score.strip()) for score in response.split(",")]
    except Exception as e:
        print(f"Error during evaluation: {e}")
        scores = [0.0] * len(batch)  # Default to 0 if parsing fails

    return scores

# Assign relevance scores in batches
batch_size = 5  # Number of articles per batch
for i in range(0, len(processed_articles), batch_size):
    batch = processed_articles[i:i + batch_size]
    scores = evaluate_relevance_batch(batch)
    for j, article in enumerate(batch):
        article["relevance_score"] = scores[j]

# Sort articles by relevance score in descending order
sorted_articles = sorted(processed_articles, key=lambda x: x.get("relevance_score", 0.0), reverse=True)

# Select the top 5 articles
top_articles = sorted_articles[:5]

# Print the top articles
for i, article in enumerate(top_articles, 1):
    print(f"{i}. Title: {article['title']}")
    print(f"   Description: {article['description']}")
    print(f"   URL: {article['url']}")
    print(f"   Relevance Score: {article.get('relevance_score', 0.0):.2f}\n")