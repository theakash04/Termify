from snowflake.snowpark import Session
import os
from dotenv import load_dotenv

"""
SnowflakeConnector

This module provides a class `SnowflakeConnector` for managing connections to a Snowflake database. It handles the following:

1. Loading connection parameters from an `.env` file to ensure secure credential management.
2. Establishing a session with Snowflake using the Snowpark `Session` class.
3. Automatically reconnecting if a session is not already active.
4. Safely closing the session to release resources.

Usage:
- Ensure the required environment variables (`SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ROLE`) are set in a `.env` file.
- Use `get_session()` to retrieve the active session or establish a new connection.
- Use `close_connection()` to safely close the active session.
"""

load_dotenv()

class SnowflakeConnector:
    def __init__(self):
        
        # Set the variables in an .env file 
        required_env_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_ROLE"
            ]

        
        for var in required_env_vars:
            if var not in os.environ:
                raise ValueError(f"missing required variable {var}")

        self.connection_parameters = {
            "account": os.environ["SNOWFLAKE_ACCOUNT"],
            "user" : os.environ["SNOWFLAKE_USER"],
            "password" : os.environ["SNOWFLAKE_PASSWORD"] ,
            "role" : os.environ["SNOWFLAKE_ROLE"],
            
        }
        self.session = None

    def __connect(self):
            try:
                self.session = Session.builder.configs(self.connection_parameters).create()
                print("Connected Successfully")
            except Exception as e:
                print(f"Error occurred during connection: {e}")
                self.session = None

    def get_session(self):
            if not self.session:
                self.__connect()
            return self.session 
        
    def close_connection(self):
            if self.session:
                try:
                    self.session.close()
                    print("Session closed successfully")
                except Exception as e:
                    print(f"Error occurred while closing the session: {e}")
            else:
                print("No active sessions to close")


__all__ = ["SnowflakeConnector"]
