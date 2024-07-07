import asyncio
import logging
from kasa import Discover

logging.basicConfig(level=logging.DEBUG)

async def discover_devices():
    devices = await Discover.discover()
    for addr, dev in devices.items():
        await dev.update()
        print(f"{dev.alias} at {addr}")

if __name__ == "__main__":
    asyncio.run(discover_devices())
