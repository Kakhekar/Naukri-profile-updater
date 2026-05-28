"""
Configuration — load credentials from environment variables whenever possible.
Configuration — load credentials from environment variables whenever possible.
"""

import json
import os
from datetime import date

# Your Naukri login credentials.
# For security, avoid committing real credentials to source control.
EMAIL = os.environ.get("NAUKRI_EMAIL", "")
PASSWORD = os.environ.get("NAUKRI_PASSWORD", "")

# If you want a daily rotating headline, set NAUKRI_HEADLINES to a JSON list,
# a pipe-separated string, or a multi-line list in the environment.
# Example (Windows CMD):
# set NAUKRI_HEADLINES=["Software Engineer...","Backend Engineer...",...]
# Example (PowerShell):
# $env:NAUKRI_HEADLINES = '["Software Engineer...","Backend Engineer...",...]'

def parse_headlines(raw_value):
    raw = (raw_value or "").strip()
    if not raw:
        return []

    try:
        parsed = json.loads(raw)
        if isinstance(parsed, list) and all(isinstance(item, str) for item in parsed):
            return [item.strip() for item in parsed if item.strip()]
    except ValueError:
        pass

    lines = [line.strip() for line in raw.replace("\r", "").splitlines() if line.strip()]
    if len(lines) > 1:
        return lines

    parts = [part.strip() for part in raw.split("|") if part.strip()]
    return parts or [raw]

HEADLINES = parse_headlines(os.environ.get("NAUKRI_HEADLINES", "")) or [
    "Software Engineer | Python | Django | 5 Years Experience",
    "Full Stack Developer | Python | React | REST APIs",
    "Backend Engineer | Django | PostgreSQL | AWS",
    "Python Developer | Automation | Web Scraping",
    "Software Engineer | DevOps | CI/CD | Docker",
    "Technical Lead | Agile | Team Collaboration",
    "Product-focused Python Engineer | Data-Driven Results",
]

override_index = os.environ.get("NAUKRI_HEADLINE_INDEX", "").strip()
if override_index.isdigit():
    index = int(override_index) % len(HEADLINES)
else:
    index = date.today().weekday() % len(HEADLINES)

HEADLINE = HEADLINES[index]

# Run browser in headless mode by default when NAUKRI_HEADLESS is set to 1/true/yes.
HEADLESS = os.environ.get("NAUKRI_HEADLESS", "False").strip().lower() in ("1", "true", "yes")

# Optional resume path for upload scripts.
RESUME_PATH = os.environ.get("NAUKRI_RESUME_PATH", "Shubham_Kakhekar.pdf")

if not EMAIL or not PASSWORD:
    raise ValueError(
        "NAUKRI_EMAIL and NAUKRI_PASSWORD must be set in environment variables or config.py"
    )
