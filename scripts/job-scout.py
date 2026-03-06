#!/usr/bin/env python3
"""
Job Scout - ATS job board scanner.

Pulls open roles from Greenhouse, Lever, Ashby, Workable, Recruitee, and
Workday boards for a watchlist of target companies, filters by title/description
keywords, extracts screening signals, deduplicates against previously seen jobs,
and writes a markdown report.

Supported ATS platforms:
  - Greenhouse  (public JSON API, no auth)
  - Lever       (public JSON API, no auth)
  - Ashby       (public JSON API, no auth)
  - Workable    (public widget API, no auth)
  - Recruitee   (public careers site API, no auth)
  - Workday     (hidden JSON API with Playwright fallback)

Usage:
    python3 skills/job-scout/scripts/job-scout.py                  # standard run (ATS + LinkedIn)
    python3 skills/job-scout/scripts/job-scout.py --verbose         # extra logging
    python3 skills/job-scout/scripts/job-scout.py --reset           # clear seen-jobs state
    python3 skills/job-scout/scripts/job-scout.py --company Stripe  # scan a single company (ATS only)
    python3 skills/job-scout/scripts/job-scout.py --dry-run         # fetch and filter, don't update state
    python3 skills/job-scout/scripts/job-scout.py --no-workday      # skip Workday companies (no Playwright needed)
    python3 skills/job-scout/scripts/job-scout.py --no-linkedin     # skip LinkedIn (no BrightData needed)
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import quote

import requests

# Playwright is optional - only needed for Workday companies
PLAYWRIGHT_AVAILABLE = False
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    pass

# ---------------------------------------------------------------------------
# Paths - resolve relative to project root, not script location.
# Works both inside MARVIN and as a standalone skill in any project.
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PROJECT_DIR = SKILL_DIR.parent.parent  # skills/job-scout/scripts -> project root

# Config: skill config dir first, then MARVIN tools dir as fallback
CONFIG_PATH = SKILL_DIR / "config" / "watchlist.json"
FALLBACK_CONFIG_PATH = PROJECT_DIR / "tools" / "job-scout-watchlist.json"

# State and output - directories are created automatically on first run
SEEN_PATH = PROJECT_DIR / "state" / "job-scout-seen.json"
OUTPUT_DIR = PROJECT_DIR / "research" / "output"
JD_DIR = PROJECT_DIR / "content" / "jobs"

# ---------------------------------------------------------------------------
# Globals set after config load
# ---------------------------------------------------------------------------
VERBOSE = False
CONFIG = {}
SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "JobScout/1.0"})

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    if VERBOSE:
        print(f"  [scout] {msg}", file=sys.stderr)


def strip_html(text: str) -> str:
    """Remove HTML tags and decode entities."""
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def slugify(text: str) -> str:
    """Convert text to a filename-safe slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:80]


def archive_jd(job: dict) -> Path:
    """Save the full job description to content/jobs/ for future reference.

    Returns the path to the saved file.
    """
    JD_DIR.mkdir(parents=True, exist_ok=True)
    company_slug = slugify(job["company"])
    title_slug = slugify(job["title"])
    filename = f"{company_slug}-{title_slug}.md"
    filepath = JD_DIR / filename

    today = datetime.now().strftime("%Y-%m-%d")
    description = strip_html(job["description_raw"]) if job.get("description_raw") else job.get("description_text", "")

    content = f"""# {job['company']} - {job['title']}

**URL:** {job['url']}
**Location:** {job['location']}
**ATS:** {job['ats']}
**Archived:** {today}
{f"**Salary:** {job['salary_text']}" if job.get('salary_text') else ""}
{f"**Posted:** {job['posted_at'][:10]}" if job.get('posted_at') else ""}

---

{description}
"""
    with open(filepath, "w") as f:
        f.write(content)

    log(f"Archived JD: {filepath}")
    return filepath


