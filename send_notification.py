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
STATE_FILE = "last_post.json"

# Load last sent post ID and timestamp from a JSON file
state = {}
try:
    with open(STATE_FILE, "r") as f:
        state = json.load(f)
        last_id = state.get("last_id", 0)
        last_timestamp_str = state.get("last_timestamp", "1970-01-01T00:00:00+00:00")
        last_timestamp = datetime.datetime.fromisoformat(last_timestamp_str)
except (FileNotFoundError, json.JSONDecodeError, ValueError):
    # Initialize if file doesn't exist or is invalid
    last_id = 0
    last_timestamp = datetime.datetime.min

# Check latest post from WordPress
try:
    res = requests.get("https://defensetalks.com/wp-json/wp/v2/posts?per_page=1")
    res.raise_for_status()
    posts = res.json()
    if not posts:
        print("No posts found from WordPress.")
        exit()

    post = posts[0]
    post_id = post["id"]
    title = post["title"]["rendered"]
    post_timestamp_str = post["modified_gmt"]
    post_timestamp = datetime.datetime.fromisoformat(post_timestamp_str)

except (requests.exceptions.RequestException, KeyError, IndexError, ValueError) as e:
    print(f"Error: {e}")
    exit()

# Check if the post is newer
if post_id == last_id and post_timestamp <= last_timestamp:
    print("No new post since the last check.")
    exit()

# Authenticate and send notification
credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
credentials.refresh(Request())

url = f"https://fcm.googleapis.com/v1/projects/{PROJECT_ID}/messages:send"
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
headers = {
    "Authorization": f"Bearer {credentials.token}",
    "Content-Type": "application/json; UTF-8",
}

response = requests.post(url, headers=headers, json=message)
print("🔔 Notification sent:", response.status_code, response.text)

# Save the new state to the JSON file
state["last_id"] = post_id
state["last_timestamp"] = post_timestamp.isoformat()
with open(STATE_FILE, "w") as f:
    json.dump(state, f)

print(f"✅ State saved to {STATE_FILE}")
