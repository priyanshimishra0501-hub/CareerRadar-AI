
import streamlit as st
from streamlit_autorefresh import st_autorefresh

from services.job_fetcher import fetch_all_jobs
from services.database import (
    initialize_database,
    save_jobs,
    get_all_jobs,
    save_job,
    get_saved_jobs,
    update_application_status,
)

# ============================================================
# CAREERRADAR AI — OPPORTUNITY INTELLIGENCE
# Proudly created by Priyanshi Mishra
# ============================================================

st.set_page_config(
    page_title="CareerRadar AI | Opportunity Intelligence",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- THEME -----------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap');

:root {
    --navy: #071426;
    --panel: #0d1e35;
    --panel2: #102744;
    --blue: #3b9cff;
    --cyan: #61d5ff;
    --muted: #9db2cc;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background: radial-gradient(circle at 80% 0%, #102c50 0%, #08172b 42%, #061222 100%);
    color: #edf5ff;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #09182c, #0b203a);
    border-right: 1px solid #1b3859;
}

[data-testid="stSidebar"] * {
    color: #e8f2ff;
}

.block-container {
    padding-top: 1.7rem;
    padding-bottom: 3rem;
    max-width: 1500px;
}

h1, h2, h3 {
    font-family: 'Space Grotesk', sans-serif !important;
    color: #f4f8ff !important;
}

.hero {
    background: linear-gradient(120deg, rgba(17,43,75,.98), rgba(8,24,45,.98));
    border: 1px solid rgba(91,166,255,.28);
    border-radius: 24px;
    padding: 32px 34px;
    box-shadow: 0 18px 60px rgba(0,0,0,.22);
    position: relative;
    overflow: hidden;
}

.hero:after {
    content: "";
    position: absolute;
    width: 280px;
    height: 280px;
    right: -90px;
    top: -130px;
    border: 1px solid rgba(77,174,255,.2);
    border-radius: 50%;
    box-shadow: 0 0 0 35px rgba(77,174,255,.035), 0 0 0 70px rgba(77,174,255,.025);
    pointer-events: none;
}

.eyebrow {
    color: #65cfff;
    font-size: 11px;
    letter-spacing: 3px;
    font-weight: 800;
}

.hero-title {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(35px, 5vw, 58px);
    line-height: 1.04;
    font-weight: 700;
    letter-spacing: -2px;
    margin: 13px 0;
    color: #fff;
}

.hero-title span {
    color: #54b4ff;
}

.hero-sub {
    color: #b5c9e1;
    font-size: 15px;
    max-width: 680px;
    line-height: 1.7;
}

.creator {
    margin-top: 24px;
    padding-top: 18px;
    border-top: 1px solid rgba(145,190,235,.18);
}

.creator-label {
    color: #86a9ce;
    font-size: 10px;
    letter-spacing: 2.4px;
    font-weight: 800;
}

.creator-name {
    font-family: 'Space Grotesk',sans-serif;
    font-size: 25px;
    font-weight: 700;
    color: #fff;
    margin-top: 4px;
}

.creator-role {
    color: #9db7d4;
    font-size: 12px;
    margin-top: 2px;
}

.metric-card {
    background: linear-gradient(145deg, #102a49, #0b1c32);
    border: 1px solid #1b3c60;
    border-radius: 17px;
    padding: 18px 20px;
    min-height: 105px;
}

.metric-number {
    font-family: 'Space Grotesk',sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: #fff;
}

.metric-label {
    color: #9fb7d2;
    font-size: 11px;
    margin-top: 3px;
    letter-spacing: .7px;
    font-weight: 700;
}

.job-card {
    background: linear-gradient(145deg, rgba(16,39,67,.96), rgba(10,27,48,.98));
    border: 1px solid #1b3b5d;
    border-radius: 17px;
    padding: 19px 20px;
    margin-bottom: 13px;
}

.job-title {
    font-family: 'Space Grotesk',sans-serif;
    color: #f5f9ff;
    font-size: 19px;
    font-weight: 700;
}

.job-company {
    color: #72c4ff;
    font-weight: 600;
    font-size: 13px;
    margin-top: 5px;
}

.job-meta {
    color: #a9bfd8;
    font-size: 12px;
    margin-top: 12px;
}

.pill {
    display: inline-block;
    padding: 5px 9px;
    border-radius: 20px;
    background: #14395b;
    color: #9edcff;
    font-size: 10px;
    font-weight: 700;
    margin: 8px 5px 0 0;
    border: 1px solid #23527b;
}

.small-note {
    color: #91a9c5;
    font-size: 11px;
}

.section-kicker {
    color: #75c5ff;
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 2px;
}

div.stButton > button, div.stLinkButton > a {
    border-radius: 10px;
    border: 1px solid #2c77b8;
    background: linear-gradient(100deg, #1675c5, #269fe5);
    color: white;
    font-weight: 700;
    transition: .2s;
}

div.stButton > button:hover, div.stLinkButton > a:hover {
    border-color: #70c9ff;
    box-shadow: 0 0 18px #1c83c955;
    transform: translateY(-1px);
    color: white;
}

.stTextInput input, .stSelectbox div[data-baseweb="select"],
.stMultiSelect div[data-baseweb="select"] {
    background: #0c2038 !important;
    color: #edf5ff !important;
    border-color: #234565 !important;
    border-radius: 10px !important;
}

[data-testid="stMetric"] {
    background: #102744;
    padding: 15px;
    border: 1px solid #1c3b5c;
    border-radius: 14px;
}

[data-testid="stExpander"] {
    border-color: #244565 !important;
    border-radius: 12px !important;
}

hr {
    border-color: #1c3855 !important;
}

footer {
    visibility: hidden;
}
</style>
""", unsafe_allow_html=True)


# -------------------------- DATABASE ---------------------------

initialize_database()


# ---------------------- AUTO JOB UPDATE ------------------------

# Refresh Streamlit session every 30 minutes.
refresh_count = st_autorefresh(
    interval=30 * 60 * 1000,
    limit=None,
    key="career_radar_auto_refresh"
)

# Initial fetch and subsequent automatic fetches.
if st.session_state.get("last_auto_refresh") != refresh_count:

    with st.spinner("CareerRadar AI is updating opportunities..."):
        fresh_jobs = fetch_all_jobs()
        inserted, updated = save_jobs(fresh_jobs)

    st.session_state["last_auto_refresh"] = refresh_count
    st.session_state["last_update_message"] = (
        f"{inserted} new opportunities added · {updated} updated"
    )


# ------------------------- UTILITIES ----------------------------

def safe_text(value, fallback="Not specified"):
    if value is None or str(value).strip() == "":
        return fallback
    return str(value).strip()


def is_internship(job):
    title = safe_text(job.get("title"), "").lower()
    job_type = safe_text(job.get("job_type"), "").lower()

    return (
        "intern" in title
        or "intern" in job_type
        or "trainee" in title
        or "apprentice" in title
    )


def is_entry_level(job):
    title = safe_text(job.get("title"), "").lower()
    description = safe_text(job.get("description"), "").lower()

    combined = title + " " + description

    signals = [
        "intern", "trainee", "graduate", "fresher",
        "entry level", "entry-level", "junior",
        "new grad", "0-1 year", "associate"
    ]

    return any(signal in combined for signal in signals)


def get_location_group(job):
    location = safe_text(job.get("location"), "").lower()

    if any(x in location for x in [
        "india", "indian", "bengaluru", "bangalore",
        "hyderabad", "pune", "mumbai", "delhi",
        "gurgaon", "gurugram", "noida", "chennai",
        "kolkata", "chandigarh", "ludhiana"
    ]):
        return "India"

    if any(x in location for x in [
        "worldwide", "anywhere", "global"
    ]):
        return "Worldwide"

    if job.get("remote") or "remote" in location:
        return "Remote"

    return "Other"


def matches_field(job, selected_fields):

    if not selected_fields or "All fields" in selected_fields:
        return True

    text = " ".join([
        safe_text(job.get("title"), ""),
        safe_text(job.get("description"), ""),
        safe_text(job.get("skills"), ""),
        safe_text(job.get("job_type"), ""),
    ]).lower()

    keywords = {
        "AI / Machine Learning": [
            "ai", "artificial intelligence",
            "machine learning", "deep learning", "llm"
        ],
        "Python": ["python"],
        "Data Science": [
            "data science", "data analyst",
            "data engineer", "analytics"
        ],
        "Software Development": [
            "software", "developer", "programmer",
            "backend", "frontend", "full stack", "java", "c++"
        ],
        "Cybersecurity": [
            "cyber", "security", "soc",
            "penetration", "infosec"
        ],
        "Web Development": [
            "web", "frontend", "backend",
            "full stack", "react", "django"
        ],
        "Cloud / DevOps": [
            "cloud", "devops", "aws",
            "azure", "kubernetes"
        ],
    }

    return any(
        word in text
        for field in selected_fields
        for word in keywords.get(field, [])
    )


# ------------------------- JOB DISPLAY --------------------------

def render_job(job, index, saved_page=False):

    title = safe_text(job.get("title"), "Untitled position")
    company = safe_text(job.get("company"), "Company not specified")
    location = safe_text(job.get("location"))
    source = safe_text(job.get("source"), "Unknown source")
    url = job.get("url")

    st.markdown(f"""
    <div class="job-card">
        <div class="job-title">{title}</div>
        <div class="job-company">{company}</div>
        <div class="job-meta">
            📍 {location} &nbsp; · &nbsp; Source: {source}
        </div>
        <span class="pill">
            {'INTERNSHIP' if is_internship(job) else 'JOB / ROLE'}
        </span>
        <span class="pill">
            {'STUDENT / FRESHER SIGNAL' if is_entry_level(job) else 'EXPERIENCE NOT CONFIRMED'}
        </span>
        {('<span class="pill">REMOTE</span>') if job.get('remote') else ''}
    </div>
    """, unsafe_allow_html=True)

    if job.get("salary"):
        st.caption(f"💰 {job['salary']}")

    if job.get("skills"):
        st.caption(f"Skills / category: {job['skills']}")

    with st.expander("View job description"):
        st.write(
            safe_text(
                job.get("description"),
                "Description not available."
            )
        )

    left, middle, right = st.columns([1, 1, 2])

    with left:
        if not saved_page:

            if st.button(
                "☆ Save job",
                key=f"save_{job.get('id', index)}",
                use_container_width=True
            ):
                save_job(job["id"])
                st.toast("Opportunity saved!")
                st.rerun()

        else:
            st.info(
                "To remove a saved item, a delete method "
                "must be added to database.py."
            )

    with middle:
        if saved_page:

            statuses = [
                "Saved", "Applied", "Interview",
                "Rejected", "Selected"
            ]

            current = safe_text(job.get("status"), "Saved")

            selected = st.selectbox(
                "Application status",
                statuses,
                index=statuses.index(current)
                if current in statuses else 0,
                key=f"status_{job.get('id', index)}",
            )

            if selected != current:
                update_application_status(job["id"], selected)
                st.toast("Application status updated.")
                st.rerun()

    with right:
        if url:
            st.link_button(
                "🚀 Apply on original listing ↗",
                url,
                use_container_width=True
            )
        else:
            st.caption("Application link not available from source.")

    st.write("")


# ----------------------------- SIDEBAR ----------------------------

with st.sidebar:

    st.markdown("## 🎯 CareerRadar AI")

    st.markdown(
        "<div class='section-kicker'>OPPORTUNITY INTELLIGENCE</div>",
        unsafe_allow_html=True
    )

    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Discover",
            "Saved opportunities",
            "About CareerRadar"
        ],
    )

    st.divider()

    st.markdown("**YOUR CAREER RADAR**")

    st.caption(
        "Built for students, freshers and early-career talent."
    )

    st.markdown("""
    <div style="padding:14px;border:1px solid #23496d;
    border-radius:13px;background:#102744">
        <div style="font-size:10px;letter-spacing:2px;
        color:#83bce9">PROUDLY CREATED BY</div>
        <div style="font-size:18px;font-weight:800;
        margin-top:5px">PRIYANSHI MISHRA</div>
        <div style="font-size:11px;color:#9fb8d4">
        AI & ML Student • Developer</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.caption(
        "Listings come from your connected public job sources. "
        "Verify every role on its original page."
    )


# ----------------------------- HERO -------------------------------

if page == "Discover":

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">
            CAREERRADAR AI &nbsp; / &nbsp; OPPORTUNITY INTELLIGENCE
        </div>
        <div class="hero-title">
            Find Your Next<br><span>Big Opportunity.</span>
        </div>
        <div class="hero-sub">
            Discover internships and jobs that match your career goals.
            One focused dashboard for students, freshers and ambitious builders.
        </div>
        <div class="creator">
            <div class="creator-label">PROUDLY CREATED BY</div>
            <div class="creator-name">PRIYANSHI MISHRA</div>
            <div class="creator-role">AI & ML Student • Developer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    top_left, top_right = st.columns([5, 1])

    with top_left:
        st.markdown("### Your opportunity dashboard")
        st.caption(
            "India opportunities first · Worldwide remote opportunities second"
        )

        st.caption(
            "⏱ Automatic refresh: Every 30 minutes"
        )

        if st.session_state.get("last_update_message"):
            st.caption(
                "Latest update: "
                + st.session_state["last_update_message"]
            )

    with top_right:

        if st.button("↻ Fetch latest", use_container_width=True):

            with st.spinner("Fetching latest opportunities..."):

                fresh_jobs = fetch_all_jobs()
                inserted, updated = save_jobs(fresh_jobs)

            st.success(
                f"Fetched {len(fresh_jobs)} listings · "
                f"{inserted} new · {updated} updated"
            )

            st.session_state["last_update_message"] = (
                f"{inserted} new opportunities added · {updated} updated"
            )

            st.rerun()

    all_jobs = get_all_jobs()
    saved_jobs = get_saved_jobs()

    total_count = len(all_jobs)

    internship_count = sum(
        is_internship(j) for j in all_jobs
    )

    saved_count = len(saved_jobs)

    source_count = len({
        safe_text(j.get("source"), "")
        for j in all_jobs if j.get("source")
    })

    metrics = [
        (total_count, "TOTAL OPPORTUNITIES"),
        (internship_count, "INTERNSHIPS"),
        (saved_count, "SAVED OPPORTUNITIES"),
        (source_count, "CONNECTED SOURCES"),
    ]

    cols = st.columns(4)

    for col, (number, label) in zip(cols, metrics):

        with col:

            st.markdown(
                f"""
                <div class='metric-card'>
                    <div class='metric-number'>{number:,}</div>
                    <div class='metric-label'>{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.write("")

    st.markdown("### Find opportunities that fit you")

    search = st.text_input(
        "Search",
        placeholder=(
            "Search role, company, location or skill "
            "— e.g. Python Developer"
        ),
        label_visibility="collapsed",
    )

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        region_filter = st.selectbox(
            "Location priority",
            [
                "India first",
                "Worldwide remote",
                "All locations"
            ]
        )

    with f2:
        type_filter = st.selectbox(
            "Opportunity type",
            [
                "All opportunities",
                "Internships only",
                "Jobs only"
            ]
        )

    with f3:
        level_filter = st.selectbox(
            "Experience level",
            [
                "Students & freshers",
                "All experience levels"
            ]
        )

    with f4:

        source_options = ["All"] + sorted({
            safe_text(j.get("source"), "")
            for j in all_jobs if j.get("source")
        })

        selected_source = st.selectbox(
            "Source",
            source_options
        )

    fields = st.multiselect(
        "Career fields",
        [
            "All fields",
            "AI / Machine Learning",
            "Python",
            "Data Science",
            "Software Development",
            "Cybersecurity",
            "Web Development",
            "Cloud / DevOps"
        ],
        default=["All fields"],
    )

    filtered_jobs = []

    for job in all_jobs:

        title = safe_text(job.get("title"), "").lower()
        company = safe_text(job.get("company"), "").lower()
        location = safe_text(job.get("location"), "").lower()
        description = safe_text(job.get("description"), "").lower()
        skills = safe_text(job.get("skills"), "").lower()

        searchable = " ".join([
            title, company, location, description, skills
        ])

        if search.strip() and search.strip().lower() not in searchable:
            continue

        if type_filter == "Internships only" and not is_internship(job):
            continue

        if type_filter == "Jobs only" and is_internship(job):
            continue

        if level_filter == "Students & freshers" and not is_entry_level(job):
            continue

        if selected_source != "All" and safe_text(
            job.get("source"), ""
        ) != selected_source:
            continue

        if not matches_field(job, fields):
            continue

        if region_filter == "Worldwide remote":

            if get_location_group(job) not in [
                "Worldwide", "Remote"
            ]:
                continue

        filtered_jobs.append(job)

    if region_filter == "India first":

        filtered_jobs.sort(
            key=lambda j: (
                0 if get_location_group(j) == "India"
                else 1 if get_location_group(j) in [
                    "Worldwide", "Remote"
                ]
                else 2,
                safe_text(j.get("title"), "").lower(),
            )
        )

    st.markdown(
        f"""
        <div style='margin:12px 0 16px;color:#b7cbe2'>
            <b style='color:#fff'>{len(filtered_jobs):,}</b>
            matching opportunities
            <span class='small-note'>
                · Data from your connected sources
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not all_jobs:

        st.info(
            "Your opportunities database is empty. "
            "Select Fetch latest to retrieve listings."
        )

    elif not filtered_jobs:

        st.info(
            "No matching opportunities found. "
            "Try a broader search or change your filters."
        )

    else:

        for index, job in enumerate(filtered_jobs):
            render_job(job, index)


# ----------------------- SAVED OPPORTUNITIES -----------------------

elif page == "Saved opportunities":

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">YOUR PERSONAL COLLECTION</div>
        <div class="hero-title" style="font-size:42px">
            Saved <span>Opportunities.</span>
        </div>
        <div class="hero-sub">
            Keep promising roles in one place and track your application progress.
        </div>
    </div>
    """, unsafe_allow_html=True)

    saved_jobs = get_saved_jobs()

    st.write("")

    st.caption(
        f"{len(saved_jobs)} saved opportunities"
    )

    if not saved_jobs:

        st.info(
            "Your saved list is empty. Open Discover and "
            "select ☆ Save job on an opportunity."
        )

    else:

        for index, job in enumerate(saved_jobs):
            render_job(job, index, saved_page=True)


# ----------------------------- ABOUT -------------------------------

else:

    st.markdown("""
    <div class="hero">
        <div class="eyebrow">JOBS • INTERNSHIPS • YOUR FUTURE</div>
        <div class="hero-title" style="font-size:42px">
            Every Opportunity.<br><span>One Dashboard.</span>
        </div>
        <div class="hero-sub">
            CareerRadar AI is a student-focused opportunity discovery
            dashboard designed to make job and internship searching more organized.
        </div>
        <div class="creator">
            <div class="creator-label">PROUDLY CREATED BY</div>
            <div class="creator-name">PRIYANSHI MISHRA</div>
            <div class="creator-role">AI & ML Student • Developer</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### What CareerRadar includes")

    st.markdown("""
    - Opportunity fetching through your existing job fetcher.
    - Persistent job storage through your SQLite database.
    - Search by role, company, location and skills.
    - Filters for internships, jobs, experience level, source and career field.
    - India-first sorting with a separate worldwide remote view.
    - Saved opportunities and application-status updates.
    - Direct links to original job listings.
    - Automatic job fetching every 30 minutes.
    """)

    st.warning(
        "CareerRadar displays listings from the sources configured "
        "in your project. It cannot guarantee every job or internship "
        "available in India. Always verify eligibility, deadline, "
        "stipend and application details on the original source."
    )


# ------------------------------ FOOTER ------------------------------

st.divider()

st.markdown(
    "<div style='text-align:center;color:#7894b5;font-size:11px'>"
    "CAREERRADAR AI · OPPORTUNITY INTELLIGENCE · "
    "PROUDLY CREATED BY PRIYANSHI MISHRA"
    "</div>",
    unsafe_allow_html=True,
)
