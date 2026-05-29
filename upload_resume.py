"""
Naukri Resume Uploader - Cookie based (no login needed)

This script is optional and is designed to use environment variables for all sensitive values.
Never commit active session cookies or login credentials into source control.
"""

from playwright.sync_api import sync_playwright
import os
import shutil
from datetime import datetime
import time
import sys

# ── Config ──────────────────────────────────────────────────
ORIGINAL_RESUME = os.environ.get("NAUKRI_ORIGINAL_RESUME", "resume.pdf")
HEADLESS = os.environ.get("NAUKRI_HEADLESS", "True").strip().lower() in ("1", "true", "yes")

NAUKRI_COOKIES = [
    {
        "name": "nauk_at",
        "value": os.environ.get("NAUK_AT", ""),
        "domain": ".naukri.com",
        "path": "/",
    },
    {
        "name": "nauk_sid",
        "value": os.environ.get("NAUK_SID", ""),
        "domain": ".naukri.com",
        "path": "/",
    },
    {
        "name": "nauk_rt",
        "value": os.environ.get("NAUK_RT", ""),
        "domain": ".naukri.com",
        "path": "/",
    },
    {
        "name": "is_login",
        "value": "1",
        "domain": ".naukri.com",
        "path": "/",
    },
]
# ────────────────────────────────────────────────────────────


def log(msg):
    print(f"[naukri] {msg}")


def rename_resume(original_path):
    if not os.path.exists(original_path):
        log(f"ERROR: '{original_path}' not found.")
        sys.exit(1)

    your_name = os.environ.get("YOUR_NAME", "resume").strip().lower().replace(" ", "_")
    ext = os.path.splitext(original_path)[1]
    today = datetime.today().strftime("%d_%m_%Y")
    new_name = f"{your_name}_{today}{ext}"
    new_path = os.path.join(os.path.dirname(os.path.abspath(original_path)), new_name)

    shutil.copy2(original_path, new_path)
    log(f"Renamed → {new_name}")
    return new_path


def upload_resume(page, resume_path):
    log("Going to profile page...")
    page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded")
    time.sleep(3)

    log("Looking for resume upload input...")
    upload_btn_selectors = [
        "text=Update Resume",
        "text=Upload Resume",
        "label[for='attachCV']",
        "div.resumeAttach .edit",
        "//div[contains(text(),'Resume')]/..//span[contains(@class,'edit')]",
    ]
    for sel in upload_btn_selectors:
        try:
            if sel.startswith("//"):
                page.locator(f"xpath={sel}").first.click(timeout=3000)
            else:
                page.locator(sel).first.click(timeout=3000)
            log(f"Clicked upload button: {sel}")
            time.sleep(1)
            break
        except Exception:
            continue

    file_input_selectors = [
        "input#attachCV",
        "input[type='file'][name='attachCV']",
        "input[type='file']",
    ]
    uploaded = False
    for sel in file_input_selectors:
        try:
            file_input = page.locator(sel).first
            file_input.wait_for(state="attached", timeout=5000)
            file_input.set_input_files(resume_path)
            uploaded = True
            log(f"File set via: {sel}")
            break
        except Exception:
            continue

    if not uploaded:
        log("Could not find file input. Saving debug_screenshot.png ...")
        page.screenshot(path="debug_screenshot.png")
        sys.exit(1)

    time.sleep(3)
    try:
        page.locator("button:has-text('Save')").first.click(timeout=4000)
        time.sleep(2)
    except Exception:
        pass

    log(f"✅ Resume uploaded: {os.path.basename(resume_path)}")


def run():
    missing = [cookie["name"] for cookie in NAUKRI_COOKIES if not cookie["value"] and cookie["name"] != "is_login"]
    if missing:
        raise ValueError(
            f"Missing cookie values for: {', '.join(missing)}. "
            "Set them through environment variables and do not commit secret values."
        )

    resume_path = rename_resume(ORIGINAL_RESUME)

    with sync_playwright() as p:
        log("Launching browser...")
        browser = p.firefox.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) "
                "Gecko/20100101 Firefox/124.0"
            ),
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )

        context.add_cookies(NAUKRI_COOKIES)
        page = context.new_page()

        try:
            upload_resume(page, resume_path)
        except Exception as e:
            log(f"Unexpected error: {e}")
            page.screenshot(path="debug_screenshot.png")
            raise
        finally:
            browser.close()

    log("Done!")


if __name__ == "__main__":
    run()