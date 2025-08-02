import json
import requests
import datetime
import google.auth
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Firebase project info
PROJECT_ID = "global-defense-insight"
TOPIC = "all"
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]

# Load service account JSON from secret
SERVICE_ACCOUNT_FILE = "service_account.json"

# Load last sent post ID
try:
    with open("last_post_id.txt", "r") as f:
        last_id = int(f.read().strip())
except:
    last_id = 0

# Check latest post from WordPress
res = requests.get("https://defensetalks.com/wp-json/wp/v2/posts")
post = res.json()[0]
post_id = post["id"]
title = post["title"]["rendered"]

if post_id <= last_id:
    print("No new post.")
    exit()

# Authenticate with service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
credentials.refresh(Request())

# FCM endpoint
url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

# FCM message payload
message = {
    "message": {
        "topic": TOPIC,
        "notification": {
            "title": "📰 New Post on GDI",
            "body": title
        },
        "data": {
            "postId": str(post_id)
        }
    }
}

# Send notification
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json; UTF-8",
}
response = requests.post(url, headers=headers, json=message)

print("🔔 Notification sent:", response.status_code, response.text)

# Save new post ID
with open("last_post_id.txt", "w") as f:
    f.write(str(post_id))
