from pinecone import Pinecone, ServerlessSpec
from sentence_transformers import SentenceTransformer
import dotenv
import os
import pandas as pd
import numpy as np
import faiss
import logging
from pathlib import Path
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
dotenv.load_dotenv()
PINECONE_API = os.getenv("PINECONE_API")
PC_ENV = os.getenv("PINECONE_ENV")
PATH = "./Data/stock_data.csv"
# Initialize
pc = Pinecone(api_key=PINECONE_API)
index_name = "stock-index"

pIndex = pc.Index(index_name)
encoder = SentenceTransformer('all-MiniLM-L6-v2')

def getCSV(Path: str) -> pd.DataFrame:
    df = pd.read_csv(Path)
    return df

def generate_embeddings(row):
    # Concatenate relevant columns into a single string for embedding
    text_representation = f"{row['Symbol']} {row['Open']} {row['High']} {row['Low']} {row['Close']} {row['Volume']}"
    return encoder.encode(text_representation)

data = getCSV(PATH)
data["embedding"] = data.apply(generate_embeddings, axis=1)
embeddings = data["embedding"]
embeddings.to_csv("embeddings.csv", index=False)
# embeddings = pd.read_csv("embe 1ddings.csv")
# embeddings = embeddings["embedding"]

print("Data loaded and embeddings generated")

def store_in_pinecone(
    data: pd.DataFrame,
    index: Pinecone.Index,
    batch_size: int = 100,
    namespace: str = None
) -> None:
    """
    Store stock data vectors in Pinecone index with batch processing.
    
    Args:
        data: DataFrame containing stock data with embeddings
        index: Pinecone index instance
        batch_size: Number of vectors to add in each batch
        namespace: Optional namespace for the vectors
    """
    try:
        batch_items = []
        total_batches = len(data) // batch_size + (1 if len(data) % batch_size else 0)
        
        for idx, row in tqdm(data.iterrows(), total=len(data), desc="Processing vectors"):
            vector = row["embedding"].astype(np.float32).tolist()
            metadata = {
                "date": str(row["Date"]),  # Pinecone requires string metadata
                "symbol": row["Symbol"],
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "dividends": float(row["Dividends"]),
                "stock_splits": float(row["Stock Splits"])
            }
            
            # Create unique ID for each vector
            vector_id = f"{row['Symbol']}_{row['Date']}_{idx}"
            
            batch_items.append((vector_id, vector, metadata))
            
            if len(batch_items) >= batch_size:
                # Prepare batch in Pinecone format
                upsert_batch = [(id, vec, meta) for id, vec, meta in batch_items]
                
                # Upsert batch to Pinecone
                index.upsert(vectors=upsert_batch, namespace=namespace)
                logger.info(f"Added batch of {len(batch_items)} vectors to Pinecone")
                batch_items = []
        
        # Process remaining vectors
        if batch_items:
            upsert_batch = [(id, vec, meta) for id, vec, meta in batch_items]
            index.upsert(vectors=upsert_batch, namespace=namespace)
            logger.info(f"Added final batch of {len(batch_items)} vectors to Pinecone")
        
        logger.info("Successfully completed storing vectors in Pinecone")
        
    except Exception as e:
        logger.error(f"Error storing vectors in Pinecone: {str(e)}")
        raise


store_in_pinecone(data, pIndex, batch_size=100, namespace="stocks")
print("Pinecone stored!")

def search_vectors_pinecone(
    index: Pinecone.Index,
    query_vector: np.ndarray,
    k: int = 5,
    namespace: str = None,
    filter: dict = None
) -> list[dict]:
    """
    Search for similar vectors in Pinecone index.
    
    Args:
        index: Pinecone index instance
        query_vector: Vector to search for
        k: Number of results to return
        namespace: Optional namespace to search in
        filter: Optional metadata filters
        
    Returns:
        List of dictionaries containing search results and metadata
    """
    try:
        # Convert query vector to list for Pinecone
        query = query_vector.astype(np.float32).tolist()
        
        # Perform similarity search
        results = index.query(
            vector=query,
            top_k=k,
            namespace=namespace,
            filter=filter,
            include_metadata=True
        )
        
        logger.info(f"Found {len(results.matches)} similar vectors")
        return results.matches
        
    except Exception as e:
        logger.error(f"Error during vector search: {str(e)}")
        raise

# Example usage:
query_embedding = encoder.encode("search text")
results = search_vectors_pinecone(
    pIndex, 
    query_embedding, 
    k=5, 
    filter={"symbol": "AAPL"}
)

print(results)

def setup_faiss_index(vector_dimension: int, index_path: str = "stock_index.faiss") -> faiss.IndexFlatL2:
    """Initialize or load existing FAISS index"""
    if Path(index_path).exists():
        logger.info("Loading existing FAISS index")
        return faiss.read_index(index_path)
    
    logger.info("Creating new FAISS index")
    return faiss.IndexFlatL2(vector_dimension)

def store_in_faiss(
    data: pd.DataFrame,
    index: faiss.IndexFlatL2,
    batch_size: int = 100,
    index_path: str = "stock_index.faiss"
) -> None:
    """
    Store stock data vectors in FAISS index with batch processing.
    
    Args:
        data: DataFrame containing stock data with embeddings
        index: FAISS index instance
        batch_size: Number of vectors to add in each batch
        index_path: Path to save the FAISS index
    """
    try:
        batch_vectors = []
        metadata_list = []
        
        for _, row in data.iterrows():
            vector = row["embedding"].astype(np.float16)
            metadata = {
                "date": row["Date"],
                "symbol": row["Symbol"],
                "open": float(row["Open"]),
                "high": float(row["High"]),
                "low": float(row["Low"]),
                "close": float(row["Close"]),
                "volume": int(row["Volume"]),
                "dividends": float(row["Dividends"]),
                "stock_splits": float(row["Stock Splits"])
            }
            
            batch_vectors.append(vector)
            metadata_list.append(metadata)
            
            if len(batch_vectors) >= batch_size:
                vectors_array = np.array(batch_vectors)
                index.add(vectors_array)
                logger.info(f"Added batch of {len(batch_vectors)} vectors to FAISS")
                batch_vectors = []
        
        # Process remaining vectors
        if batch_vectors:
            vectors_array = np.array(batch_vectors)
            index.add(vectors_array)
            logger.info(f"Added final batch of {len(batch_vectors)} vectors to FAISS")
        
        # Save index
        faiss.write_index(index, index_path)
        logger.info(f"FAISS index saved to {index_path}")
        
    except Exception as e:
        logger.error(f"Error storing vectors in FAISS: {str(e)}")
        raise

# vector_dim = len(data['embedding'].iloc[0])
# index = setup_faiss_index(vector_dimension=vector_dim)

# store_in_faiss(
#     data=data,
#     index=index,
#     batch_size=100,
#     index_path="stock_index.faiss"
# )

# def search_similar(query_vector, k=5):
#     distances, indices = index.search(
#         np.array([query_vector]).astype(np.float32), 
#         k
#     )
#     return data.iloc[indices[0]]
print("storing done")
# Example search using first vector as query
# sample_query = data['embedding'].iloc[0]
# results = search_similar(sample_query)
# print("\nSearch Results:")
# print(results[['Symbol', 'Date', 'Close']])

print("Done!")