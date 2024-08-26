# The Light

This project is created with a Flask application on a Raspberry Pi to control a TP-Link smart bulb based on Slack events.  Initial purpose is to
indicate progress of deployments to servers.  Facilitating communication through light.

## Setting Up Project

## Prerequisites

- Raspberry Pi with Raspbian OS
- Python 3 and pip installed
- Python Virtual Env
    ```sh
    pip3 install virtualenv
    ```
- TP-Link Kasa smart bulb
- Slack workspace and app
- Ngrok for local public availability using WAF for whitelisting

## Quickstart to get started:
- git clone going-light repo
- `cd going-light`
- `touch device_cache.json` - file used to store information about the bulb minimizing health checks
- `python3 -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`

# Detailed Steps
## Step 1: Environment Setup

### 1.1 Update and Upgrade Raspberry Pi

```sh
sudo apt update
sudo apt upgrade
```

### 1.2 Install Python and Pip

```sh
sudo apt install python3 python3-pip
```

### 1.3 Install Virtualenv

```sh
pip3 install virtualenv
```

### 1.4 Create and Activate Virtual Environment

```sh
python3 -m venv venv
source venv/bin/activate
```

## Step 2: Discover Smart Bulb

### 2.2 Run Discovery Script

```sh
python discover_devices.py
```

Note down the alias of the smart bulb you want to control.

Update alias of light bulb in app.py

## Step 3: Run Flask Application

### 3.1 Activate Virtual Environment

```sh
source venv/bin/activate
```

### 3.2 Run Flask Application

```sh
python app.py
```

### 3.3 Start Ngrok

Open a new terminal and start Ngrok to expose your Flask application:

```sh
ngrok http 5000
```

### 3.4 Update Slack Event Subscription

1. Go to your Slack app settings.
2. In the "Event Subscriptions" section, set the "Request URL" to the Ngrok URL, for example, `https://abcd1234.ngrok.io/slack/events`.
3. Save the changes. Slack will send a verification request to your endpoint.
4. Once the URL is verified, subscribe to the desired events (e.g., `message.channels`).

## Step 4: Test Integration

1. Send a message to your Slack channel (e.g., `#dev-channel`) with text containing `fail`, `in progress`, or `success`.
2. Observe the behavior of your smart bulb based on the message content:
   - `fail`: Bulb blinks red for 10 seconds.
   - `in progress`: Bulb blinks yellow slowly until the next event.
   - `success`: Bulb turns solid #52466F for 25 seconds.

## Production Steps
SSH into the PI and run TMUX sessions:

### Start App and NGROK

Start App using tmux to run app in background

`tmux new-session -d -s sglightsession "source <path_to_project>/venv/bin/activate && cd <path_to_project> && python app.py"`

### Start NGROK

Running Ngrok and Detatch Automatically

`tmux new-session -d -s ngroksession 'ngrok http 5000 --domain informed-absolute-malamute.ngrok-free.app'`

### Reference
Message and Color Mapping
```
{
    'fail': '#FF0000',
    'in progress': '#FFFF00',
    'success': '#52466F',
    'orange': '#FFA500',
    'blue': '#0000FF',
    'green': '#008000',
    'yellow': '#FFFF00',
    'red': '#FF0000',
    'purple': '#800080',
    'black': '#000000',
    'dark green': '#006400',
    'dark blue': '#00008B',
    'happy': '#FFFF00',
    'sad': '#0000FF',
    'laughing': '#FFD700',
    'fun': '#FF69B4'
}
```
