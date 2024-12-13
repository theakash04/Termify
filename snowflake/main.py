import sys
import os
import asyncio
from dotenv import load_dotenv

sys.path.append(os.path.abspath(".."))  # Enable imports from the parent directory
from utils.sessions import SnowflakeConnector
from dbCreator import CortexSearchModule

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
                print("Successfully parsed PDF data!")
            else:
                print(f"The file '{_pdf_path}' does not exist.")
        except Exception as err:
            print(f"Some error occurred: {err}")
    else:
        print("Operation aborted as per your choice.")


async def RAG(question: str, root=None):
    if not root:
        return "Something unexpected happened. Please try again."
    else:
        my_service = (
            root.databases[os.environ["SNOWFLAKE_DATABASE"]]
            .schemas[os.environ["SNOWFLAKE_SCHEMA"]]
            .cortex_search_services[os.environ["SNOWFLAKE_CORTEX_SEARCH_SERVICE"]]
        )
        response = my_service.search(
            query=question, columns=["CHUNKS"], limit=5
        )
        response = response.to_json()

        # NOTE: llm optimization and code starts from here you can remove "\n, \t" from the response of coretex or optimise llm to ignore that

        # NOTE: Here the response of LLM will be returned. This is temporary. [Delete this comment after implementing LLM]
        return response


__all__ = ["RAG"]

