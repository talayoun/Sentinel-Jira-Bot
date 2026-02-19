# Sentinel: NOC Auto-Remediation Bot

## Overview
Sentinel is a lightweight, automated webhook listener built with Python and Flask. It is designed to simulate a NOC workflow by automatically handling monitoring alerts (e.g., from Grafana/Datadog) and converting them into actionable Jira tickets.

## Architecture & Technologies
* **Python & Flask:** Serves as the webhook listener, processing incoming JSON payloads.
* **Jira REST API:** Used to dynamically open tasks when alerts fire, and auto-resolve them when the system recovers.
* **Ngrok (Reverse Proxy / Tunneling):** Used to expose the local Flask server to the public internet securely, allowing external monitoring services to trigger the webhook behind a NAT/Firewall.

## Features
1. **Ticket Creation:** Parses incoming POST requests and creates Jira tasks categorized by severity.
2. **Auto-Resolve (Smart Logic):** If an alert payload indicates a return to normal state (`"state": "ok"`), the bot queries the Jira API for the open ticket and adds a resolution comment automatically, saving manual NOC labor.

## How it Works
1. A monitoring tool sends a POST request with an alert payload to the `ngrok` public URL.
2. `ngrok` tunnels the request to the local Flask server running on port 5001.
3. The bot evaluates the `"state"` of the alert.
4. It authenticates with Jira via API tokens and executes the relevant action (Open/Resolve).