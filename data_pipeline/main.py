from api_client import APIClient
from data_pull import fetch_aged_ar_report, fetch_statement_submission_report
import json

def load_config(config_file):
    with open(config_file, 'r') as file:
        config = json.load(file)
    return config

def main():
    # Load configuration
    config = load_config('config.json')

    # Initialize API client
    client = APIClient(login_url=config["login_url"])

    # Load or authenticate
    client.load_cookies()
    if not client.session.cookies:
        client.login(
            username=config["username"],
            password=config["password"],
            organization=config["organization"]
        )

    # Fetch reports
    fetch_statement_submission_report(client)
    fetch_aged_ar_report(client)

if __name__ == "__main__":
    main()