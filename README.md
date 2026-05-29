# Naukri Profile Auto-Updater by @Kakhekar

Automatically logs into Naukri using session cookies and updates your **Resume Headline**, **Profile Summary**, and **Resume file** to keep your profile active and visible to recruiters.

Runs twice daily via GitHub Actions (7:30 AM and 1:30 PM IST), or locally on demand.

---

## How it works

The scripts use Playwright to drive a Firefox browser session authenticated via Naukri session cookies (no username/password login). Each run:

1. **Uploads your resume** with a date-stamped filename (`resume.py`)
2. **Updates your Resume Headline** with a rotating daily headline (`naukri_updater.py`)
3. **Updates your Profile Summary / About** with a rotating daily blurb (`naukri_updater.py`)

The headline and about text rotate based on the day of the week (Monday = index 0 … Sunday = index 6), keeping your profile looking freshly updated to Naukri's ranking algorithm.

---

## Setup

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

`requirements.txt` currently pulls in `playwright` and `schedule`.  
You will also want `python-dotenv` if running locally with a `.env` file:

```bash
pip install python-dotenv
```

### 2. Install the Firefox browser for Playwright

```bash
playwright install firefox
playwright install-deps firefox
```

### 3. Get your Naukri session cookies

The scripts authenticate via three cookies rather than a username/password login.  
To obtain them:

1. Log into [naukri.com](https://www.naukri.com) in your browser.
2. Open cosole and run
```bash
const cookies = ['nauk_at', 'nauk_sid', 'nauk_rt'];
cookies.forEach(name => {
    const value = document.cookie.split('; ').find(r => r.startsWith(name + '='))?.split('=')[1];
    console.log(`${name}=${value}`);
});
```

These expire periodically — refresh them in your `.env` / GitHub Secrets whenever the script starts failing.

### 4. Configure environment variables

Create a `.env` file in the project root (already in `.gitignore`):

```env
# Session cookies (required)
NAUK_AT=<your nauk_at cookie value>
NAUK_SID=<your nauk_sid cookie value>
NAUK_RT=<your nauk_rt cookie value>

# Browser (optional — default: false for local, true in CI)
HEADLESS=false

# Resume upload (optional — defaults shown)
YOUR_NAME=your_name
RESUME_FILENAME=YourName.pdf

# Custom rotating headlines (optional — || separates each entry)
NAUKRI_HEADLINES=Software Engineer | Python | Django || Backend Engineer | Django | AWS || ...

# Custom rotating about/summary blurbs (optional — || separates each entry)
NAUKRI_ABOUT=First blurb text... || Second blurb text... || ...
```

If `NAUKRI_HEADLINES` or `NAUKRI_ABOUT` are not set, the scripts fall back to built-in 7-day rotation defaults.

---

## Running locally

### Update headline and profile summary once

```bash
python naukri_updater.py
```

### Upload resume once

```bash
python upload_resume.py
```

### Run on a repeating schedule (every 24 hours)

```bash
python scheduler.py
```

Change `INTERVAL_HOURS` in `scheduler.py` to adjust frequency. The scheduler runs once immediately on startup, then repeats.

---

## GitHub Actions (automated)

The workflow at `.github/workflows/naukri.yml` runs automatically at **7:30 AM IST** and **1:30 PM IST** every day, and can also be triggered manually via `workflow_dispatch`.

### Required GitHub Secrets

Go to your repo → **Settings → Secrets and variables → Actions** and add:

| Secret | Description |
|---|---|
| `NAUK_AT` | `nauk_at` cookie value |
| `NAUK_SID` | `nauk_sid` cookie value |
| `NAUK_RT` | `nauk_rt` cookie value |
| `NAUKRI_HEADLINES` | `||`-separated headline list (optional) |
| `NAUKRI_ABOUT` | `||`-separated about/summary list (optional) |
| `YOUR_NAME` | Used for the date-stamped resume filename |
| `RESUME_FILENAME` | Original resume PDF filename in the repo |

On each run the workflow uploads debug screenshots as a build artifact so you can inspect failures without re-running locally.

---

## Files

| File | Purpose |
|---|---|
| `naukri_updater.py` | Updates Resume Headline and Profile Summary via session cookies |
| `resume.py` | Uploads a date-stamped copy of your resume |
| `config.py` | Credential and headline parsing helpers (used by legacy flows) |
| `scheduler.py` | Runs the updater repeatedly on a configurable interval |
| `requirements.txt` | Python dependencies |
| `.github/workflows/naukri.yml` | GitHub Actions workflow (twice-daily CI run) |

---

## Troubleshooting

**Script fails immediately with "Missing cookies"**  
→ Check that `NAUK_AT`, `NAUK_SID`, and `NAUK_RT` are set in your `.env` or GitHub Secrets. Cookie values expire — re-copy them from your browser.

**Edit button not found / headline not updating**  
→ Naukri may have changed their UI. Check the `debug_headline.png` or `debug_about.png` screenshot (saved automatically on error) to see what the page looks like, then update the selectors in `naukri_updater.py`.

**Resume upload fails**  
→ Check `debug_screenshot.png`. Confirm the resume file named in `RESUME_FILENAME` (or `NAUKRI_ORIGINAL_RESUME`) exists in the project root.

**OTP / CAPTCHA prompt appears**  
→ This happens on the first run from a new IP. Run locally with `HEADLESS=false` to complete it manually; subsequent runs from the same IP (or GitHub Actions' IP range) are usually fine.

---

## Running on a schedule (local machine)

### Linux / macOS — cron

```bash
crontab -e
# Run every day at 9 AM:
0 9 * * * cd /path/to/naukri-updater && python naukri_updater.py >> naukri.log 2>&1
```
# Naukri-profile-updater
### Windows — Task Scheduler

1. Open Task Scheduler → **Create Basic Task**
2. Trigger: **Daily** at your chosen time
3. Action: `python C:\path\to\naukri-updater\naukri_updater.py`