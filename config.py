import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Jira Credentials
JIRA_URL = os.getenv("JIRA_URL")
JIRA_USER = os.getenv("JIRA_USER")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
JIRA_PROJECT_KEY = os.getenv("JIRA_PROJECT_KEY")

# API Endpoints
JIRA_BASE_URL = JIRA_URL.split("/rest/api")[0]
JIRA_API_V2_BASE = f"{JIRA_BASE_URL}/rest/api/2"
JIRA_API_V3_BASE = f"{JIRA_BASE_URL}/rest/api/3"

JIRA_SEARCH_ENDPOINT = f"{JIRA_API_V3_BASE}/search/jql"