from snowflake.core.schema import Schema
from snowflake.core._common import DeleteMode
import streamlit as st
from utils.doc_utils import DocumentProcessor
from utils.secret_loader import get_secret

class customCortex(DocumentProcessor):
    def __init__(self, session, root, schema, service_name,chunk_size=700, overlap=50):
        super().__init__(chunk_size=chunk_size, overlap=overlap)
        self.session = session
        self.table_name = "DATA"
        self.root = root
        self.schema = schema
        self.database = get_secret("USER_DATABASE")
        self.cortex_service_name = service_name
        self.WAREHOUSE = get_secret("SNOWFLAKE_WAREHOUSE")

    def _create_schema(self):
        try:
            st.write("Creating Your personal Schema")
            self.session.sql(f"USE DATABASE {self.database}").collect()
            self.session.sql(f"CREATE SCHEMA IF NOT EXISTS {self.schema}").collect()
            st.success("Schema created successfully")
            return True
        except Exception as err:
            st.warning(f"Some unExpected Error occured...{err}")
            return False


    async def _upload_data(self, pdf_path):
        st.write("Loading pdf...")
        raw_texts = await self.pdfLoader(pdf_path)
        st.write("Cleaning texts and DataFrame...")
        return self.chunkCreator(raw_texts)

    def _store_data(self, df):
        st.write("Creating dataframe...")
        resultsdf = self.session.create_dataframe(df)
        st.write("saving in snowflake table...")
        resultsdf.write.save_as_table(self.table_name, mode="append")

    def _createCortexService(self):
        try:
            self.session.sql(f"USE DATABASE {self.database}").collect()
            self.session.sql(f"USE SCHEMA {self.schema}").collect()
            cmd =f"""
            CREATE CORTEX SEARCH SERVICE {self.cortex_service_name}
              ON CHUNKS
              WAREHOUSE = {self.WAREHOUSE}
              TARGET_LAG = '1 days'
              EMBEDDING_MODEL = 'snowflake-arctic-embed-l-v2.0'
            AS (
              SELECT
                   CHUNKS
              FROM {self.table_name}
            );
            """
            self.session.sql(cmd).collect()

            st.success("Successfully create CortexSearchService")
        except:
            st.warning("Something went Wrong while Creating CortexSearchService")

    def delete_schema(self):
        try:
            schema_res = self.root.databases[self.database].schemas[self.schema]
            schema_res.drop()

        except:
            print("Some unExpected error occured during deletion of schema")

    async def Create_service(self, file_path):
        created_schema = self._create_schema()
        if created_schema:
            df = await self._upload_data(file_path)
            self._store_data(df)
            self._createCortexService()


__all__ = ["customCortex"]
