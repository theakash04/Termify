import os
from dotenv import load_dotenv
from snowflake.snowpark import Session

load_dotenv()

connection_parameters = {
    "account": os.environ["SNOWFLAKE_ACCOUNT"],
    "user": os.environ["SNOWFLAKE_USER"],
    "password": os.environ["SNOWFLAKE_PASSWORD"],
    "role": os.environ["SNOWFLAKE_ROLE"],
    "database": os.environ["SNOWFLAKE_DATABASE"],
    "warehouse": os.environ["SNOWFLAKE_WAREHOUSE"],
    "schema": os.environ["SNOWFLAKE_SCHEMA"],
}

class snowflakeConnector:
    def __init__(self):
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
                raise ValueError(f"Missing required enviroment variable: {var}")

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
        except Exception as err:
            print(f"Error during getting connection: {err}")
            self.session = None

    def get_session(self):
        if not self.session:
            self.__connect()
        return self.session

    def close_session(self):
        if self.session:
            try:
                self.session.close()
                print("Session closed successfully")
            except Exception as err:
                print(f"Error occurred while closing the session: {err}")
        else:
            print("No active session")


__all__ = ["snowflakeConnector"]




