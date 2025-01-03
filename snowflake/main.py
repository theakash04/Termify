import sys
import os
import asyncio
import pandas as pd
# Add the parent dir to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.sessions import SnowflakeConnector
from dbCreator import CortexSearchModule
from utils.secret_loader import get_secret
from utils.datasets import FileProcessor
from snowflake.cortex import Summarize



if __name__ == "__main__":
    _connector = SnowflakeConnector()
    _cortex_search = CortexSearchModule(_connector)
    try:
        print("This Command will Process your data than store it in snowflake and create cortex search service\nMake sure you have added all necessary details in the .env file\nSee Readme.md for reference")
        ask = input("Do you want to proceed(y or n): ").lower()
        if ask in ['y', 'yes',]:
            folder_path = get_secret("USER_DATASET_FOLDER")
            output_csv_path = get_secret("USER_DATASET_FOLDER_OUTPUT")
            if folder_path and output_csv_path is not None:
                processor = FileProcessor(
                    folder_path=folder_path,
                    output_csv_path=output_csv_path,
                    chunksize=800,
                    overlap=50
                )
                asyncio.run(processor.process())
                df = pd.read_csv(output_csv_path, names=['NAME', 'DATA'])
                asyncio.run(_cortex_search.run(df))
    except Exception as err:
        print(f"Some error occurred: {err}")


class RAG:
    def __init__(self, root, session, limit_to_retirve=5):
        self.root = root
        self.session = session
        self._limit_to_retirve = limit_to_retirve
        self.data = ""


    def retrieve_context(self, query: str, user_data: bool, user_schema = None, cortex_service_name = None) -> dict:
        if not self.root or not self.session:
            return ["Something unexpected happened. Contact customer support."]

        if not user_data:
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
                return ["No relevent text found"]
        else:
            user_service = (
                self.root.databases[get_secret("USER_DATABASE")]
                .schemas[user_schema]
                .cortex_search_services[cortex_service_name]
            )

            resp = user_service.search(query=query, columns=["CHUNKS"], limit=self._limit_to_retirve)

            if resp.results:
                return [curr["CHUNKS"] for curr in resp.results]
            else:
                return ["No relevent text found"]


    def create_prompt(self, query:str, context_str: list)-> str:
        prompt = f"""
        You are an expert assistant for interpreting privacy policies and terms and conditions.Your name is Termify Provide clear, factual, and detailed answers based only on the following inputs:
        - **Context:** Relevant information for the current conversation.
        - **Previous Context:** Relevant information from the previous conversation if available.
        If the answer is not in the context, say you don’t have the information. Do not reference or explain the context. Respond courteously to casual greetings.
        Context: {context_str}
        Previous Context: {self.data}
        Question: {query}
        Answer:
        """
        return prompt

    def generate_completion(self, query: str, context_str: list) -> str:
        prompt = self.create_prompt(query, context_str)
        cmd = """select snowflake.cortex.complete(?, ?) as response"""
        model = 'mistral-large2'
        temprature = 0.2
        top_p = 0.3
        result = self.session.sql(cmd, params=[model, prompt, temprature, top_p]).collect()
        try:
            return result[0]['RESPONSE']
        finally:
            temp = self.data + query + result[0]['RESPONSE']
            self.data = Summarize(temp, self.session)


    def query(self, query: str, user_data: bool, user_schema = None, cortexServiceName = None) -> str:
        context_str = self.retrieve_context(query, user_data, user_schema, cortexServiceName)
        return self.generate_completion(query, context_str)


__all__ = ["RAG"]
