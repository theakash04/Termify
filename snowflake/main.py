from dotenv import load_dotenv
from sessions import SnowflakeConnector

load_dotenv()

snowflake_connector = SnowflakeConnector()
snowflake_connector.get_session()
snowflake_connector.close_connection()
