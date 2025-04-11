import os

import requests
import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel
# from openai import OpenAI

from dotenv import load_dotenv
from pathlib import Path

from vertexai.preview.generative_models import GenerationConfig
from auth import init_vertexai

# Load .env from the root directory
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize FastAPI app
app = FastAPI()

# Define request model for article generation
class ArticleRequest(BaseModel):
    title: str

@app.post("/generate-article")
async def generate_article(request: ArticleRequest):
    """
    Generate an article based on the provided title using Google's Vertex AI.
    
    Args:
        request: ArticleRequest containing the article title
        
    Returns:
        JSON response with the generated article
    """
    # Create prompt for the AI model
    prompt = f"Write a technical brief article about {request.title}. Include a real-world scenario example. This article will be published to dev.to so make sure it is formatted correctly. just have only article content in the response no title or anything else add code snippet if needed"
    
    # Configure generation parameters
    generation_config = GenerationConfig(
        temperature=0.2,  # Lower temperature for more focused output
        top_p=0.8,        # Nucleus sampling parameter
        top_k=40,         # Top-k sampling parameter
        max_output_tokens=500,  # Maximum length of generated text
    )
    
    # Initialize the Vertex AI model
    model = await init_vertexai()

    # Generate content using the model
    response = model.generate_content(prompt, generation_config=generation_config)

    # Extract the text from the response
    article = response.text
    
    return {"article": article}


# Define request model for publishing to Dev.to
class PublishRequest(BaseModel):
    title: str
    content: str
    published: bool = False  # Default to draft mode

@app.post("/publish-to-devto")
async def publish_to_devto(request: PublishRequest):
    """
    Publish an article to Dev.to using their API.
    
    Args:
        request: PublishRequest containing the article title and content
        
    Returns:
        JSON response with status and URL or error message
    """
    print("Publishing to Dev.to")
    print(request)
    
    # Dev.to API endpoint
    devto_url = "https://dev.to/api/articles"
    
    # Set up headers with API key
    headers = {
        "api-key": os.getenv("DEVTO_API_KEY"),
        "Content-Type": "application/json"
    }
    
    # Prepare payload according to Dev.to API requirements
    payload = {
        "article": {
            "title": request.title,
            "body_markdown": request.content,
            "published": request.published  # False = draft, True = published
        }
    }
    
    # Send POST request to Dev.to API
    response = requests.post(devto_url, json=payload, headers=headers)
    
    # Handle response
    if response.status_code == 201:
        return {"status": "success", "url": response.json()["url"]}
    else:
        return {"status": "error", "message": response.text}
    

# Run the app if this file is executed directly
if __name__ == "__main__":
    uvicorn.run("backend:app", host="0.0.0.0", port=8008, reload=True)