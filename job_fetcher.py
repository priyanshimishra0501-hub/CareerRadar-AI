
import requests
import re
import time
from html import unescape
from urllib.parse import urlparse, urlunparse
from datetime import datetime, timezone
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


# ==========================================
# CAREERRADAR AI - SMART JOB DATA COLLECTOR
# Created by Priyanshi Mishra
# ==========================================

REMOTIVE_API = "https://remotive.com/api/remote-jobs"
ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"

UPDATE_INTERVAL = 30 * 60  # 30 minutes
TIMEOUT = 20

HEADERS = {
    "User-Agent": "CareerRadarAI/2.0 (Student Job Discovery Project)"
}

# Session with automatic retry support
session = requests.Session()

retry_strategy = Retry(
    total=3,
    connect=3,
    read=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session.mount("https://", adapter)
session.mount("http://", adapter)


LAST_FETCH_TIME = None
LAST_FETCH_STATUS = "Not fetched yet"


# ==========================================
# TEXT CLEANING
# ==========================================

def clean_text(value):
    """Remove HTML tags and clean text."""

    if not value:
        return ""

    value = re.sub(r"<[^>]*>", " ", str(value))
    value = unescape(value)

    return re.sub(r"\s+", " ", value).strip()


def normalize_url(url):
    """Normalize URLs for duplicate detection."""

    if not url:
        return ""

    try:
        parsed = urlparse(url.strip())

        return urlunparse((
            parsed.scheme.lower(),
            parsed.netloc.lower(),
            parsed.path.rstrip("/"),
            "",
            "",
            ""
        ))

    except Exception:
        return url.strip().lower()


def normalize_text(value):
    return re.sub(
        r"\s+",
        " ",
        clean_text(value).lower()
    ).strip()


def get_job_date(value):
    if not value:
        return ""

    return str(value).strip()


def get_current_time():
    return datetime.now(timezone.utc).isoformat()


# ==========================================
# JOB TYPE NORMALIZATION
# ==========================================

def normalize_job_type(value):

    if isinstance(value, list):
        return ", ".join(
            clean_text(item) for item in value
        )

    return clean_text(value)


# ==========================================
# REMOTIVE JOB FETCHER
# ==========================================

def fetch_remotive_jobs():

    jobs_list = []

    try:
        response = session.get(
            REMOTIVE_API,
            params={"limit": 100},
            headers=HEADERS,
            timeout=TIMEOUT
        )

        response.raise_for_status()

        data = response.json()
        jobs = data.get("jobs", [])

        for job in jobs:

            if not job.get("url") or not job.get("title"):
                continue

            jobs_list.append({

                "id": f"remotive_{job.get('id')}",

                "title": clean_text(
                    job.get("title")
                ),

                "company": clean_text(
                    job.get("company_name")
                ),

                "location": clean_text(
                    job.get("candidate_required_location")
                ) or "Remote",

                "job_type": normalize_job_type(
                    job.get("job_type")
                ),

                "date": get_job_date(
                    job.get("publication_date")
                ),

                "description": clean_text(
                    job.get("description")
                ),

                "skills": clean_text(
                    job.get("category")
                ),

                "salary": clean_text(
                    job.get("salary")
                ),

                "url": job.get("url"),

                "source": "Remotive",

                "remote": True

            })

        print(
            f"Remotive: {len(jobs_list)} jobs fetched."
        )

    except (
        requests.RequestException,
        ValueError,
        AttributeError
    ) as error:

        print(f"Remotive error: {error}")

    return jobs_list


# ==========================================
# ARBEITNOW JOB FETCHER
# ==========================================

def fetch_arbeitnow_jobs(max_pages=3):

    jobs_list = []

    for page in range(1, max_pages + 1):

        try:

            response = session.get(
                ARBEITNOW_API,
                params={"page": page},
                headers=HEADERS,
                timeout=TIMEOUT
            )

            response.raise_for_status()

            data = response.json()
            jobs = data.get("data", [])

            if not jobs:
                break

            for job in jobs:

                if not job.get("url") or not job.get("title"):
                    continue

                job_types = job.get("job_types", [])
                tags = job.get("tags", [])

                jobs_list.append({

                    "id": f"arbeitnow_{job.get('slug')}",

                    "title": clean_text(
                        job.get("title")
                    ),

                    "company": clean_text(
                        job.get("company_name")
                    ),

                    "location": clean_text(
                        job.get("location")
                    ),

                    "job_type": normalize_job_type(
                        job_types
                    ),

                    "date": get_job_date(
                        job.get("created_at")
                    ),

                    "description": clean_text(
                        job.get("description")
                    ),

                    "skills": normalize_job_type(
                        tags
                    ),

                    "salary": "",

                    "url": job.get("url"),

                    "source": "Arbeitnow",

                    "remote": bool(
                        job.get("remote", False)
                    )

                })

        except (
            requests.RequestException,
            ValueError,
            AttributeError
        ) as error:

            print(
                f"Arbeitnow page {page} error: {error}"
            )

            break

    print(
        f"Arbeitnow: {len(jobs_list)} jobs fetched."
    )

    return jobs_list


# ==========================================
# DUPLICATE JOB REMOVER
# ==========================================

def remove_duplicate_jobs(jobs):

    unique_jobs = {}
    fingerprints = set()

    for job in jobs:

        normalized_url = normalize_url(
            job.get("url")
        )

        if not normalized_url:
            continue

        if normalized_url in unique_jobs:
            continue

        fingerprint = (

            normalize_text(job.get("title")),

            normalize_text(job.get("company")),

            normalize_text(job.get("location"))

        )

        if fingerprint in fingerprints:
            continue

        unique_jobs[normalized_url] = job
        fingerprints.add(fingerprint)

    return list(unique_jobs.values())


# ==========================================
# OPPORTUNITY CLASSIFICATION
# ==========================================

def classify_opportunity(job):

    text = " ".join([

        job.get("title", ""),
        job.get("description", ""),
        job.get("skills", ""),
        job.get("job_type", "")

    ]).lower()

    categories = {

        "AI / Machine Learning": [
            "artificial intelligence",
            "machine learning",
            "deep learning",
            "data science",
            "generative ai",
            "llm",
            "computer vision",
            "nlp"
        ],

        "Python Development": [
            "python",
            "django",
            "flask",
            "fastapi"
        ],

        "Software Development": [
            "software engineer",
            "software developer",
            "backend developer",
            "frontend developer",
            "full stack",
            "web developer"
        ],

        "Cybersecurity": [
            "cybersecurity",
            "security analyst",
            "penetration testing",
            "ethical hacking",
            "information security"
        ],

        "Data Analytics": [
            "data analyst",
            "data analytics",
            "business analyst",
            "power bi",
            "sql analyst"
        ]

    }

    matched = []

    for category, keywords in categories.items():

        if any(keyword in text for keyword in keywords):
            matched.append(category)

    return matched if matched else ["Other"]


# ==========================================
# FINAL JOB FETCHER
# ==========================================

def fetch_all_jobs():

    global LAST_FETCH_TIME
    global LAST_FETCH_STATUS

    print("\n" + "=" * 50)
    print("       CAREERRADAR AI - JOB DISCOVERY")
    print("=" * 50)

    all_jobs = []

    # Fetch independently from each source
    all_jobs.extend(fetch_remotive_jobs())

    all_jobs.extend(fetch_arbeitnow_jobs())

    # Remove duplicate opportunities
    final_jobs = remove_duplicate_jobs(all_jobs)

    # Classify jobs
    for job in final_jobs:

        job["categories"] = classify_opportunity(job)

    LAST_FETCH_TIME = get_current_time()

    if final_jobs:

        LAST_FETCH_STATUS = "Success"

    else:

        LAST_FETCH_STATUS = "No jobs returned or sources unavailable"

    sources = sorted(set(
        job["source"] for job in final_jobs
    ))

    print("\n" + "=" * 50)
    print("       CAREERRADAR AI - FETCH SUMMARY")
    print("=" * 50)

    print(f"Total opportunities: {len(final_jobs)}")

    print(f"Sources connected: {len(sources)}")

    print(
        f"Sources: {', '.join(sources) if sources else 'None'}"
    )

    print(f"Last fetched: {LAST_FETCH_TIME}")

    print(f"Status: {LAST_FETCH_STATUS}")

    print("=" * 50)

    return final_jobs


# ==========================================
# UPDATE INFORMATION
# ==========================================

def get_last_fetch_info():

    return {

        "last_updated": LAST_FETCH_TIME,

        "status": LAST_FETCH_STATUS,

        "next_update_interval": UPDATE_INTERVAL

    }


# ==========================================
# TEST RUN
# ==========================================

if __name__ == "__main__":

    opportunities = fetch_all_jobs()

    for index, job in enumerate(
        opportunities[:10],
        start=1
    ):

        print(f"\n{index}. {job['title']}")

        print("Company:", job["company"])

        print("Location:", job["location"])

        print("Type:", job["job_type"])

        print("Category:", ", ".join(job["categories"]))

        print("Source:", job["source"])

        print("Apply:", job["url"])
