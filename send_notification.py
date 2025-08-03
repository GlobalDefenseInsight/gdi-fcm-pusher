import json
import requests
from google.auth.transport.requests import Request
from google.oauth2 import service_account

# Firebase project info
PROJECT_ID = "global-defense-insight"
TOPIC = "all"
SCOPES = ["https://www.googleapis.com/auth/firebase.messaging"]
SERVICE_ACCOUNT_FILE = "service_account.json"

# 🔁 Always send mock post (FOR TESTING ONLY)
mock_post_id = 99999
mock_title = "🔧 Test Notification from GitHub Actions"

# Authenticate with service account
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
credentials.refresh(Request())

# FCM endpoint
url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"

# Payload for Firebase push
message = {
    "message": {
        "topic": TOPIC,
        "notification": {
            "title": "📰 New Post on GDI",
            "body": mock_title
        },
        "data": {
            "postId": str(mock_post_id),
            "postLink": "https://defensetalks.com/mock-test-post"
        }
    }
}

# Send request to FCM
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json; UTF-8",
}
response = requests.post(url, headers=headers, json=message)

print("🔔 Notification sent:", response.status_code, response.text)

# Save ID to prevent duplicate notifications (optional)
with open("last_post_id.txt", "w") as f:
    f.write(str(mock_post_id))
