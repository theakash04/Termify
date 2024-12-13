# os and sys import is done for solving the issue of not finding the utils custom packages
import sys
import os

# Add the parent, snowflake, and utils directories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'snowflake')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

import streamlit as st
from snowflake.core import Root
from utils.sessions import SnowflakeConnector
from snowflake.main import RAG
import asyncio


if "sfConnect" not in st.session_state:
    st.session_state.sfConnect = SnowflakeConnector()
    session = st.session_state.sfConnect.get_session()
    st.session_state.root = Root(session)


root = st.session_state.root


# intialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React on user Input
if question := st.chat_input("what is up?"):
    # user question display
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # AI response display
    response = asyncio.run(RAG(question, root))
    # response = f"echo {question}"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


def clearChat():
    st.session_state.messages = []


with st.sidebar:
    clearBtn = st.button("clear chat", on_click=clearChat)
