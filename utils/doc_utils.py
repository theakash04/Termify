from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd
import re

"""
DocumentParser Class:

This class provides functionality to parse a PDF document and divide its content into manageable chunks for further processing. 
It uses the RecursiveCharacterTextSplitter from LangChain and the PyPDFLoader for loading and processing the PDF.

Attributes:
    path (str): Path to the PDF file to be processed.
    chunk_size (int): The size of each chunk to divide the document into.
    chunk_overlap (int): The overlap size between consecutive chunks to maintain context.

Methods:
    pdfLoader(path):
        Loads the content of the PDF file from the specified path and returns the combined text.

    cleanText(texts):
        Clean the texts using regex

    chunkCreator():
        Divides the loaded document text into chunks based on the class's chunk size and overlap.

Usage:
    Create an instance of the class with appropriate parameters and call the `chunkCreator` method to parse and divide a PDF into chunks.

"""


class DocumentProcessor:
    def __init__(
        self,
        chunk_size=1000,
        overlap=100,
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap

    async def pdfLoader(self, file_path):
        try:
            loader = PyPDFLoader(file_path)
            pages = []
            async for page in loader.alazy_load():
                pages.append(page.page_content)
            pages_text = ", ".join(pages)

            return pages_text
        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at path: {file_path}")
        except Exception as e:
            raise RuntimeError(f"An error occurred while loading the document: {e}")

    async def clean_text(self, texts):
        cleaned_chunks = []
        for chunk in texts:
            try:
                cleaned_chunk = re.sub(r"[^a-zA-Z0-9\s]", "", chunk)
                cleaned_chunk = re.sub(r"\s+", " ", cleaned_chunk).strip()
                cleaned_chunks.append(cleaned_chunk)
            except Exception as e:
                print(f"An error occurred while cleaning a chunk: {e}")
                cleaned_chunks.append(chunk)
        return cleaned_chunks

    # Method to divide the PDF into chunks
    async def chunkCreator(self, texts):
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.overlap,
                length_function=len,
            )

            chunks = text_splitter.split_text(texts)
            cleaned_chunks = await self.clean_text(chunks)
            chunks_data_frame = pd.DataFrame(cleaned_chunks, columns=["CHUNKS"])
            return chunks_data_frame
        except Exception as e:
            raise RuntimeError(f"An error occurred while processing the document: {e}")


__all__ = ["DocumentProcessor"]
