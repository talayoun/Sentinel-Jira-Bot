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
            "issuetype": {"name": "Task"}  # Ensure this issue type exists in Jira
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
        
        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

# Run the server
if __name__ == '__main__':
    print("Sentinel Bot is running on port 5001...")
    app.run(host='0.0.0.0', port=5001)