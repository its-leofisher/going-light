import os
import asyncio
import logging
import json
import time
from kasa import Discover
from utils import loading_dots, create_file
from dotenv import load_dotenv

load_dotenv()

if (int(os.getenv('ENABLE_APP_DEBUG'))):
    logging.basicConfig(level=logging.DEBUG)

CACHE_FILE = os.getenv('CACHE_FILENAME')
PRIMARY_DEVICE_FILE = os.getenv('PRIMARY_DEVICE_FILENAME')

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

        devices_list = []
        item_number = 0

        for addr, dev in devices.items():

            await dev.update()

            if dev.alias:
               print(f"{item_number}: {dev.alias} @ {addr}")
               devices_list.append([dev.alias, addr])
            else:
               print('\nDevice is not compatible.')

            ++item_number

        if (pick_device(devices_list)):
            print(f"\nThank you! Now storing device alias and ip to {PRIMARY_DEVICE_FILE}.")
            print("Note: If you want to change the device number in the future re-run setup.")

def pick_device(devices_list):
    """Prompt the user to pick a device."""
    while True:
        print('\nProvide the number of the device you want to respond to events...')
        device_picked = input("> Enter number: ")

        try:
            device_picked = int(device_picked)
            if not devices_list[device_picked]:
                raise IndexError()
            break
        except ValueError:
            print("Invalid input. Please enter a valid integer.")
        except IndexError:
            print("That number does not correspond to a device number on the list. Try again.")
        except KeyboardInterrupt:
            print("\nKeyboard interrupt received. Exiting discover devices set up.")
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}")

    store_device_data = {
        'alias': devices_list[device_picked][0],
        'ip': devices_list[device_picked][1]
    }

    with open(PRIMARY_DEVICE_FILE, 'w') as f:
        json.dump(store_device_data, f)

    return True

if __name__ == "__main__":
    create_file(CACHE_FILE)
    create_file(PRIMARY_DEVICE_FILE)
    asyncio.run(discover_devices())
