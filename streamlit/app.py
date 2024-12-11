# os and sys import is done for solving the issue of not finding the utils custom packages
import sys
import os
sys.path.append(os.path.abspath(".."))

import streamlit as st
from snowflake.core import Root
from utils.sessions import SnowflakeConnector


if "sfConnect" not in st.session_state:
    st.session_state.sfConnect = SnowflakeConnector()
    session = st.session_state.sfConnect.get_session()
    st.session_state.root = Root(session)


root = st.session_state.root
if "my_service" not in st.session_state:
    st.session_state.my_service = (root
      .databases["CORTEX_CONNECT"]
      .schemas["CORTEX_SEARCH_S"]
      .cortex_search_services["mysearch"]
    )


async def searchQuery(question: str):
    response = await st.session_state.my_service.search(
      query= question,
      columns=["CHUNKS"],
      limit=5
    )
    return response


# intialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React on user Input
if question := st.chat_input("what is up?"):
    #user question display
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    #AI response display
    # response = searchQuery(question)
    response = f"echo {question}"
    with st.chat_message("assistant"):
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

def clearChat():
    st.session_state.messages = []

with st.sidebar:
    clearBtn = st.button("clear chat", on_click=clearChat)
