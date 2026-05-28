"""
Naukri Headline + About Updater - Cookie based
"""

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from datetime import date
import os, time, sys

load_dotenv()

# ── Config ───────────────────────────────────────────────────
HEADLESS = os.environ.get("HEADLESS", "true").lower() == "true"

NAUKRI_COOKIES = [
    {"name": "nauk_at",  "value": os.environ.get("NAUK_AT",  ""), "domain": ".naukri.com", "path": "/"},
    {"name": "nauk_sid", "value": os.environ.get("NAUK_SID", ""), "domain": ".naukri.com", "path": "/"},
    {"name": "nauk_rt",  "value": os.environ.get("NAUK_RT",  ""), "domain": ".naukri.com", "path": "/"},
    {"name": "is_login", "value": "1",                            "domain": ".naukri.com", "path": "/"},
]


def load_headlines():
    raw = os.environ.get("NAUKRI_HEADLINES", "").strip()
    if raw:
        return [h.strip() for h in raw.split("||") if h.strip()]
    return [
        "Full Stack Dev | Angular | Java 17 | Spring Boot",
        "TypeScript | REST APIs | Microservices | Agile",
        "Java Developer | WebSockets | RxJS | CI/CD",
        "Full Stack Engineer | Healthcare IT | Enterprise Apps",
        "Angular + Java | Microservices | Real-time Features",
        "Software Engineer | Spring Boot | Agile | Healthcare",
        "Full Stack Dev | TypeScript | Java 17 | WebSockets",
    ]


def load_about():
    raw = os.environ.get("NAUKRI_ABOUT", "").strip()
    if raw:
        return [a.strip() for a in raw.split("||") if a.strip()]
    return [
        "Full Stack Developer | 2+ yrs React.js, Node.js, REST APIs & CI/CD. 20-30% performance improvement. Agile, Docker, Kubernetes, PostgreSQL.",
        "React.js & Node.js Developer | End-to-end ownership from design to production. PostgreSQL, Docker, Kubernetes. Agile & SAFe. 20-30% perf boost.",
        "Full Stack Engineer | 2+ years building responsive frontends & scalable backends. React.js, Redux, Node.js, REST APIs, CI/CD, GitHub Copilot.",
        "Results-driven Full Stack Developer | React.js, Node.js, PostgreSQL, Docker. 20-30% performance gains. End-to-end ownership in Agile/SAFe.",
        "Frontend-leaning Full Stack Dev | React.js, Redux, JavaScript expert. Node.js & REST APIs backend. CI/CD, Docker, Kubernetes. Strong Agile skills.",
        "Performance-focused Full Stack Dev | 2+ yrs React.js & Node.js. 20-30% app improvement. PostgreSQL, Docker, CI/CD, GitHub Copilot, Agile.",
        "Full Stack Developer | React.js | Node.js | Docker | Kubernetes | 2+ years delivering scalable production-grade apps. Agile, REST APIs, CI/CD.",
    ]


HEADLINES = load_headlines()
ABOUTS    = load_about()
TODAY_IDX = date.today().weekday()
HEADLINE  = HEADLINES[TODAY_IDX % len(HEADLINES)]
ABOUT     = ABOUTS[TODAY_IDX % len(ABOUTS)]
# ─────────────────────────────────────────────────────────────


def log(msg):
    print(f"[naukri] {msg}")


def go_to_profile(page):
    log("Going to profile page...")
    page.goto("https://www.naukri.com/mnjuser/profile", wait_until="domcontentloaded")
    time.sleep(2)  # reduced from 3


def fill_input(page, text, screenshot_name, selector_hint=None):
    """Fill a specific textarea."""
    input_el = None

    selectors = []
    if selector_hint:
        selectors.append(selector_hint)

    selectors += [
        "textarea#profileSummary",
        "textarea[name='profileSummary']",
        "textarea[placeholder*='summary' i]",
        "textarea[placeholder*='profile' i]",
        "textarea#resumeHeadline",
        "textarea[name='resumeHeadline']",
        "textarea[placeholder*='headline' i]",
        "[contenteditable='true']",
        "textarea",
    ]

    for sel in selectors:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=3000)
            input_el = loc
            log(f"Found input: {sel}")
            break
        except Exception:
            continue

    if input_el is None:
        log(f"Could not find input. Saving {screenshot_name}...")
        page.screenshot(path=screenshot_name)
        return False

    input_el.click()
    input_el.press("Control+a")
    input_el.press("Delete")
    time.sleep(0.5)
    input_el.fill(text)   # ← fill() instead of type() — instant, no timeout
    time.sleep(1)
    return True

def click_save(page, screenshot_name):
    """Try multiple Save button selectors."""
    for sel in [
        "button:has-text('Save')",
        ".modal button:has-text('Save')",
        "div[role='dialog'] button:has-text('Save')",
        "xpath=//button[normalize-space(text())='Save']",
        "xpath=//div[contains(@class,'modal')]//button[contains(text(),'Save')]",
        "button.saveBtn",
        "button[type='submit']",
    ]:
        try:
            page.locator(sel).first.click(timeout=3000)
            time.sleep(2)
            log(f"Clicked Save with: {sel}")
            return True
        except Exception:
            continue

    log(f"Could not click Save. Saving {screenshot_name}...")
    page.screenshot(path=screenshot_name)
    return False


