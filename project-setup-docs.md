### Slack Setup

1. Go to the Slack app settings.
2. In the "Event Subscriptions" section, set the "Request URL" to the Ngrok URL, for example, `https://YOURDOMAIN.ngrok.io/slack/events`.
3. Save the changes. Slack will send a verification request to the endpoint.
4. Once the URL is verified, subscribe to the desired events (e.g., `message.channels`).
5. Add your slack channel ID to the SLACK_ALLOWED_CHANNELS const in app.py

## Testing Slack Integration

1. Send a message to your Slack channel (e.g., `#your-channel`) with text containing `fail`, `in progress`, or `success`.

2. Or Alternatively use this curl command:
  ```bash
  curl -X POST http://localhost:5000/slack/events \
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
4. Observe the behavior of your smart bulb based on the message content:
   - `fail`: Bulb blinks red for 10 seconds.
   - `in progress`: Bulb blinks yellow slowly until the next event.
   - `success`: Bulb turns solid #52466F for 25 seconds.


