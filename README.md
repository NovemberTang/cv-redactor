# cv-redactor

A Python tool for redacting personally identifiable information (PII) from PDF documents such as CVs/resumes.

## Features

- Identifies and redacts PII including:
  - Names (PERSON)
  - Email addresses (EMAIL_ADDRESS)
  - Phone numbers (PHONE_NUMBER)
  - Locations (LOCATION)
  - URLs (URL)
- Creates a new redacted PDF with sensitive information redacted`

## Installation

```bash
uv pip install -r requirements.txt
```

## Usage

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
