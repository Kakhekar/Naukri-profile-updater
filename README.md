# Naukri Profile Auto-Updater by @Kakhekar

Automatically logs into Naukri and updates your Resume Headline to keep your profile active and visible to recruiters.

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Install the Chromium browser for Playwright

```bash
playwright install chromium
```

### 3. Configure credentials

For safety, store your Naukri credentials in environment variables instead of committing them.

```bash
set NAUKRI_EMAIL=your_email@example.com
set NAUKRI_PASSWORD=your_password
set NAUKRI_HEADLINE="Your Updated Headline Here"
set NAUKRI_HEADLESS=False
```

You can also edit `config.py` directly if needed, but avoid storing real passwords in version control.

```python
EMAIL = os.environ.get("NAUKRI_EMAIL", "")
PASSWORD = os.environ.get("NAUKRI_PASSWORD", "")
HEADLINE = os.environ.get("NAUKRI_HEADLINE", "Your Updated Headline Here")
HEADLESS = os.environ.get("NAUKRI_HEADLESS", "False").lower() in ("1", "true", "yes")
```

---

## Running

### Run once manually

```bash
python naukri_updater.py
```

### Run on a schedule (every 24 hours)

```bash
python scheduler.py
```

Change `INTERVAL_HOURS` in `scheduler.py` to adjust frequency.

---

## Files

| File                  | Purpose                                      |
|-----------------------|----------------------------------------------|
| `config.py`           | Your credentials and headline text           |
| `naukri_updater.py`   | Main script — logs in and updates headline   |
| `scheduler.py`        | Runs the updater repeatedly on a schedule    |
| `requirements.txt`    | Python dependencies                          |

---

## Troubleshooting

- **Login fails** → Double-check credentials in `config.py`
- **Edit button not found** → Naukri may have updated their UI. Check `debug_screenshot.png` (auto-saved on error) to see what the page looks like, then update the selectors in `naukri_updater.py`
- **OTP / CAPTCHA** → Run with `HEADLESS = False` first so you can complete it manually; subsequent runs are usually fine

---

## Keep it running on Windows (optional)

Use Task Scheduler to run `scheduler.py` at startup:

1. Open Task Scheduler → Create Basic Task
2. Trigger: At startup
3. Action: `python C:\path\to\scheduler.py`

## Keep it running on Linux/Mac (optional)

Add a cron job:

```bash
crontab -e
# Add this line to run every day at 9am:
0 9 * * * python /path/to/naukri_updater.py
```
# Naukri-profile-updater