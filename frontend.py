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