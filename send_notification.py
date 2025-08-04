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

# Load last sent post ID and timestamp
try:
    with open("last_post_id.txt", "r") as f:
        last_id = int(f.read().strip())
    with open("last_post_timestamp.txt", "r") as f:
        last_timestamp_str = f.read().strip()
        last_timestamp = datetime.datetime.fromisoformat(last_timestamp_str)
except (FileNotFoundError, ValueError):
    # Initialize if files don't exist or are invalid
    last_id = 0
    last_timestamp = datetime.datetime.min

# Check latest post from WordPress
try:
    res = requests.get("https://defensetalks.com/wp-json/wp/v2/posts?per_page=1")
    res.raise_for_status() # Raise an exception for bad status codes
    posts = res.json()
    if not posts:
        print("No posts found from WordPress.")
        exit()

    post = posts[0]
    post_id = post["id"]
    title = post["title"]["rendered"]
    post_timestamp_str = post["modified_gmt"] # 'modified_gmt' is a reliable timestamp
    post_timestamp = datetime.datetime.fromisoformat(post_timestamp_str)

except requests.exceptions.RequestException as e:
    print(f"Error fetching posts: {e}")
    exit()
except (KeyError, IndexError) as e:
    print(f"Error parsing post data: {e}")
    exit()

# ✅ New and improved logic
# Check if the post is newer than the last one we sent a notification for.
# Using both ID and timestamp makes this check very robust.
if post_id == last_id and post_timestamp <= last_timestamp:
    print("No new post since the last check.")
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
            "title": "📰 New Post on Global Defense Insight",
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

# ✅ Save the new post ID and timestamp after sending the notification
with open("last_post_id.txt", "w") as f:
    f.write(str(post_id))
with open("last_post_timestamp.txt", "w") as f:
    f.write(post_timestamp.isoformat())
