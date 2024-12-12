from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd

"""
DocumentParser Class:

This class provides functionality to parse a PDF document and divide its content into manageable chunks for further processing. 
It uses the RecursiveCharacterTextSplitter from LangChain and the PyPDFLoader for loading and processing the PDF.

Attributes:
    path (str): Path to the PDF file to be processed.
    chunk_size (int): The size of each chunk to divide the document into.
    chunk_overlap (int): The overlap size between consecutive chunks to maintain context.

Methods:
    __pdfLoader(path):
        Loads the content of the PDF file from the specified path and returns the combined text.

    chunkCreator():
        Divides the loaded document text into chunks based on the class's chunk size and overlap.

Usage:
    Create an instance of the class with appropriate parameters and call the `chunkCreator` method to parse and divide a PDF into chunks.

"""


class DocumentParser:
    def __init__(
        self,
        path="/home/pranav/snowflake/Lorem_ipsum.pdf",
        chunk_size=1500,
        chunk_overlap=256,
    ):

        self.path = path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    # Method to load the PDF files
    async def __pdfLoader(self, path):
        try:
            loader = PyPDFLoader(path)
            pages = []

            async for page in loader.alazy_load():
                pages.append(page.page_content)

            pages_text = ", ".join(pages)

            return pages_text

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at path: {path}")

        except Exception as e:
            raise RuntimeError(f"An error occurred while loading the document: {e}")

    # Method to divide the PDF into chunks
    async def chunkCreator(self):
        doc_text = await self.__pdfLoader(self.path)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
        )

        chunks = text_splitter.split_text(doc_text)
        chunks_data_frame = pd.DataFrame(chunks, columns=["CHUNKS"])

        return chunks_data_frame


__all__ = ["DocumentParser"]
