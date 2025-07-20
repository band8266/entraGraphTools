import requests
import msal
import io
import os
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

# === CONFIGURATION ===
TENANT_ID = os.environ["TENANT_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
GROUP_ID = os.environ["GROUP_ID"]
VERKADA_API_KEY= os.environ["VERKADA_API_KEY"]
VERKADA_REGION = "api"  # Or 'eu', 'ca', etc.


# === AUTH: Get Microsoft Graph Token ===
def get_graph_token():
    authority = f"https://login.microsoftonline.com/{TENANT_ID}"
    app = msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=authority,
        client_credential=CLIENT_SECRET
    )
    token_result = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token_result.get("access_token")

# === AUTH: Get Verkada Token ===
def get_verkada_token(api_key):
    url = "https://api.verkada.com/token"
    headers = {
        "accept": "application/json",
        "x-api-key": api_key
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("token")
    else:
        print(f"❌ Failed to get Verkada token: {response.status_code} - {response.text}")
        return None

# === GRAPH: Get Users from Entra Group ===
def get_users_from_entra(graph_token):
    url = f"https://graph.microsoft.com/v1.0/groups/{GROUP_ID}/members?$select=mail"
    headers = {"Authorization": f"Bearer {graph_token}"}
    users = []
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to get group members: {response.status_code}")
            break
        data = response.json()
        users += [u["mail"] for u in data["value"] if u.get("mail")]
        url = data.get("@odata.nextLink")
    return users

# === GRAPH: Get Photo Bytes for a User ===
def get_user_photo(graph_token, email):
    url = f"https://graph.microsoft.com/v1.0/users/{email}/photo/$value"
    headers = {"Authorization": f"Bearer {graph_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Photo not found for {email}: {response.status_code}")
        return None

# === VERKADA: Get All Users ===
def get_all_verkada_users(verkada_token):
    url = f"https://{VERKADA_REGION}.verkada.com/access/v1/access_users"
    headers = {"x-verkada-auth": verkada_token}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"❌ Failed to fetch Verkada users: {response.status_code}")
        return {}

    users = response.json().get("access_members", [])
    return {
        user["email"].lower(): user["user_id"]
        for user in users
        if user.get("email") and user.get("user_id")
    }

# === VERKADA: Upload Photo ===
def upload_photo_to_verkada(verkada_token, user_id, photo_bytes):
    url = f"https://{VERKADA_REGION}.verkada.com/access/v1/access_users/user/profile_photo?user_id={user_id}&overwrite=true"
    headers = {
        "x-verkada-auth": verkada_token,
        "Accept": "application/json"
    }
    files = {
        'file': ('profile.jpg', io.BytesIO(photo_bytes), 'image/jpeg')
    }
    response = requests.put(url, headers=headers, files=files)
    if response.ok:
        print(f"✅ Uploaded photo to Verkada user {user_id}")
    else:
        print(f"❌ Failed upload for {user_id}: {response.status_code} - {response.text}")
    return response.ok

# === MAIN ===
def main():
    graph_token = get_graph_token()
    if not graph_token:
        print("Failed to get Microsoft Graph token")
        return

    verkada_token = get_verkada_token(VERKADA_API_KEY)
    if not verkada_token:
        return

    users = get_users_from_entra(graph_token)
    print(f"Found {len(users)} users in Entra group")

    verkada_users = get_all_verkada_users(verkada_token)
    print(f"Found {len(verkada_users)} users in Verkada")

    for email in users:
        email_lower = email.lower()
        print(f"\n📌 Processing {email}...")

        if email_lower not in verkada_users:
            print("⚠️ Not found in Verkada, skipping")
            continue

        photo = get_user_photo(graph_token, email)
        if not photo:
            continue

        verkada_user_id = verkada_users[email_lower]
        upload_photo_to_verkada(verkada_token, verkada_user_id, photo)

if __name__ == "__main__":
    main()
