# Overview

Welcome! Going Light is meant to be used as a status indicator through light, receiving a message with a keyword from a service and triggering a Smart Bulb to notify you...one less message to read and dashboard/screen to context switch to.

The meanings of the lights can be changed to represent different events and statuses.  Essentially, the project is used to facilitate communication through light.  This means that the devices need to have the ability to change colors and be dimmable.

## Brief History
This projects initial purpose was to indicate stages of code deployments by triggering different light bulb colors through a Kasa TP-Link SmartBulb.  The deployment system sent status updates to a Slack channel and a custom slack app was set up to relay the request to an always on Raspberry Pi 2 W running a copy of "Going Light".  The Application then maps the message/status to a pre-defined color and performs an API call to the registered lightbulb causing it to display the color for a certain duration.

## Tech Stack
Created with Flask on a [Raspberry Pi 2 W](https://www.canakit.com/raspberry-pi-zero-2-w.html) (Or any SBC with Wifi connectivity) to control a TP-Link Smart Bulb via [Python Kasa](https://github.com/python-kasa/python-kasa) library.  Ngrok is used to make the pi available publicly to receive incoming API requests.  The application is meant to be running 24/7 so the Pi 2 W was my choice due to the low power consumption when idle and under load.

## Default status/emotions and light color mapping:
   - "In Progress" triggers a blinking Yellow Light for 25 seconds
   - "Fail" triggers a Red Light for 30 seconds
   - "success" triggers a Green Light for 35 seconds
   - "green" triggers a solid green light
   - "laughing" triggers a solid gold "FFD700"
   - "on" and "off" will toggle the light
   - View more [here](https://github.com/its-leofisher/going-light/edit/main/README.md#default-statusemotions-and-light-color-mapping)

## Diagram
<img width="1265" alt="image" src="https://github.com/user-attachments/assets/81124ca5-7352-48df-83ba-7680e6f4a079">

## Prerequisites

- [Raspberry Pi Zero 2 W with Raspbian OS](https://www.raspberrypi.com/products/) with SSH enabled and connected to local network. Other SBCs or Laptop will do.
- Python 3 and pip installed
- Python VirtualEnv
- **tmux** to run app and ngrok in background
- Already configured [TP-Link Kasa smart bulb](https://a.co/d/72jUNL2)
  - Or a device that can change colors and is dimmable
- A Slack workspace and app
    * Phase 2: abstract class for other Communication Apps
- Ngrok
  - [Sign up, install](https://ngrok.com/download) and set up a static domain to make it easier
  - It's important to secure your endpoint

# Setup Steps
You will be able to select a device connected to your local network.  The app will let inform you of any compatible and incompatible devices.  Right now it only supports TP-Link Kasa Smart Bulbs.  There are plans to support multiple brands.

## Step 1: Environment Setup

### 1.1 Update and Upgrade Raspberry Pi packages
Install latest raspbian on SD card using [Raspberry Imager](https://www.raspberrypi.com/software/).

```sh
sudo apt update
sudo apt upgrade
```

### 1.2 Install Tmux, Python and Pip on PI

```sh
sudo apt install python3 python3-pip
sudo apt-get install tmux
```

### 1.3 Clone Going Light Repo

- git clone going-light repo: `git clone git@github.com:its-leofisher/going-light.git`
- `cd going-light`

### 1.4 Create Virtual Env and activate
  ```sh
  pip3 install virtualenv
  source venv/bin/activate
  ```

### 1.5  Install Project Dependencies
- `pip install -r requirements.txt`

## Step 2: Run setup script
This script will create necessary files and perform device discovery.  Ensure your device is set up and connected to your network prior to running.

```sh
python3 setup.py
```

## Step 3: Run Flask Application

### 3.1 Run Flask Application in Dev Mode

```sh
python app.py
```

### 3.2 Start Ngrok

Open a new terminal and start Ngrok to expose your Flask application:

```sh
ngrok http 5000
```

### 3.3 Test your integration [optional]

#### Slack
 - Follow steps in [here](https://github.com/its-leofisher/going-light/blob/main/project-setup-docs.md#testing-slack-integration)

#### Example Curl Command
```bash
curl -X POST https://your_ngrok_url_here.app/v1/events \
-H "Content-Type: application/json" \
-d '{
  "event": {
    "type": "message",
    "text": "success",
    "channel": "CHANNEL_IDS"
  },
  "type": "event_callback"
}'
```

#### More Integrations
 - More integrations coming soon.

## Production Steps
When you're ready to leave the application running in the background permanently we will use GUNICORN to serve the app. SSH into the Pi and run these TMUX commands:

### TMUX: Start App and NGROK

SSH into the raspberry pi. Start App using tmux to run app in background

`tmux new-session -d -s appsession "source <path_to_project>/venv/bin/activate && cd <path_to_project> && gunicorn -w 2 -b 127.0.0.1:8000 app:app"`

### Start NGROK

Running Ngrok and Detach Automatically

`tmux new-session -d -s ngroksession 'gunicorn -w 2 -k uvicorn.workers.UvicornWorker app:app -b 127.0.0.1:8000'`

### It's Ready!

Any events going into `v1/events` endpoint will be verified and processed!

## Color Map Reference
Message in payload: Color Mapping
```
{
    'fail': ('#FF0000', True, 30),
    'in progress': ('#FFFF00', True, 25),
    'in process': ('#FFFF00', True, 25),
    'processing': ('#FFFF00', True, 25),
    'success': ('#5C214A', False, 35),
    'off': ('', None, None),
    'on': ('', None, None),
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
```

### Support
Open to code contributions, bug reports, new ideas or coffee|tea|books

<a href="https://www.buymeacoffee.com/leoeff"><img src="https://img.buymeacoffee.com/button-api/?text=Buy me a coffee||tea||books&emoji=🌞&slug=leoeff&button_colour=FFDD00&font_colour=000000&font_family=Bree&outline_colour=000000&coffee_colour=ffffff" /></a>

