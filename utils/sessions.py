from snowflake.snowpark import Session
from snowflake.core import Root 
import os
from dotenv import load_dotenv

load_dotenv()


class SnowflakeConnector:
    def __init__(self):
        
        # set the variables in an .env file 
        required_env_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_ROLE"
            ]

        
        for var in required_env_vars:
            if var not in os.environ:
                raise ValueError(f"missing required varibale {var}")

        self.connection_parameters = {
            "account": os.environ["SNOWFLAKE_ACCOUNT"],
            "user" : os.environ["SNOWFLAKE_USER"],
            "password" : os.environ["SNOWFLAKE_PASSWORD"] ,
            "role" : os.environ["SNOWFLAKE_ROLE"],
            "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
            "schema" : os.environ["SNOWFLAKE_SCHEMA"]
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




