"""
Configuration — load credentials from environment variables whenever possible.
"""

import os

# Your Naukri login credentials.
# For security, avoid committing real credentials to source control.
EMAIL = os.environ.get("NAUKRI_EMAIL", "")
PASSWORD = os.environ.get("NAUKRI_PASSWORD", "")

# The headline to set on your profile.
HEADLINE = os.environ.get(
    "NAUKRI_HEADLINE",
    "Software Engineer | Python | Django | 5 Years Experience",
)

# Run browser in headless mode by default when NAUKRI_HEADLESS is set to 1/true/yes.
HEADLESS = os.environ.get("NAUKRI_HEADLESS", "False").strip().lower() in ("1", "true", "yes")

# Optional resume path for upload scripts.
RESUME_PATH = os.environ.get("NAUKRI_RESUME_PATH", "Shubham_Kakhekar.pdf")

if not EMAIL or not PASSWORD:
    raise ValueError(
        "NAUKRI_EMAIL and NAUKRI_PASSWORD must be set in environment variables or config.py"
    )
