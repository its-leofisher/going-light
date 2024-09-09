from flask import Flask, request, jsonify
import asyncio
import logging
from kasa import SmartBulb
from utils import rgb_to_hsv, discover_and_cache_devices, load_cached_device, retrieve_primary_device
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

if (int(os.getenv('ENABLE_APP_DEBUG'))):
    logging.basicConfig(level=logging.DEBUG)

logger = logging.getLogger(__name__)

TARGET_BULB_ALIAS = retrieve_primary_device()
SLACK_ALLOWED_CHANNELS = {'CHANNEL_IDS'}

async def set_bulb_color(bulb, hex_color, duration=None, blink=False):
    red, green, blue = int(hex_color[1:3], 16), int(hex_color[3:5], 16), int(hex_color[5:7], 16)
    hue, saturation, value = rgb_to_hsv(red, green, blue)
    await bulb.turn_on()
    await asyncio.sleep(1)
    await bulb.set_hsv(hue, saturation, value)
    
    if blink:
        if duration is None:
            duration = 10
        for _ in range(duration // 2):  # Blinking interval of 2 seconds
            await bulb.turn_off()
            await asyncio.sleep(1)
            await bulb.turn_on()
            await asyncio.sleep(1)
    elif duration:
        await asyncio.sleep(duration)
        await bulb.turn_off()
    else:
        logger.debug("Keeping light on indefinitely")

async def handle_message_event(event):
    logger.debug(f"Handling event: {event}")
    channel_id = event.get('channel')
    if channel_id in SLACK_ALLOWED_CHANNELS:
        ip_address = load_cached_device()
        if not ip_address:
            ip_address = await discover_and_cache_devices(TARGET_BULB_ALIAS)

        if ip_address:
            bulb = SmartBulb(ip_address)
            await bulb.update()

            # Colors and blink status for different message types
            color_map = {
                'fail': ('#FF0000', True, 30),
                'in progress': ('#FFFF00', True, 25),
                'in process': ('#FFFF00', True, 25),
                'processing': ('#FFFF00', True, 25),
                'success': ('#5C214A', False, 35),
                'off': ('', None, None),  # Special case to handle power off
                'on': ('', None, None),  # Special case to handle power on
                'orange': ('#FFA500', False, None),
                'royal purple': ('#5C214A', False, None),
                'matcha green': ('#94A796', False, None),
                'blue': ('#0000FF', False, None),
                'green': ('#008000', False, None),
                'yellow': ('#FFFF00', False, None),
                'red': ('#FF0000', False, None),
                'purple': ('#800080', False, None),
                'black': ('#000000', False, None),
                'dark green': ('#006400', False, None),
                'dark blue': ('#00008B', False, None),
                'happy': ('#FFFF00', False, None),
                'sad': ('#0000FF', False, None),
                'laughing': ('#FFD700', False, None),
                'fun': ('#FF69B4', False, None)
            }

            message_text = event.get('text', '').lower().strip()
            status_success = False  # Flag to track success status

            for keyword, (color, blink, duration) in color_map.items():
                if keyword in message_text:
                    if keyword == 'off':
                        await bulb.turn_off()
                    elif keyword == 'on':
                        await bulb.turn_on()
                    else:
                        await set_bulb_color(bulb, color, duration, blink)
                    break
            else:
                logger.warning("Unrecognized event type or command")

            # Additional check in attachments if 'success' was not detected in the text
            if not status_success and 'attachments' in event:
                for attachment in event['attachments']:
                    for field in attachment.get('fields', []):
                        if field.get('title', '').lower() == 'status' and field.get('value', '').lower() == 'success':
                            status_success = True
                            break
                    if status_success:
                        break

            if status_success:
                await set_bulb_color(bulb, '#52466F', 15, blink=False)
        else:
            logger.warning("Unable to find a device with alias: " + TARGET_BULB_ALIAS + ". Make sure it's connected to your network.")
    else:
        logger.warning("Event channel not in allowed channels: " + channel_id)

@app.route('/v1/events', methods=['POST'])
def events_endpoint():
    data = request.json
    logger.debug(f"Received data: {data}")

    # Verify the request
    if 'type' in data and data['type'] == 'url_verification':
        logger.debug("URL verification request")
        return jsonify({'challenge': data['challenge']})

    # Process message event
    if 'event' in data and data['event']['type'] == 'message':
        asyncio.run(handle_message_event(data['event']))

    return '', 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
