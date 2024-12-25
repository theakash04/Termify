# os and sys import is done for solving the issue of not finding the utils custom packages
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'snowflake')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

import streamlit as st
from snowflake.core._root import Root
from utils.sessions import SnowflakeConnector
from snowflake.main import RAG

# session state for better user experience
if "session" not in st.session_state:
    sfConnect = SnowflakeConnector()
    st.session_state.session = sfConnect.get_session()

if "root" not in st.session_state:
    st.session_state.root = Root(st.session_state.session)

if "sfChatApp" not in st.session_state:
    st.session_state.sfChatApp = RAG(st.session_state.root, st.session_state.session)

if "messages" not in st.session_state:
    st.session_state.messages = []

def clearChat():
    st.session_state.messages = []
    st.session_state.first_load = True

if "first_load" not in st.session_state:
    st.session_state.first_load = True

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# welcome message
if st.session_state.first_load:
    st.title("Welcome to :blue[LegalBot] ⚖️")
    st.info("Get quick answers to general legal questions.")
    st.markdown('**Example:** "What are the rights of a women?"')
    st.divider()
    st.session_state.first_load = False

# Handle user input
if question := st.chat_input("what do you want to know?"):
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # Generate response
    response = st.session_state.sfChatApp.query(question)

    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})


# sidebar
with st.sidebar:
    clearBtn = st.button("clear chat", on_click=clearChat)
