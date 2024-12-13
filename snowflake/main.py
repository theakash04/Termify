import sys
import os
sys.path.append(os.path.abspath("..")) # Enable imports from the parent directory
from utils.sessions import SnowflakeConnector
from dbCreator import CortexSearchModule
import asyncio




connector = SnowflakeConnector()

pdf_path = "/home/akash/Downloads/BNS-PDF-Download.pdf"

cortex_search = CortexSearchModule(connector, pdf_path)

asyncio.run(cortex_search.run())
