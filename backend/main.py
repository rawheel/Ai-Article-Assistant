from fastapi import FastAPI
from pydantic import BaseModel
from openai import OpenAI
import os
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load .env from the root directory
env_path = Path('..') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = FastAPI()

class ArticleRequest(BaseModel):
    title: str

@app.post("/generate-article")
async def generate_article(request: ArticleRequest):
    prompt = f"Write a technical brief article about {request.title}. Include a real-world scenario example. This article will be published to dev.to so make sure it is formatted correctly."
    
    response = client.chat.completions.create(
        temperature=0.2,
        max_tokens=500,
        model="gpt-4o-2024-08-06",
        messages=[{"role": "user", "content": prompt}]
    )
    
    article = response.choices[0].message.content
    
    return {"article": article}


class PublishRequest(BaseModel):
    title: str
    content: str
    published: bool = False

@app.post("/publish-to-devto")
async def publish_to_devto(request: PublishRequest):
    print("came here")
    print(request)
    devto_url = "https://dev.to/api/articles"
    headers = {
        "api-key": os.getenv("DEVTO_API_KEY"),
        "Content-Type": "application/json"
    }
    
    payload = {
        "article": {
            "title": request.title,
            "body_markdown": request.content,
            "published": request.published
        }
    }
    
    response = requests.post(devto_url, json=payload, headers=headers)
    
    if response.status_code == 201:
        return {"status": "success", "url": response.json()["url"]}
    else:
        return {"status": "error", "message": response.text}