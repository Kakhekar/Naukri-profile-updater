"""
Naukri Profile Auto-Updater
Logs into Naukri and updates your resume headline to keep your profile active.
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import time
import sys
from config import EMAIL, PASSWORD, HEADLINE, HEADLESS


def log(msg):
    print(f"[naukri] {msg}")


def login(page):
    log("Opening Naukri...")
    page.goto("https://www.naukri.com/", wait_until="domcontentloaded")
    time.sleep(2)

    try:
        page.click("a[href*='login']", timeout=5000)
    except PlaywrightTimeout:
        page.goto("https://www.naukri.com/nlogin/login")

    time.sleep(2)

    log("Filling login form...")
    page.fill("input[placeholder='Enter your active Email ID / Username']", EMAIL)
    page.fill("input[placeholder='Enter your password']", PASSWORD)
    page.click("button[type='submit']")
    time.sleep(4)

    if "nlogin" in page.url or "login" in page.url:
        log("ERROR: Login failed. Check credentials in config.py")
        sys.exit(1)

    log("Login successful!")


def update_headline(page):
    log("Going to profile page...")
    page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded")
    time.sleep(3)

    log("Looking for Resume Headline edit button...")
    clicked = False
    edit_selectors = [
        "//div[contains(@class,'resumeHeadline')]//span[contains(@class,'edit')]",
        "//div[contains(text(),'Resume Headline')]/..//span[contains(@class,'edit')]",
        "div.resumeHeadline .editIcon",
        "div.resumeHeadline .edit",
        "div.widgetHead .edit",
    ]
    for sel in edit_selectors:
        try:
            if sel.startswith("//"):
                page.locator(f"xpath={sel}").first.click(timeout=3000)
            else:
                page.locator(sel).first.click(timeout=3000)
            clicked = True
            log(f"Clicked edit with: {sel}")
            break
        except Exception:
            continue

    if not clicked:
        try:
            page.get_by_text("Resume Headline").locator("..").get_by_role("button").click(timeout=5000)
            clicked = True
        except Exception:
            pass

    if not clicked:
        log("Could not find edit button. Saving debug_screenshot.png ...")
        page.screenshot(path="debug_screenshot.png")
        sys.exit(1)

    time.sleep(2)

    log("Finding headline textarea...")
    textarea = None
    textarea_selectors = [
        "textarea#resumeHeadline",
        "textarea[name='resumeHeadline']",
        "textarea[placeholder*='headline' i]",
        "textarea[placeholder*='Headline']",
        "div.resumeHeadline textarea",
        "textarea",
    ]
    for sel in textarea_selectors:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=3000)
            textarea = loc
            log(f"Found textarea with: {sel}")
            break
        except Exception:
            continue

    if textarea is None:
        log("Could not find textarea. Saving debug_screenshot.png ...")
        page.screenshot(path="debug_screenshot.png")
        sys.exit(1)

    log("Updating headline text...")
    textarea.click()
    textarea.fill("")
    textarea.fill(HEADLINE)
    time.sleep(1)

    log("Saving...")
    try:
        page.locator("button:has-text('Save')").first.click(timeout=5000)
    except Exception:
        try:
            page.locator("input[value='Save']").first.click(timeout=5000)
        except Exception:
            log("Could not find Save button. Saving debug_screenshot.png ...")
            page.screenshot(path="debug_screenshot.png")
            sys.exit(1)

    time.sleep(3)
    log(f'Headline updated to: "{HEADLINE}"')


def run():
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
            update_headline(page)
        except Exception as e:
            log(f"Unexpected error: {e}")
            page.screenshot(path="debug_screenshot.png")
            raise
        finally:
            browser.close()

    log("Done. Browser closed.")


if __name__ == "__main__":
    run()