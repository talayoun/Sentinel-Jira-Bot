def clean_alert_title(alert_title):
    # Remove prefix and special characters to prevent JQL search errors
    return alert_title.replace("[Sentinel] ", "").replace("!", "")