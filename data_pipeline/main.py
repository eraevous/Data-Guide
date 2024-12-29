from api_client import APIClient
from data_pull import fetch_aged_ar_report, fetch_statement_submission_report
import json

def main():
    login_url = "https://live6.dentrixascend.com/login"
    api_url = "https://live6.dentrixascend.com/statementSubmissionReport"

    client = APIClient(login_url, cookie_file="cookie.json")

    # Attempt to load cookies from previous sessions
    client.load_cookies()

    # Login if cookies are invalid
    if not client.session.cookies:
        client.login()

    # Make a GET request
    params = {
        "location": "14000000000286",
        "dateTimeFrom": "0",
        "dateTimeTo": "9999999999999",
        "deliveryMethod": "ELECTRONIC",
        "from": "1",
        "rows": "10000",
        "field": "dateTime",
        "order": "desc"
    }
    try:
        data = client.make_request(api_url, method="GET", params=params)
        #print("Data:", json.dumps(data, indent=2))
    except Exception as e:
        print("Error during request:", e)

if __name__ == "__main__":
    main()
