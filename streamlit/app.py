# os and sys import is done for solving the issue of not finding the utils custom packages
from dataclasses import dataclass
import sys
import os
import uuid
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
from utils.Custom_cortex import customCortex
# page configuration
st.set_page_config(
    page_title="Termify",
    page_icon="📝",
    layout="centered",
    initial_sidebar_state="auto",
    menu_items={
        "Get Help": "https://github.com/theakash04/snowflake-LLM",
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

    if "parse_status" not in st.session_state:
        st.session_state.parse_status = None

    if "custom_cortex_details" not in st.session_state:
        st.session_state.custom_cortex_details = {
            "schema": f"db_{uuid.uuid4().hex}_{int(time.time())}",
            "cortexServiceName":f"css_{uuid.uuid4().hex}_{int(time.time())}",
            "using_custom_cortex": False
        }

    if "user_cortex" not in st.session_state:
        st.session_state.user_cortex = customCortex(
            session=st.session_state.session, root=st.session_state.root, schema=st.session_state.custom_cortex_details["schema"],service_name=st.session_state.custom_cortex_details["cortexServiceName"]
        )

    if 'initialized' not in st.session_state:
        st.session_state.initialized = True



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

def on_session_end():
    st.session_state.user_cortex.delete_schema()

if not st.session_state.initialized:
    on_session_end()


@st.dialog("Use your Own file")
def file_uploade_feature():
    st.warning("Do not close this dialog or click other buttons once the operation starts, as it may interrupt the process and corrupt your data.")
    uploaded_file = st.file_uploader("Upload your File", type="pdf", help="Do not upload any confidential informations")

    # temporarely store document into local_disk for better convinience while parsing
    if uploaded_file is not None:
        temp_file_path = f"temp_{uploaded_file.name}"
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(uploaded_file.read())

        # parse user documents into snowflake db
        if st.button("parse Document"):
            with st.status("Uploading... This might take a few minutes. ⏳", expanded=True) as status:
                asyncio.run(
                    st.session_state.user_cortex.Create_service(temp_file_path)
                )
                st.session_state.custom_cortex_details["using_custom_cortex"] = True
                os.remove(temp_file_path)

                # Update session state
                st.session_state.parse_status = "successfully parsed data!"
                status.update(label=st.session_state.parse_status, state="complete", expanded=False)

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
        user_data = st.session_state.custom_cortex_details["using_custom_cortex"]
        if user_data:
            schema = st.session_state.custom_cortex_details["schema"]
            cortex_service_name = st.session_state.custom_cortex_details["cortexServiceName"]
            response = st.session_state.sfChatApp.query(query,user_data,schema, cortex_service_name)
        else:
            response = st.session_state.sfChatApp.query(query, user_data)

    with st.chat_message("assistant", avatar=icons["assistant"]):
        st.write_stream(stream_output(response))
    st.session_state.messages.append(message("ai", response))


# sidebar
with st.sidebar:
    if "own_doc" not in st.session_state:
        if st.button("Upload Your File"):
            file_uploade_feature()
