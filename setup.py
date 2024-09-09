import os
import asyncio
import logging
import json
import time
from kasa import Discover
from utils import loading_dots, create_file, discover_and_cache_devices
from dotenv import load_dotenv

load_dotenv()

if (int(os.getenv('ENABLE_APP_DEBUG'))):
    logging.basicConfig(level=logging.DEBUG)

CACHE_FILE = os.getenv('CACHE_FILENAME')
PRIMARY_DEVICE_FILE = os.getenv('PRIMARY_DEVICE_FILENAME')

if __name__ == "__main__":
    create_file(CACHE_FILE)
    create_file(PRIMARY_DEVICE_FILE)
    asyncio.run(discover_and_cache_devices('', True))