def close_success_popup(page):
    for sel in [
        ".profileUpdatedProLayer > div:nth-child(1) > span:nth-child(1)",
        "button[aria-label='Close']",
        "span[aria-label='Close']",
        "[class*='crossIcon']",
        "[class*='closeIcon']",
        "[class*='closeBtn']",
        "button:has-text('Close')",
        "button:has-text('OK')",
    ]:
        try:
            if sel.startswith("//"):
                btn = page.locator(f"xpath={sel}").first
            else:
                btn = page.locator(sel).first
            btn.wait_for(state="visible", timeout=1500)  # reduced from 3000
            btn.click(timeout=1500)
            log(f"Closed popup with: {sel}")
            time.sleep(0.5)  # reduced from 1
            return True
        except Exception:
            continue

    try:
        page.keyboard.press("Escape")
        log("Closed popup with Escape")
        time.sleep(0.5)
        return True
    except Exception:
        pass

    return False

def update_headline(page):
    log("Looking for Resume Headline edit button...")
    for sel in [
        "xpath=//div[contains(@class,'resumeHeadline')]//span[contains(@class,'edit')]",
        "xpath=//div[contains(text(),'Resume Headline')]/..//span[contains(@class,'edit')]",
        "div.resumeHeadline .editIcon",
        "div.resumeHeadline .edit",
    ]:
        try:
            page.locator(sel).first.click(timeout=3000)
            log(f"Clicked headline edit: {sel}")
            break
        except Exception:
            continue

    time.sleep(2)

    if not fill_input(page, HEADLINE, "debug_headline.png"):
        sys.exit(1)

    if not click_save(page, "debug_headline.png"):
        sys.exit(1)

    log(f'✅ Headline updated: "{HEADLINE}"')

    time.sleep(2)
    closed = close_success_popup(page)
    if closed:
        log("Popup closed — moving to About update...")
    else:
        log("No popup found or already dismissed — continuing to About...")
    time.sleep(1)


def update_about(page):
    log("Looking for Profile Summary edit button...")

    try:
        page.evaluate("window.scrollBy(0, 600)")
        time.sleep(0.5)  # reduced from 1
    except Exception:
        pass

    for sel in [
        "xpath=//div[contains(@class,'profileSummary')]//span[contains(@class,'edit')]",
        "xpath=//div[contains(@class,'profileSummary')]//span[contains(@class,'editIcon')]",
        "xpath=//div[contains(text(),'Profile summary')]/..//span[contains(@class,'edit')]",
        "xpath=//section[contains(@class,'profileSummary')]//span[contains(@class,'edit')]",
        "xpath=//h2[contains(text(),'Profile summary')]/..//span[contains(@class,'edit')]",
        "div.profileSummary .editIcon",
        "div.profileSummary .edit",
        "div.profileSummary span.edit",
    ]:
        try:
            page.locator(sel).first.click(timeout=3000)
            log(f"Clicked profile summary edit: {sel}")
            break
        except Exception:
            continue

    time.sleep(1)  # reduced from 2

    input_el = None
    for sel in [
        "textarea#profileSummaryTxt",  # ← exact id from your error log
        "textarea#profileSummary",
        "textarea[name='profileSummary']",
        "textarea[placeholder*='summary' i]",
        "div.profileSummary textarea",
        "textarea",
    ]:
        try:
            loc = page.locator(sel).first
            loc.wait_for(state="visible", timeout=3000)
            input_el = loc
            log(f"Found profile summary input: {sel}")
            break
        except Exception:
            continue

    if input_el is None:
        log("Could not find Profile Summary textarea. Skipping...")
        page.screenshot(path="debug_about.png")
        return

    input_el.click()
    input_el.fill("")    # clear instantly
    input_el.fill(ABOUT) # fill instantly
    time.sleep(0.5)

    if not click_save(page, "debug_about.png"):
        log("Skipping profile summary save...")
        return

    time.sleep(1)  # reduced from 2
    close_success_popup(page)

    log(f'✅ Profile Summary updated: "{ABOUT[:60]}..."')
        
def run():
    missing = [c["name"] for c in NAUKRI_COOKIES if not c["value"] and c["name"] != "is_login"]
    if missing:
        log(f"ERROR: Missing cookies: {', '.join(missing)}")
        sys.exit(1)

    with sync_playwright() as p:
        log("Launching browser...")
        browser = p.firefox.launch(headless=HEADLESS)
        context = browser.new_context(
            viewport={"width": 1366, "height": 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
            locale="en-IN",
            timezone_id="Asia/Kolkata",
        )
        context.add_cookies(NAUKRI_COOKIES)
        page = context.new_page()

        try:
            go_to_profile(page)
            update_headline(page)
            update_about(page)
        except Exception as e:
            log(f"Unexpected error: {e}")
            page.screenshot(path="debug_screenshot.png")
            raise
        finally:
            browser.close()

    log("Done!")


if __name__ == "__main__":
    run()