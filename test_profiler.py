import pandas as pd
from data_profiler import DataProfiler  # Ensure this matches the actual file name and class name

# Load the CSV file into a DataFrame
df = pd.read_csv("C:/Users/Admin/Documents/Career/Juniper/Data/Treatment Tracker - mod.csv")

# Initialize the DataProfiler with the DataFrame
profiler = DataProfiler(df)

# Profile the dataset and columns
profiler.profile_dataset()
profiler.profile_columns()

new_dataset_content = """
### Overview
- **Dataset Purpose**: Analyzing customer trends.
- **Source**: CRM database.
- **Update Frequency**: Weekly.

### Field Descriptions
| Field Name | Description        | Data Type | Example Values |
|------------|--------------------|-----------|----------------|
| CustomerID | Unique identifier  | Integer   | 12345          |

### Summary Statistics
- **Total Rows**: 10,000
- **Total Columns**: 15
"""

append_section("data_guide_project.md", "Dataset 3", new_dataset_content)

def generate_toc(file_path):
    """
    Generate a table of contents for a markdown file.
    
    Args:
        file_path (str): Path to the markdown file.
    """
    toc = []
    with open(file_path, "r") as file:
        for line in file:
            if line.startswith("## "):  # Detect headers
                header = line.strip("#").strip()
                link = header.lower().replace(" ", "-")
                toc.append(f"- [{header}](#{link})")
    
    toc_content = "## Table of Contents\n" + "\n".join(toc) + "\n"
    
    # Insert TOC at the top of the file
    with open(file_path, "r") as file:
        content = file.read()
    
    with open(file_path, "w") as file:
        file.write(toc_content + "\n---\n" + content)

generate_toc("data_guide_project.md")


# Generate and print the Markdown report
markdown_report = profiler.generate_report(format="markdown")
print(markdown_report)

# Optionally, generate and print the HTML report
# html_report = profiler.generate_report(format="html")
# print(html_report)

# Optionally, generate and print the CSV report
# csv_report = profiler.generate_report(format="csv")
# print(csv_report)