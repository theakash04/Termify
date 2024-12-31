import sys
import os
import asyncio
from dotenv import load_dotenv
# Add the parent dir to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.sessions import SnowflakeConnector
from dbCreator import CortexSearchModule
from utils.secret_loader import get_secret

# Load environment variables
load_dotenv()


if __name__ == "__main__":
    _connector = SnowflakeConnector()
    try:
        _cortex_search = CortexSearchModule(_connector)
        asyncio.run(_cortex_search.run())
    except Exception as err:
        print(f"Some error occurred: {err}")


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
        resp = my_service.search(query=query, columns=["DATA"], limit=self._limit_to_retirve)

        if resp.results:
            return [curr["DATA"] for curr in resp.results]
        else:
            return []

    def create_prompt(self, query:str, context_str: list)-> str:
        prompt = f"""
            You are an expert legal advisor. Answer questions briefly and accurately based on the provided context.
            If you don´t have the information just say so.
            Avoid referring to the document as copyrighted or mentioning how you process it.
            Respond politely to casual greetings if they are included in the input.
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
