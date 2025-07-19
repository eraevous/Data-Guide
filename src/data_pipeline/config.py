import os

# Default input and output directories
INPUT_DIR = "input"
OUTPUT_DIR = "output"

# Mapping of dataset names to CSV file names relative to INPUT_DIR
CSV_FILES = {
    "aged_AR": "aged_ar_report.csv",
    "statement_submission": "statement_submission_report.csv",
    "integrated_payments": "integrated_payments_report.csv",
    "outstanding_claims": "outstanding_claims_report.csv",
    "unresolved_claims": "unresolved_claims_report.csv",
    "patient_list": "ZR - Patient List with Details.csv",
    "processed_payments": "ZR - Credit Card Processed Payments.csv",
    "transaction_details": "ZR - Transaction Detail.csv",
    "treatment_tracker": "ZR - Treatment Tracker.csv",
}

# Custom data type hints for each dataset
CUSTOM_TYPES = {
    "aged_AR": {
        "id": "id",
        "phoneNumber": "phone_number",
        "billingStatement": "id",
        "lastPayment.datedAs": "unix_timestamp",
    },
    "statement_submission": {
        "id": "id",
        "dateTime": "unix_timestamp",
        "patient.id": "id",
    },
    "patient_list": {
        "Ascend Patient ID": "id",
        "Phone": "phone_number",
        "Date Of Birth": "date",
        "Prim. Subscriber ID": "id",
        "Address": "address",
        "Email": "email",
        "First Visit": "date",
        "Last Visit": "date",
        "Last Procedure Date": "date",
        "Next Appointment Date": "date",
    },
    "processed_payments": {
        "Date (Modified)": "date",
        "Amount": "currency",
        "Ascend Patient ID": "id",
    },
    "transaction_details": {
        "Date": "date",
        "Ascend Patient ID": "id",
        "Charges": "currency",
        "Credits": "currency",
    },
    "treatment_tracker": {
        "Ascend Patient ID": "id",
        "Date": "date",
        "Amount Presented": "currency",
    },
    "outstanding_claims": {
        "id": "id",
        "createdDate": "unix_timestamp",
        "subscriberNumber": "id",
        "serviceDate": "unix_timestamp",
        "insuranceCarrier.phoneNumber": "phone_number",
        "insuranceCarrier.phoneExtension": "skip",
        "insuranceCarrier.website": "url",
        "subscriber.id": "id",
        "patient.id": "id",
        "groupPlan.phoneNumber": "phone_number",
        "groupPlan.phoneExtension": "skip",
        "subscriber.dateOfBirth": "unix_timestamp",
        "patient.dateOfBirth": "unix_timestamp",
    },
    "unresolved_claims": {
        "claimId": "id",
        "carrierId": "id",
        "patientId": "id",
    },
    "integrated_payments": {
        "id": "id",
        "transactionDateTime": "unix_timestamp",
        "transactionId": "id",
    },
}

def get_csv_paths(input_dir: str = INPUT_DIR) -> dict:
    """Return dataset paths joined with the provided input directory."""
    return {name: os.path.join(input_dir, fname) for name, fname in CSV_FILES.items()}
