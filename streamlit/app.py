# os and sys import is done for solving the issue of not finding the utils custom packages
from dataclasses import dataclass
import sys
import os
import time
import asyncio
from typing import Literal
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'snowflake')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils')))

import streamlit as st
from snowflake.core._root import Root
from utils.sessions import SnowflakeConnector
from snowflake.main import RAG
from utils.docParser import DocumentParser

# page configuration
st.set_page_config(
    page_title="Termify",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get Help": "https://akashtwt.tech",
        "Report a bug": "https://github.com/theakash04/snowflake-LLM",
        "About": "This is Termify that helps in understanding legal terms and concepts.",
    },
)


def initialize_session_state():
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

    if "first_load" not in st.session_state:
        st.session_state.first_load = True

    if "data_frame" not in st.session_state:
        st.session_state.data_frame = None

    if "parse_status" not in st.session_state:
        st.session_state.parse_status = None


initialize_session_state()

@dataclass
class message:
    origin: Literal["user", "ai"]
    message: str

def clearChat():
    st.session_state.messages = []
    st.session_state.first_load = True
    st.session_state.data_frame = None
    st.session_state.parse_status = None

# new feature function
def file_uploade_feature():
    uploaded_file = st.file_uploader("Upload your File", type="pdf", help="Do not upload any confidential informations")

    # temporarely store document into local_disk for better convinience while parsing
    if uploaded_file is not None:
        temp_file_path = f"temp_{uploaded_file.name}"
        with st.spinner('uploading temporary file...'):
            with open(temp_file_path, "wb") as temp_file:
                temp_file.write(uploaded_file.read())

            # parse user documents into snowflake db
            if st.button("parse Document"):
                with st.status("Parsing data...", expanded=True) as status:
                    st.write("Cleaning the data...")
                    doc_parser = DocumentParser(path=temp_file_path)
                    data_frame =  asyncio.run(doc_parser.chunkCreator())
                    st.write("storing it in dataframes")

                    # Update session state
                    st.session_state.data_frame = data_frame
                    st.session_state.parse_status = "successfully parsed data!"
                    status.update(label=st.session_state.parse_status, state="complete", expanded=False)

            if st.session_state.data_frame is not None:
                st.write(st.session_state.parse_status)
                st.dataframe(st.session_state.data_frame)

icons = {"assistant": "❄️", "user": "👤"}

# welcome message
if st.session_state.first_load:
    st.title("Welcome to :blue[Termify] 📝")
    st.info("This is Termify that helps you in understanding legal terms and concepts.")
    st.divider()
    st.session_state.first_load = False

# animated response stream
def stream_output(response):
    for word in response.split(" "):
        yield word + " "
        time.sleep(0.06)

# showing all messages
for chat in st.session_state.messages:
    if chat.origin == "user":
        with st.chat_message("user",avatar=icons["user"]):
            st.markdown(chat.message)
    else:
        with st.chat_message("assistant", avatar=icons["assistant"]):
            st.markdown(chat.message)

# chatbox and current message response
if query := st.chat_input("Hello Termify!"):
    with st.chat_message("user", avatar=icons["user"]):
        st.markdown(query)
        st.session_state.messages.append(message("user", query))

    with st.spinner("Let me figure that out for you..."):
        response = st.session_state.sfChatApp.query(query)

    with st.chat_message("assistant", avatar=icons["assistant"]):
        st.write_stream(stream_output(response))
    st.session_state.messages.append(message("ai", response))


# sidebar
with st.sidebar:
    clearBtn = st.button("clear chat", on_click=clearChat)
    # file_uploade_feature()
