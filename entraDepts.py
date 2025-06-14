import requests
from msal import ConfidentialClientApplication
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Auth setup (from environment)
TENANT_ID = os.environ["TENANT_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]


app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET
)

token_response = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
access_token = token_response.get("access_token")

headers = {
    "Authorization": f"Bearer {access_token}"
}

graph_url = (
    "https://graph.microsoft.com/v1.0/users?"
    "$filter=(userType eq 'Member') and (accountEnabled eq true)"
    "&$select=department"
    "&$top=999"
)

departments = set()

while graph_url:
    r = requests.get(graph_url, headers=headers)
    r.raise_for_status()
    data = r.json()

    for u in data.get("value", []):
        dept = u.get("department")
        if dept:
            departments.add(dept)

    graph_url = data.get("@odata.nextLink")

print("✅ Unique Departments (Enabled, Active Users Only):")
for dept in sorted(departments):
    print(f"- {dept}")
