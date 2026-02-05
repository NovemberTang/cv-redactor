# cv-redactor

A Python tool for redacting personally identifiable information (PII) from PDF documents such as CVs/resumes.

## Features

- Identifies and redacts PII including:
  - Names (PERSON)
  - Email addresses (EMAIL_ADDRESS)
  - Phone numbers (PHONE_NUMBER)
  - Locations (LOCATION)
  - URLs (URL)
- Creates a new redacted PDF with sensitive information redacted
- Web-based frontend for easy PDF upload and download

## Installation

```bash
uv pip install -r requirements.txt
```

## Usage

### Using the Web Frontend

Run the Streamlit frontend:
```bash
streamlit run frontend.py
```

Then open your browser to the URL shown (typically http://localhost:8501), upload a PDF, and click "Redact PII" to process it.

### Using the Command Line

Run the command-line version:
```bash
uv run main.py
```

## Example

Input PDF contains:
```
Sarah Chen
sarah.chen@emailprovider.com
020 7372 5330
London, England
```

Output PDF shows:
```
[NAME]
[EMAIL]
020 7372 5330
[LOCATION], [LOCATION]
```
