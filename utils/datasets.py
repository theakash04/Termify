import os
import csv
import asyncio
import json
import re
import pandas as pd
from dotenv import load_dotenv
from secret_loader import get_secret
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader  

load_dotenv()

USER_DATASET_FOLDER = get_secret("USER_DATASET_FOLDER")
USER_DATASET_FOLDER_OUTPUT = get_secret("USER_DATASET_FOLDER_OUTPUT")


class FileProcessor:
    """
    FileProcessor:

    A class that processes files from a specified directory, extracting and chunking text content from JSON and PDF files. 
    The extracted chunks are saved into a CSV file for further analysis.

    Attributes:
        folder_path (str): The directory containing the files to be processed.
        output_csv_path (str): The path to the CSV file where processed data will be saved.
        chunk_size (int): The maximum size of each text chunk.
        chunk_overlap (int): The overlap size between consecutive text chunks.
        pdf_data (list): A list to store the text extracted from PDF files.

    Methods:
        clean_json(json_content):
            Recursively cleans JSON content by removing non-alphanumeric characters.
        
        clean_text(chunks):
            Cleans each text chunk by removing non-alphanumeric characters and extra spaces.
        
        chunk_creator(text):
            Splits the given text into chunks based on the specified chunk size and overlap.
        
        extract_pdf_text(pdf_path):
            Extracts text content from a PDF file using PyPDFLoader.
        
        process():
            Processes all files in the folder path, extracting and chunking JSON and PDF content.
            Writes the processed chunks to a CSV file.
    """

    def __init__(self, folder_path, output_csv_path, chunk_size, chunk_overlap):
        self.folder_path = folder_path
        self.output_csv_path = output_csv_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.pdf_data = []

    async def clean_json(self, json_content):
        def recursive_clean(obj):
            if isinstance(obj, dict):
                return recursive_clean(next(iter(obj.values())))
            elif isinstance(obj, list):
                return [recursive_clean(i) for i in obj]
            elif isinstance(obj, str):
                return re.sub(r"[^a-zA-Z0-9\s]", "", obj)
            else:
                return obj

        return recursive_clean(json_content)

    async def clean_text(self, chunks):
        cleaned_chunks = []
        for chunk in chunks:
            try:
                cleaned_chunk = re.sub(r"[^a-zA-Z0-9\s]", "", chunk)
                cleaned_chunk = re.sub(r"\s+", " ", cleaned_chunk).strip()
                cleaned_chunks.append(cleaned_chunk)
            except Exception as e:
                print(f"An error occurred while cleaning a chunk: {e}")
                cleaned_chunks.append(chunk)
        return cleaned_chunks

    async def chunk_creator(self, text):
        try:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
            )
            chunks = text_splitter.split_text(text)
            cleaned_chunks = await self.clean_text(chunks)
            return pd.DataFrame(cleaned_chunks, columns=["CHUNKS"])
        except Exception as e:
            raise RuntimeError(f"An error occurred while chunking the text: {e}")

    async def extract_pdf_text(self, pdf_path):
        try:
            print(f"Loading PDF file with PyPDFLoader: {pdf_path}")
            loader = PyPDFLoader(pdf_path)
            pages = []
            async for page in loader.alazy_load():
                pages.append(page.page_content)
            page_text = "' ".join(pages)
            return page_text
        except Exception as e:
            print(f"Error extracting text from PDF {pdf_path}: {e}")
            return None

    async def process(self):
        print("Started processing...")
        with open(self.output_csv_path, mode="w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["name", "data"])  # Write the CSV header

            for folder_name in os.listdir(self.folder_path):
                folder_full_path = os.path.join(self.folder_path, folder_name)

                if os.path.isdir(folder_full_path):
                    for file_name in os.listdir(folder_full_path):
                        file_full_path = os.path.join(folder_full_path, file_name)
                        print(f"Processing file: {file_full_path}")
                        try:
                            if file_name.endswith(".json"):
                                with open(file_full_path, "r", encoding="utf-8") as json_file:
                                    content = json.load(json_file)
                                cleaned_json = await self.clean_json(content)
                                cleaned_json_str = json.dumps(cleaned_json)
                                chunks_df = await self.chunk_creator(cleaned_json_str)
                                for chunk in chunks_df["CHUNKS"]:
                                    writer.writerow([folder_name, chunk])
                            elif file_name.endswith(".pdf"):
                                print(f"Found PDF file: {file_full_path}")
                                pdf_text = await self.extract_pdf_text(file_full_path) 

                                if pdf_text:
                                    chunks_df = await self.chunk_creator(pdf_text)
                                    for chunk in chunks_df["CHUNKS"]:
                                        writer.writerow([folder_name, chunk])
                                else:
                                    print(f"No extractable text found in PDF: {file_full_path}")
                        except Exception as e:
                            print(f"Error processing {file_full_path}: {e}")
                        print("Done processing file.")

    
async def main():
    folder_path = USER_DATASET_FOLDER
    output_csv_path = USER_DATASET_FOLDER_OUTPUT

    processor = FileProcessor(
        folder_path=folder_path,
        output_csv_path=output_csv_path,
        chunk_size=1000,
        chunk_overlap=100,
    )
    await processor.process()


if __name__ == "__main__":
    asyncio.run(main())
