import json
import requests

SLACK_TOKEN = 'your-slack-bot-token'
GOOGLE_CHAT_WEBHOOK_URL = 'https://chat.googleapis.com/v1/spaces/XXXXX/messages?key=your-key&token=your-token'

def handler(event, context):
    # Extract the body from the incoming API Gateway event
    body = json.loads(event.get('body', '{}'))

    if 'slack' in event['headers']['User-Agent']:
        # This is a Slack event
        slack_event = body.get('event', {})
        if slack_event.get('type') == 'message':
            user_id = slack_event.get('user')
            message_text = slack_event.get('text')
            channel = slack_event.get('channel')
            print(f"Received message from Slack user {user_id}: {message_text}")
            # Forward message to Google Chat
            response_code = send_message_to_google_chat(f"Message from Slack user {user_id}: {message_text}")
            return {
                'statusCode': 200,
                'body': json.dumps({'status': 'success', 'code': response_code})
            }

    elif 'google-chat' in event['headers']['User-Agent']:
        # This is a Google Chat event
        google_chat_message = body.get('message', {})
        text = google_chat_message.get('text', '')
        sender = google_chat_message.get('sender', {}).get('displayName', 'Unknown')
        print(f"Received message from Google Chat user {sender}: {text}")
        # Forward message to Slack
        response_code = send_message_to_slack('#general', f"Message from Google Chat user {sender}: {text}")
        return {
            'statusCode': 200,
            'body': json.dumps({'status': 'success', 'code': response_code})
        }

    return {
        'statusCode': 400,
        'body': json.dumps({'error': 'Unsupported event'})
    }

def send_message_to_google_chat(message):
    data = {"text": message}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(GOOGLE_CHAT_WEBHOOK_URL, headers=headers, data=json.dumps(data))
    return response.status_code

def send_message_to_slack(channel, text):
    url = 'https://slack.com/api/chat.postMessage'
    headers = {'Authorization': f'Bearer {SLACK_TOKEN}'}
    data = {
        'channel': channel,
        'text': text
    }
    response = requests.post(url, headers=headers, json=data)
    return response.status_code
