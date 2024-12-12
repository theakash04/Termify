from snowflake.snowpark import Session
from snowflake.core import Root, CreateMode
from snowflake.core.database import Database
from snowflake.core.schema import Schema
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd


class CortexSearchModule:
    def __init__(self, session: Session, pdf_path: str):
        self.session = session
        self.pdf_path = pdf_path
        self.pages_text = None

    def load_pdf_content(self):
        loader = PyPDFLoader(self.pdf_path)
        pages = []
        async for page in loader.alazy_load():
            pages.append(page.page_content)
        self.pages_text = "\n".join(pages)

    def create_database_and_schema(self):
        root = Root(self.session)
        database = root.databases.create(
            Database(
                name="CORTEX_CONNECT_DB"
            ),
            mode=CreateMode.or_replace
        )
        print("Created database.")

        schema = database.schemas.create(
            Schema(
                name="CORTEX_SEARCH_SCHEMA"
            ),
            mode=CreateMode.or_replace
        )
        print("Created schema.")

    def chunk_text(self):
        class TextChunker:
            def process(self, pdf_text: str):
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1512,
                    chunk_overlap=256,
                    length_function=len
                )
                chunks = text_splitter.split_text(pdf_text)
                prompts = [
                    f"Given the document content: <chunk content: {chunk}>, identify the relevant category."
                    for chunk in chunks
                ]
                df = pd.DataFrame({
                    'chunks': chunks,
                    'prompts': prompts
                })
                return df

        chunker = TextChunker()
        result = chunker.process(self.pages_text)
        return result

    def store_results_in_snowflake(self, result_df):
        result_df = self.session.create_dataframe(result_df)
        result_df.write.save_as_table("CORTEX_SEARCH_TABLE", mode="append")
        print("Data inserted into Snowflake CORTEX_SEARCH_TABLE with Cortex Search format.")

    def run(self):
        self.load_pdf_content()
        self.create_database_and_schema()
        result_df = self.chunk_text()
        self.store_results_in_snowflake(result_df)


__all__ = ["CortexSearchModule"]
