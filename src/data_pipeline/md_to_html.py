import sys
import markdown
from pathlib import Path

def convert_md_to_html(directory):
    """Recursively converts all Markdown (.md) files in a directory and subdirectories to HTML files."""
    
    directory = Path(directory).resolve()

    if not directory.exists() or not directory.is_dir():
        print(f"Error: Directory '{directory}' does not exist or is not a valid directory.")
        return

    for md_file in directory.rglob("*.md"):  # Recursively find all .md files
        html_file = md_file.with_suffix(".html")  # Replace .md with .html

        # Try reading the file in UTF-8, fallback to Windows-1252
        try:
            with md_file.open("r", encoding="utf-8") as file:
                md_content = file.read()
        except UnicodeDecodeError:
            print(f"Warning: Could not decode '{md_file}'. Trying Windows-1252...")
            with md_file.open("r", encoding="windows-1252", errors="replace") as file:
                md_content = file.read()

        # Convert Markdown to HTML
        html_content = markdown.markdown(md_content)

        with html_file.open("w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"Converted: '{md_file.relative_to(directory)}' -> '{html_file.relative_to(directory)}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:  # Ensures directory argument is provided
        print("Usage: python md_to_html.py <directory>")
        sys.exit(1)

    directory = sys.argv[1]
    convert_md_to_html(directory)
