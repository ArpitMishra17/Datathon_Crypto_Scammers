from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from huggingface_hub import InferenceClient
import os

app = FastAPI()

# Initialize the Hugging Face Inference Client
HUGGING_FACE_API_TOKEN = os.getenv("HF_API_KEY")
client = InferenceClient(api_key=HUGGING_FACE_API_TOKEN)

# Define a Pydantic model for the request body
class ChatRequest(BaseModel):
    initial_data: str  # The large context (350-500 words)
    user_message: str  # The user's query

def get_hf_response(initial_data, user_message):
    # Combine the initial data and user message into a single prompt
    prompt = f"Context: {initial_data}\n\nUser: {user_message}\n\nAssistant:"
    
    try:
        # Send the prompt to the Hugging Face model
        response = client.text_generation(
            prompt=prompt,
            model="google/gemma-2-9b-it",
            max_new_tokens=200,  # Limit the output length
            temperature=0.7,     # Controls randomness
            top_k=50,            # Limits the number of tokens considered for sampling
            do_sample=True       # Enables sampling for more diverse responses
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        # Get the response from the Hugging Face model
        hf_response = get_hf_response(request.initial_data, request.user_message)
        
        return {"response": hf_response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)