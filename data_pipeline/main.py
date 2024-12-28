import json
from api_client import APIClient
from data_pull import DataPull

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

    # Static parameters for GET
    get_urls = [
        "https://live6.dentrixascend.com/statementSubmissionReport?location=14000000000286&dateTimeFrom=0&dateTimeTo=9999999999999&deliveryMethod=ELECTRONIC&from=1&rows=10000&field=dateTime&order=desc",
        "https://live6.dentrixascend.com/statementSubmissionReport?location=14000000000286&dateTimeFrom=0&dateTimeTo=9999999999999&deliveryMethod=MAIL_FOR_ME&from=1&rows=10000&field=dateTime&order=desc",
        "https://live6.dentrixascend.com/statementSubmissionReport?location=14000000000286&dateTimeFrom=0&dateTimeTo=9999999999999&deliveryMethod=PRINT&from=1&rows=10000&field=dateTime&order=desc"
    ]
   
    get_params = {
        "location": "14000000000286",
        "dateTimeFrom": "0",
        "dateTimeTo": "9999999999999",
        "deliveryMethod": "ELECTRONIC",
        "from": "1",
        "rows": "10000",
        "field": "dateTime",
        "order": "desc"
    }
    DataPull.get_data(client, get_urls, get_params, "statement_submission.csv")

    # Static parameters for POST
    post_urls = ["https://live6.dentrixascend.com/agedReceivables/create"]
    post_payload = {
        "0": {"id": 14000000000191},
        "1": {"id": 14000000000756},
        "2": {"id": 14000000001321},
        "3": {"id": 14000000001886},
        "asOfDate": 1734480000000,
        "billingTypes": [],
        "isEmpty": False,
        "isPendingClaimCheckboxDisabled": False,
        "isPendingClaimHidden": False,
        "locations": [14000000000286],
        "period": "ALL",
        "periodName": "All",
        "skipPendingClaim": False,
        "start": 1644772954021,
        "withOrganization": False
    }
    DataPull.post_data(client, post_urls, post_payload, "aged_ar_report.csv")

if __name__ == "__main__":
    main()