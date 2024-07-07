## Prerequisites

- Raspberry Pi with Raspbian OS
- Python 3 and pip installed
- TP-Link Kasa smart bulb
- Slack workspace and app
- Ngrok installed

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
mkdir ~/proj_folder && cd ~/proj_folder
python3 -m venv venv
source venv/bin/activate
```

### 1.5 Install Dependencies

```sh
pip install flask requests python-kasa
```

## Step 2: Discover Smart Bulb

### 2.1 Run Discovery Script

```sh
python discover_devices.py
```

Note down the alias of the smart bulb you want to control.

## Step 3: Run Flask Application

### 3.0
Update app.py file with alias of device.

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

1. Go to the Slack app settings.
2. In the "Event Subscriptions" section, set the "Request URL" to the Ngrok URL, for example, `https://abcd1234.ngrok.io/slack/events`.
3. Save the changes. Slack will send a verification request to the endpoint.
4. Once the URL is verified, subscribe to the desired events (e.g., `message.channels`).

## Step 4: Test Integration

1. Send a message to your Slack channel (e.g., `#your-channel`) with text containing `fail`, `in progress`, or `success`.
2. Observe the behavior of your smart bulb based on the message content:
   - `fail`: Bulb blinks red for 10 seconds.
   - `in progress`: Bulb blinks yellow slowly until the next event.
   - `success`: Bulb turns solid #52466F for 25 seconds.


