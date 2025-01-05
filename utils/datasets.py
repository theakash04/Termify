import os
import csv
import json
import re
from utils.doc_utils import DocumentProcessor
from tqdm import tqdm


class FileProcessor(DocumentProcessor):
    """
    Processes JSON and PDF files in a folder, extracts content, chunks it,
    and writes the results to a CSV.

    Attributes:
        folder_path (str): Path to the folder with files.
        output_csv_path (str): Path to the output CSV.
        chunk_size (int): Size of each chunk.
        chunk_overlap (int): Overlap between chunks.

    Methods:
        clean_json: Cleans JSON content.
        process: Processes JSON and PDF files in
    """

    def __init__(self, folder_path, output_csv_path, chunksize=None, overlap=None):
        chunk_size = chunksize if chunksize is not None else self.chunk_size
        overlap = overlap if overlap is not None else self.overlap

        super().__init__(chunk_size=chunk_size, overlap=overlap) 
        self.folder_path = folder_path
        self.output_csv_path = output_csv_path

    async def clean_json(self, json_content):
        if isinstance(json_content, dict):
            return await self.clean_json(next(iter(json_content.values())))
        elif isinstance(json_content, list):
            return [await self.clean_json(i) for i in json_content]
        elif isinstance(json_content, str):
            return re.sub(r"[^a-zA-Z0-9\s]", "", json_content)
        else:
            return json_content

    async def process(self):
        print("Started processing...")
        with open(
            self.output_csv_path, mode="w", newline="", encoding="utf-8"
        ) as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["name", "data"])
            files_processed = 0
            for folder_name in tqdm(os.listdir(self.folder_path),desc="Folders"):
                folder_full_path = os.path.join(self.folder_path, folder_name)

                if os.path.isdir(folder_full_path):
                    for file_name in tqdm(os.listdir(folder_full_path),desc=f"Files in {folder_name}", leave=False):
                        file_full_path = os.path.join(folder_full_path, file_name)
                        try:
                            if file_name.endswith(".json"):
                                with open(
                                    file_full_path, "r", encoding="utf-8"
                                ) as json_file:
                                    content = json.load(json_file)
                                cleaned_json = await self.clean_json(content)
                                cleaned_json_str = json.dumps(cleaned_json)
                                chunks_df = self.chunkCreator(cleaned_json_str)
                                for chunk in chunks_df["CHUNKS"]:
                                    writer.writerow(
                                        {"name": folder_name, "data": chunk}
                                    )
                            elif file_name.endswith(".pdf"):
                                pdf_text = await self.pdfLoader(file_full_path)

                                if pdf_text:
                                    chunks_df = self.chunkCreator(pdf_text)
                                    for chunk in chunks_df["CHUNKS"]:
                                        writer.writerow(
                                            {"name": folder_name, "data": chunk}
                                        )
                                else:
                                    print(
                                        f"No extractable text found in PDF: {file_full_path}"
                                    )
                        except Exception as e:
                            print(f"Error processing {file_full_path}: {e}")
                        files_processed += 1
            print(f"Done processing {files_processed} files.")


__all__ = ["FileProcessor"]
