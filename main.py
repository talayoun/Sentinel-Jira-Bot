from flask import Flask, request, jsonify
from jira_service import create_jira_ticket, auto_resolve_ticket

app = Flask(__name__)

print("Sentinel System Loaded.")


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

        if state == 'alerting':
            print(f"Processing Alert: {title}")
            create_jira_ticket(f"[Sentinel] {title}", message)

        elif state == 'ok':
            print(f"Processing Auto-Resolve for: {title}")
            auto_resolve_ticket(f"[Sentinel] {title}")

        return jsonify({"status": "received"}), 200

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500


# Run the server
if __name__ == '__main__':
    print("Sentinel Bot is running on port 5001...")
    app.run(host='0.0.0.0', port=5001)