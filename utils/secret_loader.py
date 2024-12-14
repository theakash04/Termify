import os
import streamlit as st
from dotenv import load_dotenv

def get_secret(key: str):
    """Fetch secret from environment variables or fallback to Streamlit secrets."""
    secret_value = os.environ[key]
    if secret_value:
        return secret_value

    # if not found in env
    try:
        if key in st.secrets:
            return st.secrets[key]
    except FileNotFoundError:
        pass

    return None

  

__all__ = ["get_secret"]
