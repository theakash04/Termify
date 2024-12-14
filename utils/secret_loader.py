import os
import streamlit as st

def get_secret(key: str):
    """Fetch secret from Streamlit secrets or fallback to environment variables."""
    secrets_file_path = os.path.join(os.getcwd(), ".streamlit", "secrets.toml")
    if not os.path.exists(secrets_file_path):
        return os.environ[key]
    # Use st.secrets only if the file exists and the key is present
    try:
        if key in st.secrets:
            return st.secrets[key]
    except FileNotFoundError:
        pass  # Silently skip st.secrets if secrets.toml doesn't exist


__all__ = ["get_secret"]
