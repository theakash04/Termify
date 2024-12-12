from snowflake.snowpark import Session
from snowflake_connector import SnowflakeConnector
from document_parser import DocumentParser
import pandas as pd

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


from snowflake.snowpark import Session
from snowflake_connector import SnowflakeConnector
from document_parser import DocumentParser
import pandas as pd

class CortexSearchModule:
    def __init__(self, connector: SnowflakeConnector, pdf_path: str):
        self.connector = connector
        self.pdf_path = pdf_path
        self.session = self.connector.get_session()

    def create_database_and_schema(self):
        root = self.session.create_root()
        database = root.database.create(
            name="CORTEX_CONNECT_DB",
            mode="or_replace"
        )
        print("Created database")
        
        schema = database.schema.create(
            name="CORTEX_SEARCH_SCHEMA",
            mode="or_replace"
        )
        print("Created schema")
       

    def chunk_text(self):
        document_parser = DocumentParser(
            path=self.pdf_path,
            chunk_size=1500,
            chunk_overlap=256
        )
        chunks_df = document_parser.chunkCreator()

        # Generate prompts for each chunk
        chunks_df["prompts"] = chunks_df["CHUNKS"].apply(
            lambda chunk: f"Given the document content: <chunk content: {chunk}>, identify the relevant category."
        )

        return chunks_df
    
    def store_results_in_snowflake(self, results_df):
        # Create DataFrame in Snowflake
        resultsdf = self.session.create_dataframe(results_df)
        resultsdf.write.save_as_table("CORTEX_SEARCH_TABLE", mode="append")
        
    def run(self):
        self.create_database_and_schema()
        results_df = self.chunk_text()
        self.store_results_in_snowflake(results_df)

__all__ = ["CortexSearchModule"]
