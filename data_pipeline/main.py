from api_client import APIClient
from data_pull import DataPull

def main():
    # Initialize API client
    client = APIClient(login_url="https://live6.dentrixascend.com/login")

    # Load or authenticate
    client.load_cookies()
    if not client.session.cookies:
        client.login(
            username="your_username",
            password="your_password",
            organization="your_organization"
        )

    # Static parameters for GET
    get_url = "https://live6.dentrixascend.com/statementSubmissionReport"
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
    DataPull.get_data(client, get_url, get_params, "statement_submission.csv")

    # Static parameters for POST
    post_url = "https://live6.dentrixascend.com/agedARReport"
    post_payload = {
        "location": "14000000000286",
        "dateRange": {"from": "2024-01-01", "to": "2024-12-31"},
        "filters": {"minBalance": 0},
        "groupBy": "provider",
        "rows": 10000
    }
    DataPull.post_data(client, post_url, post_payload, "aged_ar_report.csv")

if __name__ == "__main__":
    main()
