import os
from flask import Flask, request, jsonify
import requests
import json
from dotenv import load_dotenv

# Load configurations and secrets
load_dotenv()  # Loads the .env file containing credentials
app = Flask(__name__)

# Retrieve variables from the secret .env file
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# Extract the base URL (removing /rest/api)
JIRA_BASE_URL = JIRA_URL.split("/rest/api")[0]

JIRA_API_V2_BASE = f"{JIRA_BASE_URL}/rest/api/2"
JIRA_API_V3_BASE = f"{JIRA_BASE_URL}/rest/api/3"

JIRA_SEARCH_ENDPOINT = f"{JIRA_API_V3_BASE}/search/jql"

print(f"Sentinel System Loaded.")
print(f"Targeting Jira Project: {JIRA_PROJECT_KEY}")

# Create a Jira ticket
def create_jira_ticket(summary, description):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    
    # Construct the payload for Jira
    payload = json.dumps({
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Task"}
        }
    })

    try:
        # Send the POST request to Jira API
        response = requests.post(
            JIRA_URL,
            data=payload,
            headers=headers,
            auth=(JIRA_USER, JIRA_API_TOKEN)
        )
        
        # Check if the ticket was created successfully (HTTP 201)
        if response.status_code == 201:
            key = response.json()['key']
            print(f"Success! Ticket created: {key}")
            return key
        else:
            print(f"Failed to create ticket. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        return None


# Find and auto - resolve a Jira ticket
def resolve_jira_ticket(alert_title):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    clean_title = alert_title.replace("[Sentinel] ", "").replace("!", "")

    jql_query = f'project = "{JIRA_PROJECT_KEY}" AND summary ~ "{clean_title}" ORDER BY created DESC'

    search_payload = json.dumps({
        "jql": jql_query,
        "maxResults": 1,
        "fields": ["summary", "status"]
    })

    try:
        response = requests.post(
            JIRA_SEARCH_ENDPOINT,
            data=search_payload,
            headers=headers,
            auth=(JIRA_USER, JIRA_API_TOKEN)
        )

        if response.status_code == 200:
            json_response = response.json()
            issues = json_response.get("issues", [])

            if not issues:
                print(f"No matching ticket found to resolve. JQL: {jql_query}")
                return None

            issue_key = issues[0].get("key")
            if not issue_key:
                print(f"Error: Jira returned an issue without a 'key'. Response: {json_response}")
                return None

            comment_url = f"{JIRA_API_V2_BASE}/issue/{issue_key}/comment"
            comment_payload = json.dumps({
                "body": "**Auto-Resolve:** The alert has returned to normal state. Issue resolved by Sentinel."
            })

            res = requests.post(
                comment_url,
                data=comment_payload,
                headers=headers,
                auth=(JIRA_USER, JIRA_API_TOKEN)
            )

            if res.status_code == 201:
                print(f"Success! Added resolved comment to: {issue_key}")
                return issue_key
            else:
                print(f"Failed to add comment. Status: {res.status_code}, Response: {res.text}")
                return None
        else:
            print(f"Failed to search Jira. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except Exception as e:
        print(f"Error resolving Jira ticket: {e}")
        return None

# The Webhook (Listener for Grafana alerts)
@app.route('/webhook', methods=['POST'])
def grafana_listener():
    try:
        data = request.json
        print("\nAlert received from Grafana!")
        
        # Extract data (Compatible with standard Grafana payload)
        title = data.get('title', 'Unknown Alert')
        message = data.get('message', 'No details provided')
        state = data.get('state', 'alerting')
        
        # Only create a ticket if the state is 'alerting'
        if state == 'alerting':
            print(f"Processing Alert: {title}")
            create_jira_ticket(f"[Sentinel] {title}", message)

        elif state == 'ok':
            print(f"Processing Auto-Resolve for: {title}")
            resolve_jira_ticket(f"[Sentinel] {title}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Run the server
if __name__ == '__main__':
    print("Sentinel Bot is running on port 5001...")
    app.run(host='0.0.0.0', port=5001)