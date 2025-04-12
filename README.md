# Article Generator Workshop

A practical workshop to build an AI-powered article generator and publishing tool using Google's Vertex AI and Dev.to API.

## Project Overview

This workshop guides you through building a simple yet powerful application that:
1. Generates technical articles using Google's Vertex AI (Gemini model)
2. Allows previewing the generated content
3. Publishes articles directly to Dev.to

The application consists of a FastAPI backend for AI processing and API integration, with a Streamlit frontend for user interaction.

## Prerequisites

- Python 3.8+
- Google Cloud account with Vertex AI API enabled
- Dev.to account with API key
- Basic understanding of Python and REST APIs

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/article-generator-workshop.git
cd article-generator-workshop
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

Create a `requirements.txt` file with the following content:

```
fastapi
uvicorn
python-dotenv
google-cloud-aiplatform
requests
streamlit
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

### 4. Set Up Google Cloud Credentials

1. Create a new project in Google Cloud Console
2. Enable the Vertex AI API
3. Create a service account and download the JSON key file
4. Save the key file in your project directory as `weighty-triode-456314-m7-2b1e6b3b3533.json` (or update the code to use your filename)

### 5. Create Environment Variables

Create a `.env` file in the root directory with the following variables:

```
VERTEX_GEMINI_MODEL=gemini-1.5-pro
DEVTO_API_KEY=your_dev_to_api_key
BACKEND_URL=http://localhost:8008
```

Replace `your_dev_to_api_key` with your actual Dev.to API key.

## Building the Application

### Step 1: Authentication Module

Create `auth.py` to handle Google Cloud authentication and Vertex AI initialization:

```python
import os

import vertexai
from vertexai.preview.generative_models import GenerativeModel

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the current directory path
current_dir = os.path.dirname(os.path.abspath(__file__)) 

# Set the path to the Google Cloud credentials file
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.join(
    current_dir, 'weighty-triode-456314-m7-2b1e6b3b3533.json')

# Google Cloud project ID and location
project_id = 'weighty-triode-456314-m7'
location = 'us-central1'

async def init_vertexai():
    """
    Initialize the Vertex AI client and load the Gemini model.
    
    Returns:
        GenerativeModel: An instance of the Gemini 1.5 Pro model
    """
    # Initialize Vertex AI with project and location
    vertexai.init(project=project_id, location=location)
    
    # Load the Gemini 1.5 Pro model
    model = GenerativeModel(os.getenv("VERTEX_GEMINI_MODEL"))
    
    return model
```

> **Note:** Make sure to update the `project_id` and credentials filename to match your Google Cloud setup.

### Step 2: Backend API

Create `backend.py` to implement the FastAPI routes for article generation and publishing:

```python
import os

import requests
import uvicorn

from fastapi import FastAPI
from pydantic import BaseModel

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
```

### Step 3: Frontend Interface

The frontend is built with Streamlit for a simple and interactive user experience. It communicates with the backend API to generate and publish articles.

Create `frontend.py`:

```python
import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get backend URL from environment variable or use default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8008")

# Main app title
st.title("Article Generator")

# Input field for article title
title = st.text_input("Enter article title")

# Generate article button
if st.button("Generate Article"):
    # Send request to backend API
    response = requests.post(
        f"{BACKEND_URL}/generate-article",
        json={"title": title}
    )
    
    # If request is successful, store article in session state
    if response.status_code == 200:
        article = response.json()["article"]
        st.session_state.generated_article = article
        st.session_state.article_title = title

# Display article preview if an article has been generated
if 'generated_article' in st.session_state:
    st.subheader("Article Preview")
    st.markdown(st.session_state.generated_article)
    
    # Publish to Dev.to button
    if st.button("Publish to Dev.to"):
        # Send publish request to backend API
        publish_response = requests.post(
            f"{BACKEND_URL}/publish-to-devto",
            json={
                "title": st.session_state.article_title,
                "content": st.session_state.generated_article
            }
        )
        
        # Handle publish response
        if publish_response.status_code == 200:
            # Show success message with article URL
            st.success(f"Article published successfully! View it at: {publish_response.json()['url']}")
            # Clean up session state
            del st.session_state.generated_article
            del st.session_state.article_title
        else:
            # Show error message
            st.error(f"Failed to publish article: {publish_response.json()['message']}")
```

## Running the Application

### 1. Start the Backend Server

```bash
python backend.py
```

The API will be available at http://localhost:8008

### 2. Start the Frontend Application

In a new terminal:

```bash
streamlit run frontend.py
```

The Streamlit interface will open automatically in your browser.

## Workshop Flow

1. **Introduction** (15 minutes)
   - Overview of the application architecture
   - Introduction to Vertex AI and Dev.to API

2. **Environment Setup** (20 minutes)
   - Install dependencies
   - Set up Google Cloud credentials
   - Configure environment variables

3. **Building the Backend** (45 minutes)
   - Create the authentication module
   - Implement the FastAPI routes for article generation
   - Implement the Dev.to publishing endpoint

4. **Testing the Application** (20 minutes)
   - Generate sample articles
   - Publish to Dev.to (as drafts)

5. **Next Steps & Extensions** (10 minutes)
   - Adding user authentication
   - Enhancing the article generation with better prompts
   - Adding image generation capabilities

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Ensure your Google Cloud credentials file is properly configured
   - Check that your project has the Vertex AI API enabled

2. **Dev.to API Issues**
   - Verify your API key is correct
   - Ensure your Dev.to account has API access enabled

3. **Module Import Errors**
   - Check that all dependencies are installed
   - Verify the project structure matches the imports

## Resources

- [Google Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [Dev.to API Documentation](https://developers.forem.com/api)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
