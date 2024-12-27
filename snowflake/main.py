import sys
import os
import asyncio
from dotenv import load_dotenv

from langchain_community.document_loaders import pdf

# Add the parent dir to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.sessions import SnowflakeConnector
from dbCreator import CortexSearchModule
from utils.secret_loader import get_secret

# Load environment variables
load_dotenv()


if __name__ == "__main__":
    _connector = SnowflakeConnector()
    _create = input("Do You want to create new Database with a pdf Y/N:  ")

    # If the user chooses 'Y', ask for a PDF path, validate its existence, and parse it using CortexSearchModule.
    # If the file doesn't exist, notify the user. Handle any exceptions gracefully. Otherwise, abort the operation.
    if _create == 'Y' or _create == 'y':
        _pdf_path = input("Specify your path for the PDF (give absolute path):  ")
        try:
            if os.path.exists(_pdf_path) and os.path.isfile(_pdf_path):
                _cortex_search = CortexSearchModule(_connector, _pdf_path)
                asyncio.run(_cortex_search.run())
            else:
                print(f"The file '{_pdf_path}' does not exist.")
        except Exception as err:
            print(f"Some error occurred: {err}")
    else:
        print("Operation aborted as per your choice.")


class RAG:
    def __init__(self, root, session, limit_to_retirve=5):
        self.root = root
        self.session = session
        self._limit_to_retirve = limit_to_retirve


    def retrieve_context(self, query: str) -> dict:
        if not self.root or not self.session:
            return {
                "input": query,
                "response": "Something unexpected happened. Contact customer support.",
            }

        # Accessing the Snowflake Cortex search service
        my_service = (
            self.root.databases[get_secret("SNOWFLAKE_DATABASE")]
            .schemas[get_secret("SNOWFLAKE_SCHEMA")]
            .cortex_search_services[get_secret("SNOWFLAKE_CORTEX_SEARCH_SERVICE")]
        )

        # Searching and building context
        resp = my_service.search(query=query, columns=["CHUNKS"], limit=self._limit_to_retirve)

        if resp.results:
            return [curr["CHUNKS"] for curr in resp.results]
        else:
            return []

    def create_prompt(self, query:str, context_str: list)-> str:
        prompt = f"""
            You are an expert legal advisor. Answer questions briefly and accurately based on the provided context.
            If you don´t have the information just say so.
            Do not mention the process or context in your responses.
            You can also reply to casual greetings like "Hi," "Hello," or "How are you?" appropriately.
            Context: {context_str}
            Question: {query}
            Answer:
        """
        return prompt

    def generate_completion(self, query: str, context_str: list) -> str:
        prompt = self.create_prompt(query, context_str)
        cmd = """select snowflake.cortex.complete(?, ?) as response"""
        model = 'mistral-large2'
        result = self.session.sql(cmd, params=[model, prompt]).collect()
        return result[0]['RESPONSE']

    def query(self, query: str) -> str:
        context_str = self.retrieve_context(query)
        return self.generate_completion(query, context_str)


__all__ = ["RAG"]
