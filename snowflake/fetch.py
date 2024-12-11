from utils.sessions import SnowflakeConnector
from snowflake.core import Root 
from dotenv import load_dotenv
load_dotenv()



connector = SnowflakeConnector()
session = connector.get_session()
root = Root(session)




my_service = (root
  .databases["CORTEX_CONNECT"]
  .schemas["CORTEX_SEARCH_S"]
  .cortex_search_services["mysearch"]

)

# query service
resp = my_service.search(
  query="Types of rocks in India",
  columns=["CHUNKS"],
  limit=5
)
print(resp.to_json())