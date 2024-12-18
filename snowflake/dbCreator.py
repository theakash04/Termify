import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.sessions import SnowflakeConnector
from utils.docParser import DocumentParser
from snowflake.core import Root, CreateMode
from snowflake.core.database import Database
from snowflake.core.schema import Schema
from dotenv import load_dotenv
from utils.secret_loader import get_secret

load_dotenv()

"""
CortexSearchModule

This module provides functionality for loading PDF content, chunking the text into smaller parts, and storing the results in a Snowflake database. It includes methods to:

1. Load content from a PDF file.
2. Create a Snowflake database and schema if they do not already exist.
3. Split the loaded text into smaller chunks and generate prompts for further processing.

The main class `CortexSearchModule` encapsulates all the operations needed for processing and storing the PDF content.

Usage:
1. **Initialize**: 
   - Create an instance of `SnowflakeConnector` and provide the necessary Snowflake connection details (like account, user, password, role) via environment variables.
   - Provide the path to the PDF file to be processed.

   ```python
   connector = SnowflakeConnector()  # Initialize SnowflakeConnector
   pdf_path = "/path/to/your/document.pdf"  # Path to the PDF file
   cortex_search = CortexSearchModule(connector, pdf_path)
"""

CORTEX_SERVICE_NAME = get_secret("SNOWFLAKE_CORTEX_SEARCH_SERVICE")
WAREHOUSE = get_secret("SNOWFLAKE_WAREHOUSE")
DATABASE = get_secret("SNOWFLAKE_DATABASE")
SCHEMA = get_secret("SNOWFLAKE_SCHEMA")
CORTEX_SEARCH_TABLE_NAME = "LAW_TABLE"

class CortexSearchModule:
    def __init__(self, connector: SnowflakeConnector, pdf_path: str):
        self.connector = connector
        self.pdf_path = pdf_path
        self.session = self.connector.get_session()

    def create_database_and_schema(self):
        """Creates or replaces the Snowflake database and schema."""
        root = Root(self.session)
        try:
            database = root.databases.create(
                Database(name=DATABASE), mode=CreateMode.or_replace
            )
            print("Created databases Successfully")

            database.schemas.create(
                Schema(name=SCHEMA),
                mode=CreateMode.or_replace,
            )
            print("Created schemas Successfully")
        except Exception as err:
            print("Some Error occured while creating database and schema", err)

    async def chunk_text(self):
        """Parses the PDF and creates text chunks."""
        try:
            document_parser = DocumentParser(
                path=self.pdf_path, chunk_size=512, chunk_overlap=256
            )
            chunks_df = await document_parser.chunkCreator()

            return chunks_df
        except Exception as err:
            print("Error occurred while parsing document and creating chunks", {err})

    def store_results_in_snowflake(self, results_df):
         """Stores the results in a Snowflake table."""
        # Create DataFrame in Snowflake
        resultsdf = self.session.create_dataframe(results_df)
        resultsdf.write.save_as_table(CORTEX_SEARCH_TABLE_NAME, mode="append")

    def create_cortex_search_service(self):
        """Creates or replaces the Cortex Search Service in Snowflake."""

        #NOTE: we can add attributes for filtering of data using a column in table but RN we only have one column in table
        try:
            self.session.sql(f"USE DATABASE {DATABASE}").collect()
            self.session.sql(f"USE SCHEMA {SCHEMA}").collect()
            cmd =f"""
            CREATE OR REPLACE CORTEX SEARCH SERVICE {CORTEX_SERVICE_NAME}
              ON CHUNKS
              WAREHOUSE = {WAREHOUSE}
              TARGET_LAG = '1 hour'
              EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
            AS (
              SELECT
                  CHUNKS
              FROM {CORTEX_SEARCH_TABLE_NAME}
            );
            """
            self.session.sql(cmd).collect()
            print(f"Cortex Search service '{CORTEX_SERVICE_NAME}' created successfully in database '{DATABASE}' and schema '{SCHEMA}'.")
        except Exception as err:
            print(f"Something happen while creating cortex search service {CORTEX_SERVICE_NAME} in database {DATABASE} and schema {SCHEMA} \n")
            print(err)

    async def run(self):
        """Executes the full workflow: database/schema setup, chunking, storing results, and creating the search service."""
        self.create_database_and_schema()
        results_df = await self.chunk_text()
        self.store_results_in_snowflake(results_df)
        # creating cortex search service after creating a new databse
        print("Initializing Cortex Search Service... This might take a few moments.")
        self.create_cortex_search_service()


__all__ = ["CortexSearchModule"]
