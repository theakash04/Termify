from dotenv import load_dotenv
from sessions import SnowflakeConnector

load_dotenv()

snowflake_connector = SnowflakeConnector()
snowflake_connector.connect()
snowflake_connector.close_connection()
