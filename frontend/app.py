import streamlit as st
import requests
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = "http://backend:8000"

st.title("Article Generator")
title = st.text_input("Enter article title")

if st.button("Generate Article"):
    response = requests.post(
        f"{BACKEND_URL}/generate-article",
        json={"title": title}
    )
    if response.status_code == 200:
        article = response.json()["article"]
        st.session_state.generated_article = article
        st.session_state.article_title = title
        st.session_state.show_preview = False

if 'generated_article' in st.session_state:
    st.subheader("Article Preview")
    st.markdown(st.session_state.generated_article)
    
    if not st.session_state.get('show_preview', False):
        if st.button("Preview on Dev.to"):
            st.session_state.show_preview = True
            st.rerun()  # Updated from st.experimental_rerun()
    
    if st.session_state.get('show_preview', False):
        st.subheader("Dev.to Preview")
        st.markdown("### " + st.session_state.article_title)
        st.markdown(st.session_state.generated_article)
        
        if st.button("Approve and Publish to Dev.to"):
            publish_response = requests.post(
                f"{BACKEND_URL}/publish-to-devto",
                json={
                    "title": st.session_state.article_title,
                    "content": st.session_state.generated_article
                }
            )
            
            if publish_response.status_code == 200:
                st.success(f"Article published successfully! View it at: {publish_response.json()['url']}")
                del st.session_state.generated_article
                del st.session_state.article_title
                del st.session_state.show_preview
            else:
                st.error(f"Failed to publish article: {publish_response.json()['message']}")