import pandas as pd
import os

def fetch_aged_ar_report(client, output_dir):
    """
    Fetch the Aged AR Report using a POST request.
    """
    url = "https://live6.dentrixascend.com/agedReceivables/create"
    payload = {
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
    
    data = client.make_request(url, method="POST", payload=payload)['receivables']['agedReceivables']
    df = pd.json_normalize(data)

    print(df.head())

    # Save to CSV
    output_path = os.path.join(output_dir, "aged_ar_report.csv")
    df.to_csv(output_path, index=False)

    print("Aged AR Report saved to aged_ar_report.csv")

def fetch_statement_submission_report(client, output_dir):
    """
    Fetch the Statement Submission Report using a GET request.
    """
    url = "https://live6.dentrixascend.com/statementSubmissionReport"
    params1 = {
        "location": "14000000000286",
        "dateTimeFrom": "0",
        "dateTimeTo": "9999999999999",
        "deliveryMethod": "ELECTRONIC",
        "from": "1",
        "rows": "10000",
        "field": "dateTime",
        "order": "desc"
    }

    params2, params3 = params1.copy(), params1.copy()
    params2["deliveryMethod"] = "MAIL_FOR_ME"
    params3["deliveryMethod"] = "PRINT"

    data1 = client.make_request(url, method="GET", params=params1)["data"]
    data2 = client.make_request(url, method="GET", params=params2)["data"]
    data3 = client.make_request(url, method="GET", params=params3)["data"]

    # Convert to dataframes and add source column
    df1 = pd.json_normalize(data1)
    df1["source"] = "ELECTRONIC"
    df2 = pd.json_normalize(data2)
    df2["source"] = "MAIL_FOR_ME"
    df3 = pd.json_normalize(data3)
    df3["source"] = "PRINT"

    # Concatenate dataframes
    df = pd.concat([df1, df2, df3], ignore_index=True)

    print(df.head())

    # Save to CSV
    output_path = os.path.join(output_dir, "statement_submission.csv")
    df.to_csv(output_path, index=False)
    print(f"Statement Submission Report saved to {output_path}")

def fetch_billing_statement_report(client, output_dir):
    url = "https://live6.dentrixascend.com/billingStatements"
    pass

def fetch_integrated_payments_report(client, output_dir):
    url = "https://live6.dentrixascend.com/integratedPaymentReport"
    params = {
        "order": "desc",
        "field": "transactionDateTime",
        "locationIds": "14000000000286",
        "from": "1",
        "rows": "10000",
        "cardPaymentAccountId": "1413596",
        "transactionDateTimeFrom": "0",
        "transactionDateTimeTo": "9999999999999"
    }

    data = client.make_request(url, method="GET", params=params)["data"]
    df = pd.json_normalize(data)
    
    print(df.head())

    # Save to CSV
    output_path = os.path.join(output_dir, "integrated_payments_report.csv")
    df.to_csv(output_path, index=False)
        
    print(f"Integrated Payments Report saved to {output_path}")
    

def fetch_outstanding_claims_report(client, output_dir):
    url = "https://live6.dentrixascend.com/statementSubmissionReport"
    pass

def fetch_unresolved_claims_report(client, output_dir):
    url = "https://live6.dentrixascend.com/statementSubmissionReport"
    pass