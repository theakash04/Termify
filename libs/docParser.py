from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
import pandas as pd


class DocumentParser:
    def __init__(
            self, path="/home/pranav/snowflake/Lorem_ipsum.pdf",
            chunk_size=1500,
            chunk_overlap=256
    ):

        self.path = path
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

     
    # Method to loading the pdf files
    def __pdfLoader(self, path): 

        try: 
            loader = PyPDFLoader(path)
            pages = []
        
            for page in loader.alazy_load():
                pages.append(page.page_content)

            pages_text = ", ".join(pages)

            return pages_text

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found at path: {path}")

        except Exception as e:
            raise RuntimeError(f"An error occurred while loading the document: {e}") 
                

    # Method to divde the pdf into chunks
    def chunkCreator(self, path, chunk_size, chunk_overlap):

        doc_text = self.__pdfLoader(path)

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = chunk_size,
            chunk_overlap = chunk_overlap,
            length_function = len
        )
        
        chunks = text_splitter.split_text(doc_text)
        chunks_data_frame = pd.DataFrame(chunks, column=['chunks'], index=False, name=None)

        return chunks_data_frame

__all__ = ["DocumentParser"]


