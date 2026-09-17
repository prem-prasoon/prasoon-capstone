"""Streamlit user interface connecting to the FastAPI streaming endpoint."""
import requests
import streamlit as st

API_URL = "http://localhost:8000/ask"

st.set_page_config(page_title="Capstone Q&A", page_icon="🤖")
st.title("Capstone Knowledge Assistant")
st.caption("Ask domain questions and stream real-time responses from FastAPI.")

user_query = st.text_input("Enter your question:", placeholder="What is RAG in one sentence?")

if st.button("Ask") and user_query:
    placeholder = st.empty()
    accumulated_text = ""

    try:
        with requests.post(API_URL, json={"question": user_query}, stream=True, timeout=60) as resp:
            if resp.status_code == 200:
                for chunk in resp.iter_content(decode_unicode=True):
                    if chunk:
                        accumulated_text += chunk
                        placeholder.markdown(accumulated_text + "▌")
                placeholder.markdown(accumulated_text)
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
    except requests.exceptions.ConnectionError:
        st.error("Cannot reach the API. Ensure FastAPI is running on http://localhost:8000.")