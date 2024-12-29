from api_client import APIClient
from data_pull import fetch_aged_ar_report, fetch_statement_submission_report

def main():
    # Initialize client
    client = APIClient(login_url="https://live6.dentrixascend.com/login")
    
    # Load cookies or login
    client.load_cookies()
    if not client.session.cookies:
        client.login(
            organization="JuniperD",
            username="Zach",
            password="your_password"
        )
    
    # Fetch reports
    fetch_statement_submission_report(client)
    fetch_aged_ar_report(client)

if __name__ == "__main__":
    main()