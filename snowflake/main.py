import sys
import os
from utils.sessions import SnowflakeConnector
from dbCreator import CortexSearchModule
import asyncio

sys.path.append(os.path.abspath("..")) # Enable imports from the parent directory


connector = SnowflakeConnector()

pdf_path = "/home/akash/Downloads/BNS-PDF-Download.pdf"

cortex_search = CortexSearchModule(connector, pdf_path)

asyncio.run(cortex_search.run())
