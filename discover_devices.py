import asyncio
import logging
import sys
import time
from kasa import Discover

# logging.basicConfig(level=logging.DEBUG)

async def discover_devices():
    task = asyncio.create_task(loading_dots('Searching for devices'))
    try:
        devices = await Discover.discover()
        if not devices:
            print('\nDevice not found')
    except Exception as e:
        print(f'\nCritical error occurred: {e}')
    finally:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass
        print("\nList of Devices")
        print("=====================")
        for addr, dev in devices.items():
            await dev.update()
            if dev.alias:
               print(f"Alias: {dev.alias} @ {addr}")
            else:
               print('\nDevice is not compatible.')

async def loading_dots(text='Loading'):
    while True:
        for dot in ['.', '..', '...']:
            print(f'\r{text}{dot}', end='')
            sys.stdout.flush()
            await asyncio.sleep(0.5)

if __name__ == "__main__":
    asyncio.run(discover_devices())
