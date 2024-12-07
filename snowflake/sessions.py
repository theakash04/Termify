import os
from dotenv import load_dotenv
from snowflake.snowpark import Session

class SnowflakeConnector:
    def __init__(self):
        
        load_dotenv()
        required_env_vars = [
            "SNOWFLAKE_ACCOUNT",
            "SNOWFLAKE_USER",
            "SNOWFLAKE_PASSWORD",
            "SNOWFLAKE_ROLE",
            "SNOWFLAKE_DATABASE",
            "SNOWFLAKE_WAREHOUSE",
            "SNOWFLAKE_SCHEMA",
        ]
        
        for var in required_env_vars:
            if var not in os.environ:
                raise ValueError(f"Missing required environment variable: {var}")
                
        
        self.connection_parameters = {
            "account": os.environ["SNOWFLAKE_ACCOUNT"],
            "user": os.environ["SNOWFLAKE_USER"],
            "password": os.environ["SNOWFLAKE_PASSWORD"],
            "role": os.environ["SNOWFLAKE_ROLE"],
            "database": os.environ["SNOWFLAKE_DATABASE"],
            "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
            "schema": os.environ["SNOWFLAKE_SCHEMA"],
        }
        self.session = None
        
    def __connect(self):
        try:
            self.session = Session.builder.configs(self.connection_parameters).create()
            print("Connected successfully")
        except Exception as e:
            print(f"Error occurred during connection: {e}")
            self.session = None
            
    def get_session(self):
        if not self.session:
            self.__connect() # Establish a new session if none exists
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

