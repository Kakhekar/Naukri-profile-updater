"""
Naukri Resume Uploader
- Renames your resume to shubham_kakhekar_DD-MM-YYYY.pdf
- Uploads it to your Naukri profile
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import os
import shutil
from datetime import datetime
import time
import sys

# ── Config ──────────────────────────────────────────────────
EMAIL           = os.environ.get("NAUKRI_EMAIL", "your_email@example.com")
PASSWORD        = os.environ.get("NAUKRI_PASSWORD", "your_password")
ORIGINAL_RESUME = "Shubham_Kakhekar.pdf"
HEADLESS        = True          # ← was `true` (JavaScript), Python needs capital T
# ────────────────────────────────────────────────────────────


def log(msg):
    print(f"[naukri] {msg}")


def rename_resume(original_path):
    if not os.path.exists(original_path):
        log(f"ERROR: '{original_path}' not found.")
        sys.exit(1)

    ext = os.path.splitext(original_path)[1]
    today = datetime.today().strftime("%d-%m-%Y")
    new_name = f"shubham_kakhekar_{today}{ext}"
    new_path = os.path.join(os.path.dirname(os.path.abspath(original_path)), new_name)

    shutil.copy2(original_path, new_path)
    log(f"Renamed → {new_name}")
    return new_path


def login(page):
    log("Opening Naukri...")
    page.goto("https://www.naukri.com/", wait_until="domcontentloaded")
    time.sleep(2)

    try:
        page.click("a[href*='login']", timeout=5000)
    except PlaywrightTimeout:
        page.goto("https://www.naukri.com/nlogin/login")

    time.sleep(2)

    log("Logging in...")
    page.fill("input[placeholder='Enter your active Email ID / Username']", EMAIL)
    page.fill("input[placeholder='Enter your password']", PASSWORD)
    page.click("button[type='submit']")
    time.sleep(4)

    if "nlogin" in page.url or "login" in page.url:
        log("ERROR: Login failed. Check your credentials.")
        sys.exit(1)

    log("Login successful!")


def upload_resume(page, resume_path):
    log("Going to profile page...")
    page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded")
    time.sleep(3)

    log("Looking for resume upload input...")

    # Try clicking the Update Resume / upload button first
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

    # Set the file on the file input directly
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

    # Confirm/Save if dialog appears
    try:
        page.locator("button:has-text('Save')").first.click(timeout=4000)
        time.sleep(2)
    except Exception:
        pass  # some flows auto-save after file selection

    log(f"Resume uploaded: {os.path.basename(resume_path)}")


def run():
    resume_path = rename_resume(ORIGINAL_RESUME)

    with sync_playwright() as p:
        log("Launching browser...")
        browser = p.chromium.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        try:
            login(page)
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