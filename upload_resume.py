"""
Naukri Resume Uploader - Cookie based (no login needed)
"""

from playwright.sync_api import sync_playwright
import os
import shutil
from datetime import datetime
import time
import sys

# ── Config ──────────────────────────────────────────────────
ORIGINAL_RESUME = "Shubham_Kakhekar.pdf"
HEADLESS        = True

NAUKRI_COOKIES = [
    {"name": "nauk_at",  "value": os.environ.get("NAUK_AT",  "eyJraWQiOiIzIiwidHlwIjoiSldUIiwiYWxnIjoiUlM1MTIifQ.eyJkZXZpY2VUeXBlIjoibTBiNSIsInVkX3Jlc0lkIjoyNTAxNTA1NDAsInN1YiI6IjIzMTUwMDcwMiIsInVkX3VzZXJuYW1lIjoiZjE2NTYzOTA4Ny4xOTcxIiwidWRfaXNFbWFpbCI6dHJ1ZSwiaXNzIjoiSW5mb0VkZ2UgSW5kaWEgUHZ0LiBMdGQuIiwidXNlckFnZW50IjoiTW96aWxsYS81LjAgKFdpbmRvd3MgTlQgMTAuMDsgV2luNjQ7IHg2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzE0OC4wLjAuMCBTYWZhcmkvNTM3LjM2IiwiaXBBZHJlc3MiOiIxMDMuODEuMzYuOTgiLCJ1ZF9pc1RlY2hPcHNMb2dpbiI6ZmFsc2UsInVzZXJJZCI6MjMxNTAwNzAyLCJzdWJVc2VyVHlwZSI6IiIsInVzZXJTdGF0ZSI6IkFVVEhFTlRJQ0FURUQiLCJ1ZF9pc1BhaWRDbGllbnQiOmZhbHNlLCJ1ZF9lbWFpbFZlcmlmaWVkIjp0cnVlLCJ1c2VyVHlwZSI6ImpvYnNlZWtlciIsInNlc3Npb25TdGF0VGltZSI6IjIwMjYtMDUtMjRUMjE6NDM6MDQiLCJ1ZF9lbWFpbCI6Imtha2hla2Fyc2h1YmhhbUBnbWFpbC5jb20iLCJ1c2VyUm9sZSI6InVzZXIiLCJleHAiOjE3Nzk2NDc5MjMsInRva2VuVHlwZSI6ImFjY2Vzc1Rva2VuIiwiaWF0IjoxNzc5NjQ0MzIzLCJqdGkiOiIyNTU3MmI1NDViZDk0YmNiOThkNzNiZTZlODQ1NDhjZiIsInBvZElkIjoicHJvZC04NWRiNjlmZDQ4LXFwdDVtIn0.dSf4eTFWPkfyI1lZ2f8i0vJDq7wi1L-7HHfFuRd9VG2uChlVYP9vWwt0tLeErMK38otYYZOQnubU60XZGX9VFVFS9Xk1Ptt146kVRfIZKkwKI83vulGIWKO6-lwgZg3YhXXsFoEAt71ugWjq75JH5F1ChWFa1bi1rJLmeM27wpEuBZTvhxUn6wOepJs_NJGYmXIkNLPew4w6YqHfl4okC7adq1n4KkExrhjax4lqhqoA3L8B8BzyVkyWQp3NhSsTxxNHjkK8FcrWq__NJT6uk48Z47_gau8s7j2iASwB5Q_buXSZiREunUwFEmsZPzIWWaqIkmoOrzwAmybPxv5BfQ"), "domain": ".naukri.com", "path": "/"},
    {"name": "nauk_sid", "value": os.environ.get("NAUK_SID", "25572b545bd94bcb98d73be6e84548cf"), "domain": ".naukri.com", "path": "/"},
    {"name": "nauk_rt",  "value": os.environ.get("NAUK_RT",  "25572b545bd94bcb98d73be6e84548cf"), "domain": ".naukri.com", "path": "/"},
    {"name": "is_login", "value": "1", "domain": ".naukri.com", "path": "/"},
]
# ────────────────────────────────────────────────────────────


def log(msg):
    print(f"[naukri] {msg}")


def rename_resume(original_path):
    if not os.path.exists(original_path):
        log(f"ERROR: '{original_path}' not found.")
        sys.exit(1)

    ext = os.path.splitext(original_path)[1]
    today = datetime.today().strftime("%d_%m_%Y")
    new_name = f"shubham_kakhekar_{today}{ext}"
    new_path = os.path.join(os.path.dirname(os.path.abspath(original_path)), new_name)

    shutil.copy2(original_path, new_path)
    log(f"Renamed → {new_name}")
    return new_path


def upload_resume(page, resume_path):
    log("Going to profile page...")
    page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded")
    time.sleep(3)

    page.screenshot(path="profile_page.png")
    log("Screenshot saved → profile_page.png")

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