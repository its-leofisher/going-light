import time
import json
import os
from kasa import Discover, SmartBulb
import logging

logger = logging.getLogger(__name__)

CACHE_FILE = 'device_cache.json'
CACHE_EXPIRY = 12 * 60 * 60  # 12 hours

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

async def discover_and_cache_device(target_alias):
    devices = await Discover.discover()
    for addr, dev in devices.items():
        await dev.update()
        if isinstance(dev, SmartBulb) and dev.alias == target_alias:
            # Cache the device IP
            cache_data = {
                'ip': addr,
                'timestamp': time.time()
            }
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache_data, f)
            return addr
    return None

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

