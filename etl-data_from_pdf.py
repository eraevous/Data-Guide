# Import necessary libraries
import pdfplumber
import pandas as pd
import json
import re

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    """Extracts raw text from a PDF file."""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
    return text

# Function to parse text and extract key fields
def parse_pdf_text(raw_text):
    """Parses raw text to extract client information, due date, and line items."""
    data = {}
    # Example regex patterns (adjust based on your PDF format)
    data["client_name"] = re.search(r"Client Name:\s*(.*)", raw_text).group(1).strip()
    data["due_date"] = re.search(r"Due Date:\s*(.*)", raw_text).group(1).strip()
    # Extract line items (assuming a table-like structure in the text)
    line_items = []
    for match in re.finditer(r"Item Code:\s*(\w+)\s*Description:\s*(.*)\s*Qty:\s*(\d+)\s*Price:\s*([\d.]+)", raw_text):
        line_items.append({
            "item_code": match.group(1),
            "description": match.group(2),
            "quantity": int(match.group(3)),
            "price": float(match.group(4))
        })
    data["line_items"] = line_items
    return data

# Function to save structured data as JSON or CSV
def save_data(data, output_path, file_format="json"):
    """Saves parsed data into JSON or CSV format."""
    if file_format == "json":
        with open(output_path, "w") as json_file:
            json.dump(data, json_file, indent=4)
    elif file_format == "csv":
        df = pd.DataFrame(data["line_items"])
        df.to_csv(output_path, index=False)

# Main program logic
if __name__ == "__main__":
    pdf_path = "input.pdf"  # Path to the input PDF
    output_path = "output.json"  # Path to save the output file
    file_format = "json"  # Desired output format: "json" or "csv"

    # Step 1: Extract text
    raw_text = extract_text_from_pdf(pdf_path)

    # Step 2: Parse text
    parsed_data = parse_pdf_text(raw_text)

    # Step 3: Save structured data
    save_data(parsed_data, output_path, file_format)

    print(f"Data saved to {output_path} in {file_format} format.")