def safe_get(url: str, params: Optional[dict] = None, timeout: int = 30) -> Optional[dict]:
    """GET with error handling. Returns parsed JSON or None."""
    try:
        log(f"GET {url}")
        resp = SESSION.get(url, params=params, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        log(f"ERROR {url}: {exc}")
        return None


# ---------------------------------------------------------------------------
# ATS Fetchers - each returns a list of normalized job dicts
# ---------------------------------------------------------------------------

def normalize_job(
    job_id: str,
    title: str,
    url: str,
    location: str,
    description: str,
    company: str,
    ats: str,
    salary_min: Optional[int] = None,
    salary_max: Optional[int] = None,
    salary_text: str = "",
    posted_at: str = "",
) -> dict:
    return {
        "id": f"{ats}:{company}:{job_id}",
        "title": title.strip(),
        "url": url.strip(),
        "location": location.strip(),
        "description_raw": description,
        "description_text": strip_html(description),
        "company": company,
        "ats": ats,
        "salary_min": salary_min,
        "salary_max": salary_max,
        "salary_text": salary_text,
        "posted_at": posted_at,
    }


def fetch_greenhouse(company: dict) -> Tuple[List[dict], Optional[str]]:
    """Fetch all jobs from a Greenhouse board."""
    token = company["board_token"]
    url = f"https://boards-api.greenhouse.io/v1/boards/{quote(token)}/jobs"
    data = safe_get(url, params={"content": "true"})
    if data is None:
        return [], f"Failed to fetch Greenhouse board '{token}'"
    jobs_raw = data.get("jobs", [])
    jobs = []
    for j in jobs_raw:
        loc_parts = []
        for loc in j.get("location", {}).get("name", "").split(","):
            loc_parts.append(loc.strip())
        location = ", ".join(loc_parts) if loc_parts else "Unknown"

        desc = j.get("content", "") or ""
        posted = j.get("updated_at", "") or j.get("first_published_at", "")

        jobs.append(normalize_job(
            job_id=str(j.get("id", "")),
            title=j.get("title", ""),
            url=j.get("absolute_url", ""),
            location=location,
            description=desc,
            company=company["name"],
            ats="greenhouse",
            posted_at=posted,
        ))
    return jobs, None


def fetch_lever(company: dict) -> Tuple[List[dict], Optional[str]]:
    """Fetch all jobs from a Lever postings API."""
    token = company["board_token"]
    url = f"https://api.lever.co/v0/postings/{quote(token)}"
    data = safe_get(url)
    if data is None:
        return [], f"Failed to fetch Lever board '{token}'"
    if not isinstance(data, list):
        return [], f"Unexpected Lever response for '{token}'"
    jobs = []
    for j in data:
        loc = j.get("categories", {}).get("location", "Unknown")
        desc = j.get("descriptionPlain", "") or strip_html(j.get("description", "") or "")

        sal_min = None
        sal_max = None
        sal_text = ""
        comp = j.get("salaryRange", {})
        if comp:
            sal_min = comp.get("min")
            sal_max = comp.get("max")
            currency = comp.get("currency", "USD")
            if sal_min and sal_max:
                sal_text = f"{currency} {sal_min:,}-{sal_max:,}"

        posted = j.get("createdAt", "")
        if isinstance(posted, int):
            posted = datetime.fromtimestamp(posted / 1000, tz=timezone.utc).isoformat()

        jobs.append(normalize_job(
            job_id=str(j.get("id", "")),
            title=j.get("text", ""),
            url=j.get("hostedUrl", ""),
            location=loc,
            description=desc,
            company=company["name"],
            ats="lever",
            salary_min=sal_min,
            salary_max=sal_max,
            salary_text=sal_text,
            posted_at=str(posted),
        ))
    return jobs, None


def fetch_ashby(company: dict) -> Tuple[List[dict], Optional[str]]:
    """Fetch all jobs from an Ashby job board API."""
    token = company["board_token"]
    url = f"https://api.ashbyhq.com/posting-api/job-board/{quote(token)}"
    data = safe_get(url, params={"includeCompensation": "true"})
    if data is None:
        return [], f"Failed to fetch Ashby board '{token}'"

    jobs_raw = data.get("jobs", [])
    jobs = []
    for j in jobs_raw:
        loc = j.get("location", "Unknown")
        if isinstance(loc, dict):
            loc = loc.get("name", "Unknown")

        desc = j.get("descriptionHtml", "") or j.get("descriptionPlain", "") or ""

        sal_min = None
        sal_max = None
        sal_text = ""
        comp = j.get("compensation")
        if comp:
            sal_text = comp.get("compensationTierSummary", "")
            for tier in comp.get("compensationTiers", []):
                tmin = tier.get("min")
                tmax = tier.get("max")
                if tmin and (sal_min is None or tmin < sal_min):
                    sal_min = int(tmin)
                if tmax and (sal_max is None or tmax > sal_max):
                    sal_max = int(tmax)

        posted = j.get("publishedDate", "") or j.get("createdAt", "")

        jobs.append(normalize_job(
            job_id=str(j.get("id", "")),
            title=j.get("title", ""),
            url=j.get("jobUrl", j.get("applyUrl", "")),
            location=loc if isinstance(loc, str) else "Unknown",
            description=desc,
            company=company["name"],
            ats="ashby",
            salary_min=sal_min,
            salary_max=sal_max,
            salary_text=sal_text,
            posted_at=str(posted),
        ))
    return jobs, None


def fetch_workable(company: dict) -> Tuple[List[dict], Optional[str]]:
    """Fetch all jobs from a Workable widget API."""
    token = company["board_token"]
    url = f"https://apply.workable.com/api/v1/widget/accounts/{quote(token)}"
    data = safe_get(url)
    if data is None:
        return [], f"Failed to fetch Workable board '{token}'"

    jobs_raw = data.get("jobs", [])
    jobs = []
    for j in jobs_raw:
        loc = j.get("location", "Unknown")
        if isinstance(loc, dict):
            city = loc.get("city", "")
            country = loc.get("country", "")
            loc = ", ".join(filter(None, [city, country])) or "Unknown"

        desc = j.get("description", "") or ""
        shortcode = j.get("shortcode", j.get("id", ""))
        job_url = f"https://apply.workable.com/{quote(token)}/j/{shortcode}/"

        posted = j.get("published_on", "") or j.get("created_at", "")

        jobs.append(normalize_job(
            job_id=str(shortcode),
            title=j.get("title", ""),
            url=job_url,
            location=loc if isinstance(loc, str) else "Unknown",
            description=desc,
            company=company["name"],
            ats="workable",
            posted_at=str(posted),
        ))
    return jobs, None


def fetch_recruitee(company: dict) -> Tuple[List[dict], Optional[str]]:
    """Fetch all jobs from a Recruitee careers site API."""
    token = company["board_token"]
    url = f"https://{quote(token)}.recruitee.com/api/offers/"
    data = safe_get(url)
    if data is None:
        return [], f"Failed to fetch Recruitee board '{token}'"

    jobs_raw = data.get("offers", [])
    jobs = []
    for j in jobs_raw:
        if j.get("status") != "published":
            continue

        loc = j.get("location", "Unknown")
        desc = j.get("description", "") or ""

        sal_min = None
        sal_max = None
        sal_text = ""
        if j.get("min_salary") and j.get("max_salary"):
            sal_min = int(j["min_salary"])
            sal_max = int(j["max_salary"])
            currency = j.get("salary_currency", "USD")
            sal_text = f"{currency} {sal_min:,}-{sal_max:,}"

        slug = j.get("slug", "")
        job_url = j.get("careers_url", f"https://{token}.recruitee.com/o/{slug}")
        posted = j.get("published_at", "") or j.get("created_at", "")

        jobs.append(normalize_job(
            job_id=str(j.get("id", slug)),
            title=j.get("title", ""),
            url=job_url,
            location=loc,
            description=desc,
            company=company["name"],
            ats="recruitee",
            salary_min=sal_min,
            salary_max=sal_max,
            salary_text=sal_text,
            posted_at=str(posted),
        ))
    return jobs, None


def _workday_post_jobs(api_url: str, offset: int = 0, limit: int = 20) -> Optional[dict]:
    """POST to Workday's hidden /wday/cxs/ jobs API."""
    payload = {
        "appliedFacets": {},
        "limit": limit,
        "offset": offset,
        "searchText": "",
    }
    try:
        log(f"POST (workday) {api_url} offset={offset}")
        resp = SESSION.post(api_url, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as exc:
        log(f"Workday POST failed: {exc}")
        return None


def _workday_discover_api_with_playwright(careers_url: str) -> Optional[str]:
    """Use Playwright to discover the Workday /wday/cxs/ API URL by intercepting XHR."""
    if not PLAYWRIGHT_AVAILABLE:
        return None
    log(f"Playwright discovering Workday API for {careers_url}")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            captured_url = {}

            def handle_response(response):
                url = response.url
                if "/wday/cxs/" in url and "/jobs" in url:
                    captured_url["api"] = url

            page.on("response", handle_response)
            page.goto(careers_url, wait_until="networkidle", timeout=30000)
            browser.close()
            return captured_url.get("api")
    except Exception as exc:
        log(f"Playwright discovery failed: {exc}")
        return None


def fetch_workday(company: dict) -> Tuple[List[dict], Optional[str]]:
    """Fetch jobs from a Workday careers site.

    Workday has a hidden POST API at /wday/cxs/{tenant}/{site}/jobs that returns
    structured JSON. Strategy:
    1. Construct the API URL from the board_token and POST to it
    2. If that fails, use Playwright to discover the correct API URL
    3. Paginate through all results (20 per page)

    board_token format: "company.wd5/SiteName" (e.g., "salesforce.wd12/External_Career_Site")
    This maps to: https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/External_Career_Site/jobs
    """
    token = company["board_token"]

    # Parse token: "salesforce.wd12/External_Career_Site" -> host="salesforce.wd12", site="External_Career_Site"
    if "/" in token:
        host_part, site_name = token.split("/", 1)
    else:
        host_part = token
        site_name = ""

    tenant = host_part.split(".")[0]  # "salesforce" from "salesforce.wd12"
    base_url = f"https://{host_part}.myworkdayjobs.com"
    api_url = f"{base_url}/wday/cxs/{tenant}/{site_name}/jobs" if site_name else None

    # Strategy 1: Try the constructed API URL
    data = None
    if api_url:
        data = _workday_post_jobs(api_url)

    # Strategy 2: Playwright fallback to discover the real API URL
    if data is None and PLAYWRIGHT_AVAILABLE:
        careers_url = f"{base_url}/{site_name}" if site_name else base_url
        discovered_url = _workday_discover_api_with_playwright(careers_url)
        if discovered_url:
            log(f"Discovered Workday API: {discovered_url}")
            api_url = discovered_url
            data = _workday_post_jobs(api_url)

    if data is None:
        if not PLAYWRIGHT_AVAILABLE and not api_url:
            return [], f"Workday '{token}': could not construct API URL and Playwright not installed"
        if not PLAYWRIGHT_AVAILABLE:
            return [], f"Workday '{token}': API returned error. Try installing Playwright: pip install playwright && playwright install chromium"
        return [], f"Failed to fetch Workday board '{token}'"

    # Parse the response - Workday returns {jobPostings: [...], total: N}
    postings = data.get("jobPostings", [])
    total = data.get("total", len(postings))

    jobs = []

    def parse_postings(postings_list):
        for p in postings_list:
            title = p.get("title", "")
            external_path = p.get("externalPath", "")
            location = p.get("locationsText", "Unknown")
            posted = p.get("postedOn", "")

            # bulletFields sometimes contains salary info
            salary_text = ""
            for field in p.get("bulletFields", []):
                if "$" in str(field) or "salary" in str(field).lower():
                    salary_text = str(field)

            job_url = f"{base_url}/en-US{external_path}" if external_path else base_url
            job_id = external_path.split("/")[-1] if external_path else title

            jobs.append(normalize_job(
                job_id=str(job_id),
                title=title,
                url=job_url,
                location=location,
                description="",  # List endpoint doesn't include full descriptions
                company=company["name"],
                ats="workday",
                salary_text=salary_text,
                posted_at=posted,
            ))

    parse_postings(postings)

    # Paginate through remaining results
    max_pages = 50  # safety limit (50 * 20 = 1000 jobs max)
    offset = len(postings)
    while offset < total and offset // 20 < max_pages:
        page_data = _workday_post_jobs(api_url, offset=offset)
        if page_data is None:
            break
        page_postings = page_data.get("jobPostings", [])
        if not page_postings:
            break
        parse_postings(page_postings)
        offset += len(page_postings)
        time.sleep(0.3)

    log(f"Workday {company['name']}: {len(jobs)} jobs fetched (total available: {total})")
    return jobs, None


ATS_FETCHERS = {
    "greenhouse": fetch_greenhouse,
    "lever": fetch_lever,
    "ashby": fetch_ashby,
    "workable": fetch_workable,
    "recruitee": fetch_recruitee,
    "workday": fetch_workday,
}

# ---------------------------------------------------------------------------
# LinkedIn via BrightData
# ---------------------------------------------------------------------------

BRIGHTDATA_DATASET_ID = "gd_lpfll7v5hcqtkxl6l"
BRIGHTDATA_TRIGGER_URL = (
    f"https://api.brightdata.com/datasets/v3/trigger"
    f"?dataset_id={BRIGHTDATA_DATASET_ID}&format=json&type=discover_new&discover_by=keyword"
)
BRIGHTDATA_SNAPSHOT_URL = "https://api.brightdata.com/datasets/v3/snapshot"


def linkedin_trigger(api_key: str, filters: dict, limit: int = 25) -> Optional[str]:
    """Trigger a BrightData LinkedIn job search. Returns snapshot_id or None."""
    url = f"{BRIGHTDATA_TRIGGER_URL}&limit_per_input={limit}"
    try:
        resp = SESSION.post(
            url,
            json=[filters],
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json().get("snapshot_id")
    except requests.RequestException as exc:
        log(f"LinkedIn trigger error: {exc}")
        return None


def linkedin_poll(api_key: str, snapshot_id: str, max_wait: int = 180) -> Optional[list]:
    """Poll a BrightData snapshot until ready. Returns list of jobs or None."""
    url = f"{BRIGHTDATA_SNAPSHOT_URL}/{snapshot_id}?format=json"
    elapsed = 0
    while elapsed < max_wait:
        try:
            resp = SESSION.get(
                url,
                headers={"Authorization": f"Bearer {api_key}"},
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            log(f"LinkedIn poll error: {exc}")
            return None

        if isinstance(data, list):
            return data

        status = data.get("status", "")
        if status in ("running", "closing", "starting"):
            wait = 30 if status in ("closing", "starting") else 10
            log(f"LinkedIn snapshot {snapshot_id}: status={status}, waiting {wait}s...")
            time.sleep(wait)
            elapsed += wait
            continue

        log(f"LinkedIn snapshot unexpected response: {data}")
        return None

    log(f"LinkedIn snapshot {snapshot_id} timed out after {max_wait}s")
    return None


def normalize_linkedin_job(job: dict) -> dict:
    """Normalize a BrightData LinkedIn job into the standard job dict format."""
    sal_min = None
    sal_max = None
    sal_text = ""
    base = job.get("base_salary")
    if base:
        sal_min = base.get("min_amount")
        sal_max = base.get("max_amount")
        if sal_min and sal_max:
            sal_text = f"${sal_min:,.0f}-${sal_max:,.0f}"
        elif sal_min:
            sal_text = f"${sal_min:,.0f}+"
    if not sal_text:
        sal_text = job.get("job_base_pay_range", "")

    description = job.get("job_summary", "") or job.get("job_description_formatted", "")

    return normalize_job(
        job_id=str(job.get("job_posting_id", "")),
        title=job.get("job_title", ""),
        url=job.get("url", ""),
        location=job.get("job_location", "Unknown"),
        description=description,
        company=job.get("company_name", "Unknown"),
        ats="linkedin",
        salary_min=int(sal_min) if sal_min else None,
        salary_max=int(sal_max) if sal_max else None,
        salary_text=sal_text,
        posted_at=job.get("job_posted_date", ""),
    )


def fetch_linkedin(config: dict) -> Tuple[List[dict], List[str]]:
    """Run all LinkedIn search queries from the watchlist. Returns (jobs, errors)."""
    api_key = os.environ.get("BRIGHTDATA_API_KEY", "")
    if not api_key:
        return [], ["BRIGHTDATA_API_KEY not set, skipping LinkedIn"]

    queries = config.get("linkedin", {}).get("search_queries", [])
    if not queries:
        return [], ["No LinkedIn search queries configured"]

    time_range = config.get("linkedin", {}).get("time_range", "past_week")
    time_range_map = {
        "past_24h": "Past 24 hours",
        "past_week": "Past week",
        "past_month": "Past month",
    }
    bd_time_range = time_range_map.get(time_range, "Past week")

    all_jobs = []
    errors = []
    seen_ids: set = set()

    for q in queries:
        filters = {
            "keyword": q["keywords"],
            "location": q.get("location", "United States"),
            "time_range": bd_time_range,
        }
        if q.get("remote"):
            filters["remote"] = "Remote"

        log(f"LinkedIn search: {q['keywords']}")
        snapshot_id = linkedin_trigger(api_key, filters, limit=25)
        if not snapshot_id:
            errors.append(f"LinkedIn trigger failed for '{q['keywords']}'")
            continue

        log(f"LinkedIn snapshot {snapshot_id} - polling...")
        raw_jobs = linkedin_poll(api_key, snapshot_id)
        if raw_jobs is None:
            errors.append(f"LinkedIn poll failed/timed out for '{q['keywords']}'")
            continue

        log(f"LinkedIn '{q['keywords']}': {len(raw_jobs)} results")
        for rj in raw_jobs:
            jid = str(rj.get("job_posting_id", ""))
            if jid and jid not in seen_ids:
                seen_ids.add(jid)
                all_jobs.append(normalize_linkedin_job(rj))

        # Pace between queries
        time.sleep(1)

    return all_jobs, errors

# ---------------------------------------------------------------------------
# Keyword Filtering
# ---------------------------------------------------------------------------

def title_matches(title: str, config: dict) -> bool:
    """Return True if title matches include keywords and doesn't match excludes."""
    t = title.lower()
    includes = config["keywords"]["title_include"]
    excludes = config["keywords"]["title_exclude"]

    if any(kw in t for kw in excludes):
        return False
    return any(kw in t for kw in includes)


def description_score(text: str, config: dict) -> int:
    """Count how many boost keywords appear in the description."""
    t = text.lower()
    return sum(1 for kw in config["keywords"]["description_boost"] if kw in t)


# ---------------------------------------------------------------------------
# Salary Extraction
# ---------------------------------------------------------------------------

SALARY_PATTERNS = [
    # $225,000 - $325,000 (with optional currency prefix)
    re.compile(
        r"(?:USD|CAD|GBP|EUR)?\s*\$\s*([\d,]+)\s*[-\u2013\u2014to]+\s*\$?\s*([\d,]+)",
        re.IGNORECASE,
    ),
    # $225K - $325K
    re.compile(
        r"\$\s*(\d+(?:\.\d+)?)\s*[kK]\s*[-\u2013\u2014to]+\s*\$?\s*(\d+(?:\.\d+)?)\s*[kK]",
        re.IGNORECASE,
    ),
    # Single value: $225,000 or $225K
    re.compile(r"\$\s*([\d,]+(?:\.\d+)?)\s*[kK]?", re.IGNORECASE),
]


def extract_salary(text: str, job: dict) -> Tuple[Optional[int], Optional[int], str]:
    """Extract salary range from text and structured fields."""
    if job.get("salary_min") and job.get("salary_max"):
        return job["salary_min"], job["salary_max"], job.get("salary_text", "")
    if job.get("salary_text"):
        text = job["salary_text"] + " " + text

    for pat in SALARY_PATTERNS[:2]:
        m = pat.search(text)
        if m:
            g1 = m.group(1).replace(",", "")
            g2 = m.group(2).replace(",", "")
            v1 = float(g1)
            v2 = float(g2)
            if v1 < 1000:
                v1 *= 1000
            if v2 < 1000:
                v2 *= 1000
            return int(v1), int(v2), m.group(0).strip()

    m = SALARY_PATTERNS[2].search(text)
    if m:
        v = m.group(1).replace(",", "")
        val = float(v)
        if val < 1000:
            val *= 1000
        if val >= 50000:
            return int(val), None, m.group(0).strip()

    return None, None, ""


# ---------------------------------------------------------------------------
# Screening Signals
# ---------------------------------------------------------------------------

def signal(value: str, evidence: str = "") -> dict:
    return {"value": value, "evidence": evidence[:200]}


def screen_remote(job: dict, config: dict) -> dict:
    loc = job["location"].lower()
    desc = job["description_text"].lower()
    combined = loc + " " + desc

    remote_kws = config["screening"].get("remote_keywords", ["remote", "distributed", "work from home", "wfh", "anywhere"])
    hybrid_kws = config["screening"].get("hybrid_keywords", ["hybrid", "in-office", "on-site", "onsite", "in office"])

    has_remote = any(kw in combined for kw in remote_kws)
    has_hybrid = any(kw in combined for kw in hybrid_kws)

    if has_remote and not has_hybrid:
        return signal("PASS", f"Location: {job['location']}")
    if has_remote and has_hybrid:
        return signal("LIKELY_PASS", f"Location: {job['location']} (hybrid mentioned)")
    if has_hybrid and not has_remote:
        return signal("LIKELY_FAIL", f"Location: {job['location']} (hybrid/onsite)")
    return signal("UNKNOWN", f"Location: {job['location']}")


def screen_comp(job: dict, config: dict) -> dict:
    sal_min, sal_max, sal_text = extract_salary(job["description_text"], job)
    floor = config["screening"].get("comp_floor", 0)

    if floor == 0:
        if sal_max or sal_min:
            return signal("INFO", sal_text or f"${sal_max or sal_min:,}")
        return signal("UNKNOWN", "No salary data found")

    if sal_max and sal_max >= floor:
        return signal("PASS", sal_text or f"${sal_max:,}")
    if sal_min and sal_min >= floor:
        return signal("PASS", sal_text or f"${sal_min:,}")
    if sal_max and sal_max < floor:
        return signal("FAIL", sal_text or f"${sal_max:,} (below ${floor:,})")
    if sal_min and sal_min < floor:
        return signal("LIKELY_FAIL", sal_text or f"${sal_min:,}")
    return signal("UNKNOWN", "No salary data found")


def screen_level(job: dict, config: dict) -> dict:
    t = job["title"].lower()
    target_kws = config["screening"].get("senior_keywords", [])
    exclude_kws = config["screening"].get("level_exclude_keywords", [])

    if not target_kws and not exclude_kws:
        return signal("SKIPPED", "No level keywords configured")

    found_target = [kw for kw in target_kws if kw in t]
    found_exclude = [kw for kw in exclude_kws if kw in t]

    if found_exclude:
        return signal("LIKELY_FAIL", f"Title: {job['title']} (matched exclude: {', '.join(found_exclude)})")
    if found_target:
        return signal("PASS", f"Title: {job['title']} (matched: {', '.join(found_target)})")
    return signal("UNKNOWN", f"Title: {job['title']}")


def screen_builder(job: dict, config: dict) -> dict:
    desc = job["description_text"].lower()
    builder_kws = config["screening"].get("builder_keywords", [])
    operator_kws = config["screening"].get("operator_keywords", [])

    if not builder_kws and not operator_kws:
        return signal("SKIPPED", "No builder/operator keywords configured")

    builder_count = sum(1 for kw in builder_kws if kw in desc)
    operator_count = sum(1 for kw in operator_kws if kw in desc)

    if builder_count > operator_count + 2:
        return signal("PASS", f"Builder: {builder_count} vs Operator: {operator_count}")
    if builder_count > operator_count:
        return signal("LIKELY_PASS", f"Builder: {builder_count} vs Operator: {operator_count}")
    if operator_count > builder_count + 2:
        return signal("FAIL", f"Builder: {builder_count} vs Operator: {operator_count}")
    if operator_count > builder_count:
        return signal("LIKELY_FAIL", f"Builder: {builder_count} vs Operator: {operator_count}")
    return signal("UNKNOWN", f"Builder: {builder_count} vs Operator: {operator_count}")


def screen_ai(job: dict, config: dict) -> dict:
    desc = job["description_text"].lower()
    ai_kws = config["screening"].get("ai_keywords", [])

    if not ai_kws:
        return signal("SKIPPED", "No AI keywords configured")

    count = sum(1 for kw in ai_kws if kw in desc)
    if count >= 3:
        return signal("PASS", f"{count} AI keywords found")
    if count >= 1:
        return signal("LIKELY_PASS", f"{count} AI keywords found")
    return signal("UNKNOWN", "No AI keywords found")


def screen_tech_depth(job: dict, config: dict) -> dict:
    desc = job["description_text"].lower()
    deep_kws = config["screening"].get("deep_eng_keywords", [])

    if not deep_kws:
        return signal("SKIPPED", "No deep-eng keywords configured")

    count = sum(1 for kw in deep_kws if kw in desc)
    if count >= 3:
        return signal("LIKELY_FAIL", f"{count} deep-eng keywords: may be infra role")
    if count >= 1:
        return signal("UNKNOWN", f"{count} deep-eng keywords found")
    return signal("PASS", "No deep-engineering red flags")


AVAILABLE_SIGNALS = {
    "Remote": screen_remote,
    "Comp": screen_comp,
    "Level": screen_level,
    "Builder": screen_builder,
    "AI": screen_ai,
    "TechDepth": screen_tech_depth,
}


def screen_job(job: dict, config: dict) -> dict:
    """Run screening signals on a job. Respects disabled_signals in config."""
    disabled = set(config.get("screening", {}).get("disabled_signals", []))
    results = {}
    for name, fn in AVAILABLE_SIGNALS.items():
        if name in disabled:
            continue
        results[name] = fn(job, config)
    return results


# ---------------------------------------------------------------------------
# Dedup State
# ---------------------------------------------------------------------------

def load_seen() -> dict:
    if SEEN_PATH.exists():
        with open(SEEN_PATH) as f:
            return json.load(f)
    return {"seen": {}, "last_run": None}


def save_seen(state: dict) -> None:
    SEEN_PATH.parent.mkdir(parents=True, exist_ok=True)
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    with open(SEEN_PATH, "w") as f:
        json.dump(state, f, indent=2)


def is_new(job: dict, state: dict) -> bool:
    return job["id"] not in state["seen"]


def mark_seen(job: dict, state: dict) -> None:
    state["seen"][job["id"]] = {
        "title": job["title"],
        "company": job["company"],
        "first_seen": datetime.now(timezone.utc).isoformat(),
        "url": job["url"],
    }


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------

def format_signals(signals: dict) -> str:
    parts = []
    for name, s in signals.items():
        if s["value"] != "SKIPPED":
            parts.append(f"{name} {s['value']}")
    return " | ".join(parts)


def generate_report(
    new_matches: list[dict],
    still_active: list[dict],
    errors: list[dict],
    stats: dict,
    today: str,
    linkedin_stats: Optional[dict] = None,
) -> str:
    lines = []
    lines.append(f"# Job Scout Results - {today}\n")
    li = linkedin_stats or {}
    li_summary = ""
    if li.get("linkedin_jobs"):
        li_summary = (
            f" | **LinkedIn:** {li['linkedin_jobs']} jobs from "
            f"{li['linkedin_queries']} queries"
        )
    lines.append(
        f"**Scanned:** {stats['companies_scanned']} companies | "
        f"**Jobs fetched:** {stats['total_jobs']} | "
        f"**Title matches:** {stats['title_matches']} | "
        f"**New:** {stats['new_matches']}{li_summary}\n"
    )

    lines.append("## New Matches\n")
    if not new_matches:
        lines.append("No new matches found.\n")
    for i, m in enumerate(new_matches, 1):
        job = m["job"]
        signals = m["signals"]
        desc_score = m["desc_score"]
        sal_min, sal_max, sal_text = extract_salary(job["description_text"], job)

        lines.append(f"### {i}. {job['company']} - {job['title']}")
        lines.append(f"- **URL:** {job['url']}")
        lines.append(f"- **Location:** {job['location']}")
        if sal_text:
            lines.append(f"- **Salary:** {sal_text}")
        elif sal_min:
            sal_display = f"${sal_min:,}"
            if sal_max:
                sal_display += f"-${sal_max:,}"
            lines.append(f"- **Salary:** {sal_display}")
        lines.append(f"- **Signals:** {format_signals(signals)}")
        lines.append(f"- **Description relevance:** {desc_score} boost keywords")
        clean_desc = strip_html(job["description_text"])
        snippet = clean_desc[:300]
        if len(clean_desc) > 300:
            snippet += "..."
        lines.append(f"- **Description:** {snippet}")
        if job.get("posted_at"):
            lines.append(f"- **Posted:** {job['posted_at'][:10]}")
        lines.append("")

    # LinkedIn section
    lines.append("## LinkedIn Discoveries\n")
    if li.get("linkedin_jobs"):
        li_new = [m for m in new_matches if m["job"].get("ats") == "linkedin"]
        if li_new:
            lines.append(f"{len(li_new)} new LinkedIn match(es) included in New Matches above.\n")
        else:
            lines.append(f"LinkedIn returned {li['linkedin_jobs']} jobs, {li.get('linkedin_title_matches', 0)} title matches, but no new ones.\n")
    elif li.get("skipped"):
        lines.append("*LinkedIn search skipped (--no-linkedin or no API key).*\n")
    elif li.get("error"):
        lines.append(f"*LinkedIn search failed: {li['error']}*\n")
    else:
        lines.append("*No LinkedIn search queries configured in watchlist.*\n")

    lines.append("## Previously Seen (Still Active)\n")
    if still_active:
        lines.append("| Company | Title | First Seen |")
        lines.append("|---------|-------|-----------|")
        for sa in still_active[:30]:
            lines.append(f"| {sa['company']} | {sa['title']} | {sa['first_seen'][:10]} |")
        lines.append("")
    else:
        lines.append("No previously seen jobs re-matched.\n")

    if errors:
        lines.append("## Errors\n")
        lines.append("| Company | Error |")
        lines.append("|---------|-------|")
        for e in errors:
            lines.append(f"| {e['company']} | {e['error']} |")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    global VERBOSE, CONFIG

    parser = argparse.ArgumentParser(description="Job Scout - ATS job board scanner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Extra logging")
    parser.add_argument("--reset", action="store_true", help="Clear seen-jobs state before running")
    parser.add_argument("--company", type=str, help="Scan a single company by name")
    parser.add_argument("--dry-run", action="store_true", help="Fetch and filter but don't update state")
    parser.add_argument("--config", type=str, help="Path to watchlist.json (overrides default)")
    parser.add_argument("--no-workday", action="store_true", help="Skip Workday companies (avoids Playwright dependency)")
    parser.add_argument("--no-linkedin", action="store_true", help="Skip LinkedIn search (requires BRIGHTDATA_API_KEY)")
    parser.add_argument("--archive-jds", action="store_true", help="Save full JDs for all new matches to content/jobs/")
    args = parser.parse_args()
    VERBOSE = args.verbose

    # Find config
    config_path = Path(args.config) if args.config else None
    if config_path is None:
        if CONFIG_PATH.exists():
            config_path = CONFIG_PATH
        elif FALLBACK_CONFIG_PATH.exists():
            config_path = FALLBACK_CONFIG_PATH
        else:
            print("ERROR: No watchlist.json found.", file=sys.stderr)
            print(f"  Expected at: {CONFIG_PATH}", file=sys.stderr)
            print("  Run /job-onboard to set up your configuration.", file=sys.stderr)
            sys.exit(1)

    with open(config_path) as f:
        CONFIG = json.load(f)
    log(f"Config loaded from {config_path}")

    # Load or reset seen state
    if args.reset:
        log("Resetting seen state")
        state = {"seen": {}, "last_run": None}
    else:
        state = load_seen()
    log(f"Loaded {len(state['seen'])} previously seen jobs")

    today = datetime.now().strftime("%Y-%m-%d")

    # Determine companies to scan
    companies = CONFIG.get("companies", [])
    if not companies:
        print("ERROR: No companies in watchlist. Run /job-onboard to add target companies.", file=sys.stderr)
        sys.exit(1)

    if args.company:
        companies = [c for c in companies if c["name"].lower() == args.company.lower()]
        if not companies:
            print(f"ERROR: Company '{args.company}' not found in watchlist", file=sys.stderr)
            sys.exit(1)

    # Fetch all jobs
    all_jobs = []
    errors = []
    companies_scanned = 0

    for company in companies:
        if company.get("skip"):
            log(f"Skipping {company['name']} (skip=true)")
            continue

        ats = company.get("ats", "greenhouse")
        if ats == "workday" and args.no_workday:
            log(f"Skipping {company['name']} (--no-workday)")
            continue
        fetcher = ATS_FETCHERS.get(ats)
        if not fetcher:
            errors.append({"company": company["name"], "error": f"Unknown ATS: {ats}"})
            continue

        jobs, err = fetcher(company)
        if err:
            errors.append({"company": company["name"], "error": err})
        else:
            all_jobs.extend(jobs)
            companies_scanned += 1
            log(f"{company['name']}: {len(jobs)} jobs fetched")

        time.sleep(0.3)

    # LinkedIn search
    linkedin_jobs = []
    linkedin_errors = []
    if not args.no_linkedin and not args.company:
        log("Starting LinkedIn search...")
        linkedin_jobs, linkedin_errors = fetch_linkedin(CONFIG)
        log(f"LinkedIn: {len(linkedin_jobs)} jobs from {len(CONFIG.get('linkedin', {}).get('search_queries', []))} queries")
        for le in linkedin_errors:
            errors.append({"company": "LinkedIn", "error": le})
    elif args.no_linkedin:
        log("LinkedIn search skipped (--no-linkedin)")

    log(f"Total ATS jobs fetched: {len(all_jobs)}")

    # Filter ATS jobs by title keywords
    title_filtered = [j for j in all_jobs if title_matches(j["title"], CONFIG)]
    log(f"ATS title matches: {len(title_filtered)}")

    # Filter LinkedIn jobs by title keywords and combine
    linkedin_filtered = [j for j in linkedin_jobs if title_matches(j["title"], CONFIG)]
    log(f"LinkedIn title matches: {len(linkedin_filtered)}")
    title_filtered = title_filtered + linkedin_filtered

    # Screen, score, and separate new vs seen
    new_matches = []
    still_active = []

    for job in title_filtered:
        if is_new(job, state):
            signals = screen_job(job, CONFIG)
            dscore = description_score(job["description_text"], CONFIG)
            new_matches.append({
                "job": job,
                "signals": signals,
                "desc_score": dscore,
            })
            if not args.dry_run:
                mark_seen(job, state)
        else:
            seen_data = state["seen"].get(job["id"], {})
            still_active.append({
                "company": job["company"],
                "title": job["title"],
                "first_seen": seen_data.get("first_seen", "unknown"),
                "url": job["url"],
            })

    new_matches.sort(key=lambda m: m["desc_score"], reverse=True)

    # Archive full JDs if requested
    if args.archive_jds and new_matches:
        JD_DIR.mkdir(parents=True, exist_ok=True)
        for m in new_matches:
            path = archive_jd(m["job"])
            m["jd_path"] = str(path)
        print(f"  Archived {len(new_matches)} JDs to {JD_DIR}")

    stats = {
        "companies_scanned": companies_scanned,
        "total_jobs": len(all_jobs),
        "title_matches": len(title_filtered),
        "new_matches": len(new_matches),
    }

    linkedin_stats = None
    if not args.no_linkedin and not args.company:
        linkedin_stats = {
            "linkedin_jobs": len(linkedin_jobs),
            "linkedin_queries": len(CONFIG.get("linkedin", {}).get("search_queries", [])),
            "linkedin_title_matches": len(linkedin_filtered),
        }
        if not linkedin_jobs and linkedin_errors:
            linkedin_stats["error"] = "; ".join(linkedin_errors)
    elif args.no_linkedin:
        linkedin_stats = {"skipped": True}

    # Generate report
    report = generate_report(new_matches, still_active, errors, stats, today, linkedin_stats)

    # Write report file
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{today}-job-scout-results.md"
    with open(output_path, "w") as f:
        f.write(report)

    # Save state
    if not args.dry_run:
        save_seen(state)

    # Print summary
    print(f"Job Scout complete - {today}")
    print(f"  ATS companies scanned: {companies_scanned}")
    print(f"  ATS jobs fetched: {len(all_jobs)}")
    if linkedin_stats and linkedin_stats.get("linkedin_jobs"):
        print(f"  LinkedIn queries: {linkedin_stats['linkedin_queries']}")
        print(f"  LinkedIn jobs fetched: {linkedin_stats['linkedin_jobs']}")
        print(f"  LinkedIn title matches: {linkedin_stats['linkedin_title_matches']}")
    print(f"  Total title matches: {len(title_filtered)}")
    print(f"  New matches: {len(new_matches)}")
    if errors:
        print(f"  Errors: {len(errors)}")
    print(f"  Report: {output_path}")

    if new_matches:
        print("\nTop new matches:")
        for m in new_matches[:5]:
            j = m["job"]
            print(f"  - {j['company']} - {j['title']}")
            print(f"    {format_signals(m['signals'])}")


if __name__ == "__main__":
    main()
