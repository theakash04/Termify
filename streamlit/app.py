# os and sys import is done for solving the issue of not finding the utils custom packages
import sys
import os

# Add the parent, snowflake, and utils directories to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'snowflake')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

import streamlit as st
from snowflake.core._root import Root
from utils.sessions import SnowflakeConnector
from snowflake.main import RAG
import asyncio

# session state for better user experience
if "session" not in st.session_state:
    sfConnect = SnowflakeConnector()
    st.session_state.session = sfConnect.get_session()

session = st.session_state.session

if "root" not in st.session_state:
    st.session_state.root = Root(session)

root = st.session_state.root

# initializing snowflake chatapp with session
if "sfChatApp" not in st.session_state:
    st.session_state.sfChatApp = RAG(root, session)

# intialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# home page text shown only on first loads
if "first_load" not in st.session_state:
    st.session_state.first_load = True

if st.session_state.first_load:
    st.title("Welcome to :blue[LegalBot] ⚖️")
    st.info("Get quick answers to general legal questions.")
    st.markdown('**Example:** "What are the rights of a women?"')
    st.divider()
    st.session_state.first_load = False

# React on user Input
if question := st.chat_input("what do you want to know?"):
    # user question display
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # AI response display
    response = st.session_state.sfChatApp.query(question)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


def clearChat():
    st.session_state.messages = []


with st.sidebar:
    clearBtn = st.button("clear chat", on_click=clearChat)
