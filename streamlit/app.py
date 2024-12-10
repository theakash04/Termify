import streamlit as st
from libs.session import snowflakeConnector
from snowflake.core import Root

sfConnect = snowflakeConnector()

session = sfConnect.get_session()
root = Root(session)



session = sfConnect.get_session()
root = Root(session)

