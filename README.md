# cv-redactor

A Python tool for redacting personally identifiable information (PII) from PDF documents such as CVs/resumes.

## Features

- Extracts text from PDF files
- Identifies and redacts PII including:
  - Names (PERSON)
  - Email addresses (EMAIL_ADDRESS)
  - Phone numbers (PHONE_NUMBER)
  - Locations (LOCATION)
  - URLs (URL)
- Creates a new redacted PDF with sensitive information replaced by placeholders

## Requirements

- Python 3.8+
- Dependencies listed in `requirements.txt`

## Installation

```bash
pip install -r requirements.txt
```

## Usage

The tool processes a PDF file and creates a redacted version:

```bash
python main.py
```

By default, it processes `test-resources/cv.pdf` and outputs `test-resources/cv_redacted.pdf`.

## How It Works

1. Opens the input PDF file
2. Extracts text content from all pages
3. Uses Microsoft Presidio to analyze and identify PII entities
4. Replaces identified PII with placeholder tags (e.g., [NAME], [EMAIL])
5. Creates a new PDF with the redacted text

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

## Libraries Used

- **PyMuPDF (fitz)**: PDF reading and writing
- **Presidio Analyzer**: PII detection
- **Presidio Anonymizer**: Text redaction
- **ReportLab**: PDF generation support