import os
import csv
import asyncio
from docParser import DocumentParser  

"""
JSONToCSVProcessor and DocumentParser Integration:

This script provides functionality to process JSON files in a directory structure,
chunk their content into smaller manageable pieces, and save the results in a CSV file.
It integrates the `DocumentParser` class for chunking and cleaning the text content.

Classes:
    - JSONToCSVProcessor:
        Processes JSON files in nested folders, extracts text chunks using `DocumentParser`,
        and writes the folder names and corresponding chunks to a CSV file.

    - DocumentParser:
        Parses and chunks document content (PDFs or JSON text) using LangChain's
        RecursiveCharacterTextSplitter, and cleans the resulting chunks.

JSONToCSVProcessor:
    Attributes:
        folder_path (str): Path to the root folder containing subfolders with JSON files.
        output_csv_path (str): Path to the output CSV file.
        chunk_size (int): Size of each text chunk for processing.
        chunk_overlap (int): Overlap size between consecutive chunks to maintain context.

    Methods:
        process():
            Processes all JSON files in the folder structure, extracts text chunks
            using DocumentParser, and writes the folder name and chunks to a CSV file.


"""


class JSONToCSVProcessor:
    def __init__(self, folder_path, output_csv_path, chunk_size, chunk_overlap):
        self.folder_path = folder_path
        self.output_csv_path = output_csv_path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def process(self):
        with open(self.output_csv_path, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['name', 'data'])  # Write the CSV header

            for folder_name in os.listdir(self.folder_path):
                folder_full_path = os.path.join(self.folder_path, folder_name)

                if os.path.isdir(folder_full_path):
                    for file_name in os.listdir(folder_full_path):
                        if file_name.endswith('.json'):
                            file_full_path = os.path.join(folder_full_path, file_name)

                            parser = DocumentParser(
                                path=file_full_path,
                                chunk_size=self.chunk_size,
                                chunk_overlap=self.chunk_overlap,
                            )
                            try:
                                chunks_df = await parser.chunkCreator()

                                for chunk in chunks_df["CHUNKS"]:
                                    writer.writerow([folder_name, chunk])
                            except Exception as e:
                                print(f"Error processing {file_full_path}: {e}")

async def main():
    folder_path = USER_DATASET_FOLDER
    output_csv_path = USER_DATASET_FOLDER_OUTPUT

    processor = JSONToCSVProcessor(
        chunk_size=1000,  
        chunk_overlap=100,  #
        folder_path=folder_path,
        output_csv_path=output_csv_path,
    )
    await processor.process()



if __name__ == "__main__":
    asyncio.run(main())

