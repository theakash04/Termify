from snowflake.snowpark import Session
from snowflake.core import Root 
import os
from dotenv import load_dotenv


class SnowflakeConnector:
    def __init__(self):
        required_env_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD"
            ]

        
        for var in required_env_vars:
            if var not in os.environ:
                raise ValueError(f"missing required varibale {var}")

        self.connection_parameters = {
            "account": os.environ["SNOWFLAKE_ACCOUNT"],
            "user" : os.environ["SNOWFLAKE_USER"],
            "password" : os.environ["SNOWFLAKE_PASSWORD"] 
        }
        self.session = None

        def __connect(self):
            try:
                self.session = Session.builder.configs(self.connection_parameters).create()
                print("Connected Successfully")
            except Exception as e:
                print(f"Error occured during connection: {e}")
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




