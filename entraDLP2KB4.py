import requests
from msal import ConfidentialClientApplication
import time
# === CONFIGURATION ===
TENANT_ID = os.environ["TENANT_ID"]
CLIENT_ID = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]
KB4_EVENT_URL = "https://api.events.knowbe4.com/events"
KB4_EVENT_API_KEY = os.environ["KB4_EVENT_API_KEY"]
DRY_RUN = False  # Set to False to actually send to KB4

# === Get MS Graph Token ===
app = ConfidentialClientApplication(
    CLIENT_ID,
    authority=f"https://login.microsoftonline.com/{TENANT_ID}",
    client_credential=CLIENT_SECRET
)
token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
access_token = token.get("access_token")
if not access_token:
    raise Exception("Failed to get Graph token")

headers_graph = {"Authorization": f"Bearer {access_token}"}
headers_kb4   = {
    "Authorization": f"Bearer {KB4_EVENT_API_KEY}",
    "Content-Type": "application/json"
}

# === Fetch & Process Alerts ===
alert_url = (
    "https://graph.microsoft.com/v1.0/security/alerts?"
    "$filter=category eq 'DataLossPrevention' and status eq 'newAlert'"
)
while alert_url:
    resp = requests.get(alert_url, headers=headers_graph)
    resp.raise_for_status()
    data = resp.json()
    for alert in data.get("value", []):
        uid   = alert.get("id")
        upn   = alert.get("userStates", [{}])[0].get("userPrincipalName")
        title = alert.get("title","No title")
        timestamp = alert.get("createdDateTime", "Unknown")
        if not upn:
            continue

        desc = f"DLP Alert: {title} on {timestamp}"
        payload = {
            "target_user":  upn,
            "event_type":   "dlp_violation",
            "description":  desc
        }

        if DRY_RUN:
            print(f"[DRY RUN] → {upn}: {desc}")
        else:
            kresp = requests.post(KB4_EVENT_URL, json=payload, headers=headers_kb4)
            if kresp.status_code == 201:
                # mark the alert so it won’t fire again
                patch_url = f"https://graph.microsoft.com/v1.0/security/alerts/{uid}"
                requests.patch(patch_url, headers=headers_graph, json={"status":"inProgress"})
            else:
                print(f"KB4 error {kresp.status_code}: {kresp.text}")
            time.sleep(1)  # throttle KB4 calls

    alert_url = data.get("@odata.nextLink")
    time.sleep(1)
