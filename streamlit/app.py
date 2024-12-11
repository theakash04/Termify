import streamlit as st
from utils.sessions import SnowflakeConnector
from snowflake.core import Root

sfConnect = SnowflakeConnector()

session = sfConnect.get_session()
root = Root(session)

