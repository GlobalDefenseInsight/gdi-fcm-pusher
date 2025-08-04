import json
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# ✅ Config
PROJECT_ID = "global-defense-insight"
TOPIC = "all"
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
SERVICE_ACCOUNT_FILE = "service_account.json"

# ✅ 🔒 Manual post ID and title for testing
manual_post_id = 18400  # 👈 Replace with your known post ID
manual_title = "Test Post from Firebase Python Script"

# ✅ Authenticate with Firebase
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
credentials.refresh(Request())

# ✅ FCM endpoint
url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

# ✅ Payload
message = {
    "message": {
        "topic": TOPIC,
        "notification": {
            "title": "📰 New Post on Global Defense Insight",
            "body": manual_title
        },
        "data": {
            "postId": str(manual_post_id)
        }
    }
}

# ✅ Send the request
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json; UTF-8",
}
response = requests.post(url, headers=headers, json=message)

print("🔔 Notification sent:", response.status_code, response.text)
