import requests
import json
from config import (
    JIRA_URL, JIRA_USER, JIRA_API_TOKEN, JIRA_PROJECT_KEY,
    JIRA_SEARCH_ENDPOINT, JIRA_API_V2_BASE
)
from utils import clean_alert_title


# Helper function for common headers
def _get_headers():
    return {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }


def create_jira_ticket(summary, description):
    payload = json.dumps({
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": "Task"}
        }
    })

    try:
        response = requests.post(
            JIRA_URL,
            data=payload,
            headers=_get_headers(),
            auth=(JIRA_USER, JIRA_API_TOKEN)
        )

        if response.status_code == 201:
            key = response.json()['key']
            print(f"Success! Ticket created: {key}")
            return key
        else:
            print(f"Failed to create ticket. Status: {response.status_code}, Response: {response.text}")
            return None
    except Exception as e:
        print(f"Error connecting to Jira: {e}")
        return None


# Search ticket
def _find_ticket_by_title(clean_title):
    jql_query = f'project = "{JIRA_PROJECT_KEY}" AND summary ~ "{clean_title}" ORDER BY created DESC'
    payload = json.dumps({
        "jql": jql_query,
        "maxResults": 1,
        "fields": ["summary", "status"]
    })

    try:
        response = requests.post(JIRA_SEARCH_ENDPOINT, data=payload, headers=_get_headers(),
                                 auth=(JIRA_USER, JIRA_API_TOKEN))
        if response.status_code == 200:
            issues = response.json().get("issues", [])
            if issues and issues[0].get("key"):
                return issues[0].get("key")
        print(f"Ticket not found for JQL: {jql_query}")
        return None
    except Exception as e:
        print(f"Error searching ticket: {e}")
        return None


# Add comment
def _add_comment(issue_key, comment_text):
    url = f"{JIRA_API_V2_BASE}/issue/{issue_key}/comment"
    payload = json.dumps({"body": comment_text})

    try:
        response = requests.post(url, data=payload, headers=_get_headers(), auth=(JIRA_USER, JIRA_API_TOKEN))
        if response.status_code == 201:
            print(f"Success! Comment added to: {issue_key}")
            return True
        print(f"Failed to add comment. Status: {response.status_code}")
        return False
    except Exception as e:
        print(f"Error adding comment: {e}")
        return False


# Move status to Done
def _move_to_done(issue_key):
    url = f"{JIRA_API_V2_BASE}/issue/{issue_key}/transitions"
    try:
        response = requests.get(url, headers=_get_headers(), auth=(JIRA_USER, JIRA_API_TOKEN))
        if response.status_code == 200:
            transitions = response.json().get("transitions", [])
            done_id = None

            for t in transitions:
                if t['name'].lower() == "done":
                    done_id = t['id']
                    break

            if done_id:
                payload = json.dumps({"transition": {"id": done_id}})
                move_res = requests.post(url, data=payload, headers=_get_headers(), auth=(JIRA_USER, JIRA_API_TOKEN))
                if move_res.status_code == 204:
                    print(f"BOOM! Ticket {issue_key} was moved to DONE automatically!")
                    return True
                print(f"Failed to move ticket. Status: {move_res.status_code}")
            else:
                print(f"No 'Done' transition found for {issue_key}.")
        return False
    except Exception as e:
        print(f"Error moving ticket: {e}")
        return False


# Main resolution orchestrator
def auto_resolve_ticket(alert_title):
    clean_title = clean_alert_title(alert_title)

    issue_key = _find_ticket_by_title(clean_title)
    if not issue_key:
        return None

    comment_text = "**Auto-Resolve:** The alert has returned to normal state. Issue resolved by Sentinel."
    _add_comment(issue_key, comment_text)

    _move_to_done(issue_key)

    return issue_key