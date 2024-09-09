import time
import json
import os
import sys
import asyncio
from kasa import Discover, SmartBulb
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

if (int(os.getenv('ENABLE_APP_DEBUG'))):
    logging.basicConfig(level=logging.DEBUG)

CACHE_FILE = os.getenv('CACHE_FILENAME')
CACHE_EXPIRY = int(os.getenv('CACHE_EXPIRY_SECONDS'))
PRIMARY_DEVICE_FILE = os.getenv('PRIMARY_DEVICE_FILENAME')

def rgb_to_hsv(r, g, b):
    """Convert RGB to HSV."""
    r, g, b = r / 255.0, g / 255.0, b / 255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx - mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g - b) / df) + 360) % 360
    elif mx == g:
        h = (60 * ((b - r) / df) + 120) % 360
    elif mx == b:
        h = (60 * ((r - g) / df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = df / mx
    v = mx
    return int(h), int(s * 100), int(v * 100)

async def discover_and_cache_devices(target_alias='',is_setup=False):
    """Attempt to discover devices on network and store target device
    alias to Cache and Storage for future retrieval"""
    task = asyncio.create_task(loading_dots('Searching for devices'))

    try:
        devices = await Discover.discover()

        if not devices:
            print('\n\nCould not find any devices on your network. Make sure to setup your device and connect it to your network, and retry.')
            await cancel_task(task)
            return False

    except Exception as e:
        print(f'\nCritical error occurred: {e}')

    # ensure async task for dot loading is cancelled properly
    await cancel_task(task)

    devices_list = []
    compatible_device_count = 0
    incompatible_device_count = 0

    for ip_addr, dev in devices.items():

        await dev.update()

        if isinstance(dev, SmartBulb) and dev.alias:

           # If target alias passed in then select it automatically otherwise perform prompt
           if dev.alias == target_alias and is_setup == False:
                print(f"Previous device found with alias {dev.alias}")
                continue_w_prev_device = input("Will you like to use this device? Enter 'yes' or 'no': ")

                if continue_w_prev_device.lower() == 'y' or continue_w_prev_device.lower() == 'yes':
                    set_primary_device_data(dev.alias, ip_addr)
                    set_cached_device(ip_addr)
                    return ip_addr
                else:
                    print("Continuing discovery, when completed you will be able to select a new primary device.")
                    is_setup = True
                    target_alias = ''
           else:
                print(f"\nCompatible device found: {dev.alias} @ {ip_addr}")
                compatible_device_count += 1
                devices_list.append([dev.alias, ip_addr])
        else:
           print('\nDevice is not compatible.')
           print(f"{dev}")
           incompatible_device_count += 1

    print(f"\nTotal compatible devices: {compatible_device_count}")
    print(f"\nTotal incompatible devices: {incompatible_device_count}")
    print(f"\nTotal devices found on network: {compatible_device_count + incompatible_device_count}")

    if compatible_device_count == 0:
        print(f"\nNo compatible devices found. Please connect your device to your network and your hardware to the same network, try again.")
        return False

    if not target_alias:

        print("\nList of Compatible Devices")
        print("=========================")
        for index, (dev_alias, ip_addr) in enumerate(devices_list):
            print(f"{index}: {dev_alias} @ {ip_addr}")

        if is_setup and pick_device(devices_list):
            return True

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

    device_alias = devices_list[device_picked][0]

    ip_addr = devices_list[device_picked][1]

    set_primary_device_data(device_alias, ip_addr)

    set_cached_device(ip_addr)

    print(f"\nThank you! Now storing device alias and ip to {PRIMARY_DEVICE_FILE}.")

    print("Continue to Step 3 in README.md")

    print("Note: If you want to change the device number in the future re-run setup.")

    return True

def set_primary_device_data(device_alias, ip_addr):
    """Set primary device, used in app.py to know which device to communicate with"""
    store_device_data = {
        'alias': device_alias,
        'ip': ip_addr
    }

    with open(PRIMARY_DEVICE_FILE, 'w') as f:
        json.dump(store_device_data, f)

    return True

def set_cached_device(ip_addr):
    """Device data is cached to not always run discovery process"""
    cache_data = {
        'ip': ip_addr,
        'timestamp': time.time()
    }

    with open(CACHE_FILE, 'w') as f:
        json.dump(cache_data, f)

    return True

def load_cached_device():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
                if time.time() - cache_data['timestamp'] < CACHE_EXPIRY:
                    return cache_data['ip']
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error reading cache file: {e}")
            return None
    return None

def retrieve_primary_device():
    if os.path.exists(PRIMARY_DEVICE_FILE):
        try:
            with open(PRIMARY_DEVICE_FILE, 'r') as f:
                data = json.load(f)
                return data['alias']
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Error reading file: {e}")
            return None
    return None

async def cancel_task(task):
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

async def loading_dots(text='Loading'):
    while True:
        for dot in ['.', '..', '...']:
            print(f'\r{text}{dot}', end='')
            sys.stdout.flush()
            await asyncio.sleep(0.5)

def create_file(file_name):
    if not os.path.exists(file_name):
        with open(file_name, 'w') as file:
            file.write('')
        print(f'File {file_name} created successfully.')
        return True
    else:
        print(f'File {file_name} already exists.')
        return False
