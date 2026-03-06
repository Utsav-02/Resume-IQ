import streamlit as st
import requests
import json
import os

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="ResumeIQ — AI Career Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;500;600;700;800&family=DM+Mono:wght@300;400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f !important;
    color: #e8e6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

[data-testid="stSidebar"] {
    background: #0f0f1a !important;
    border-right: 1px solid #1e1e2e !important;
}

[data-testid="stSidebar"] * { color: #c4c2d4 !important; }

/* ── Hide Streamlit Branding ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none; }

/* ── Main Header ── */
.hero {
    position: relative;
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 16px;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(99,102,241,0.15) 0%, transparent 70%);
    pointer-events: none;
}
.hero::after {
    content: '';
    position: absolute;
    bottom: -40px; left: 30%;
    width: 200px; height: 200px;
    background: radial-gradient(circle, rgba(16,185,129,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #6366f1;
    border: 1px solid rgba(99,102,241,0.3);
    padding: 4px 12px;
    border-radius: 4px;
    margin-bottom: 1rem;
    background: rgba(99,102,241,0.05);
}
.hero h1 {
    font-family: 'Syne', sans-serif !important;
    font-size: 2.8rem !important;
    font-weight: 800 !important;
    line-height: 1.1 !important;
    margin: 0 0 0.75rem 0 !important;
    color: #f0eeff !important;
    letter-spacing: -0.02em !important;
}
.hero h1 span { color: #6366f1; }
.hero p {
    font-size: 1rem !important;
    color: #6b6880 !important;
    margin: 0 !important;
    max-width: 520px;
}

/* ── Status Pill ── */
.status-online {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(16,185,129,0.1);
    border: 1px solid rgba(16,185,129,0.25);
    color: #10b981 !important;
    padding: 5px 12px; border-radius: 20px;
    font-family: 'DM Mono', monospace; font-size: 0.72rem;
    letter-spacing: 0.05em;
}
.status-online::before { content: '●'; font-size: 0.6rem; }
.status-offline {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(239,68,68,0.1);
    border: 1px solid rgba(239,68,68,0.25);
    color: #ef4444 !important;
    padding: 5px 12px; border-radius: 20px;
    font-family: 'DM Mono', monospace; font-size: 0.72rem;
}
.status-offline::before { content: '●'; font-size: 0.6rem; }

/* ── Section Labels ── */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a4860;
    margin-bottom: 0.75rem;
    display: flex; align-items: center; gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #1e1e2e;
}

/* ── Cards ── */
.card {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 12px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    transition: border-color 0.2s;
}
.card:hover { border-color: #2e2e4e; }

.summary-card {
    background: linear-gradient(135deg, #0f0f1a 0%, #13132a 100%);
    border: 1px solid #1e1e2e;
    border-left: 3px solid #6366f1;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin-bottom: 1.5rem;
    font-size: 0.92rem;
    color: #a8a6c4;
    line-height: 1.7;
}

/* ── Stat Boxes ── */
.stat-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
.stat-box {
    flex: 1;
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    text-align: center;
}
.stat-value {
    font-family: 'Syne', sans-serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #f0eeff;
    line-height: 1;
    margin-bottom: 4px;
}
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #4a4860;
}

/* ── Tags ── */
.tags-row { display: flex; flex-wrap: wrap; gap: 6px; margin: 0.5rem 0 1rem 0; }
.tag {
    font-family: 'DM Mono', monospace;
    font-size: 0.72rem;
    padding: 4px 10px;
    border-radius: 6px;
    letter-spacing: 0.02em;
}
.tag-tech { background: rgba(99,102,241,0.1); color: #818cf8; border: 1px solid rgba(99,102,241,0.2); }
.tag-soft { background: rgba(139,92,246,0.1); color: #a78bfa; border: 1px solid rgba(139,92,246,0.2); }
.tag-missing { background: rgba(239,68,68,0.08); color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
.tag-match { background: rgba(16,185,129,0.08); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
.tag-keyword { background: rgba(251,191,36,0.08); color: #fbbf24; border: 1px solid rgba(251,191,36,0.2); }

/* ── Job Match Card ── */
.job-card {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.job-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.job-card.high::before { background: linear-gradient(90deg, #10b981, #34d399); }
.job-card.medium::before { background: linear-gradient(90deg, #f59e0b, #fbbf24); }
.job-card.low::before { background: linear-gradient(90deg, #ef4444, #f87171); }

.job-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.2rem;
    font-weight: 700;
    color: #f0eeff;
    margin-bottom: 2px;
}
.job-company {
    font-family: 'DM Mono', monospace;
    font-size: 0.75rem;
    color: #4a4860;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.score-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 8px;
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
}
.score-high { background: rgba(16,185,129,0.1); color: #10b981; border: 1px solid rgba(16,185,129,0.25); }
.score-medium { background: rgba(245,158,11,0.1); color: #f59e0b; border: 1px solid rgba(245,158,11,0.25); }
.score-low { background: rgba(239,68,68,0.1); color: #ef4444; border: 1px solid rgba(239,68,68,0.25); }

/* ── Score Bar ── */
.score-bar-bg {
    height: 4px;
    background: #1e1e2e;
    border-radius: 2px;
    margin: 0.75rem 0;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 0.8s ease;
}

/* ── Recommendation Box ── */
.rec-box {
    background: rgba(99,102,241,0.05);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 10px;
    padding: 1rem 1.25rem;
    font-size: 0.88rem;
    color: #a8a6c4;
    line-height: 1.7;
    margin-top: 1rem;
}
.rec-box strong {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #6366f1;
    display: block;
    margin-bottom: 6px;
}

/* ── Upload Zone ── */
[data-testid="stFileUploader"] {
    background: #0f0f1a !important;
    border: 1px dashed #2e2e4e !important;
    border-radius: 12px !important;
    padding: 1rem !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: #6366f1 !important;
}

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 8px !important;
    color: #e8e6f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 2px rgba(99,102,241,0.15) !important;
}

/* ── Buttons ── */
[data-testid="baseButton-primary"] {
    background: #6366f1 !important;
    border: none !important;
    color: #fff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    border-radius: 8px !important;
    letter-spacing: 0.01em !important;
    transition: all 0.2s !important;
}
[data-testid="baseButton-primary"]:hover {
    background: #4f46e5 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.3) !important;
}
[data-testid="baseButton-secondary"] {
    background: transparent !important;
    border: 1px solid #2e2e4e !important;
    color: #a8a6c4 !important;
    font-family: 'DM Sans', sans-serif !important;
    border-radius: 8px !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    background: #0f0f1a !important;
    border-bottom: 1px solid #1e1e2e !important;
    gap: 0 !important;
    padding: 0 !important;
}
[data-testid="stTabs"] [role="tab"] {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
    color: #4a4860 !important;
    padding: 0.75rem 1.25rem !important;
    border-radius: 0 !important;
    border-bottom: 2px solid transparent !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #6366f1 !important;
    border-bottom-color: #6366f1 !important;
    background: transparent !important;
}

/* ── Expander ── */
[data-testid="stExpander"] {
    background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 10px !important;
    margin-bottom: 0.75rem !important;
}
[data-testid="stExpander"]:hover { border-color: #2e2e4e !important; }

/* ── Divider ── */
hr { border-color: #1e1e2e !important; }

/* ── Alerts ── */
[data-testid="stAlert"] {
    background: #0f0f1a !important;
    border-radius: 8px !important;
}

/* ── Metrics ── */
[data-testid="stMetric"] {
    background: #0f0f1a !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 10px !important;
    padding: 1rem !important;
}
[data-testid="stMetricLabel"] { color: #4a4860 !important; font-family: 'DM Mono', monospace !important; font-size: 0.7rem !important; text-transform: uppercase !important; letter-spacing: 0.1em !important; }
[data-testid="stMetricValue"] { color: #f0eeff !important; font-family: 'Syne', sans-serif !important; }

/* ── Sidebar nav ── */
.sidebar-nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 0.6rem 0.75rem;
    border-radius: 8px;
    font-size: 0.85rem;
    color: #6b6880;
    margin-bottom: 4px;
    cursor: pointer;
    transition: all 0.15s;
}
.sidebar-nav-item:hover { background: #1a1a2e; color: #c4c2d4; }
.sidebar-nav-item.active { background: rgba(99,102,241,0.1); color: #818cf8; }

/* ── Steps ── */
.step {
    display: flex; align-items: flex-start; gap: 1rem;
    margin-bottom: 1rem;
}
.step-num {
    width: 24px; height: 24px;
    background: rgba(99,102,241,0.15);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    color: #6366f1;
    flex-shrink: 0;
    margin-top: 2px;
}
.step-text { font-size: 0.85rem; color: #6b6880; line-height: 1.5; }
.step-text strong { color: #c4c2d4; font-weight: 500; }

/* ── File info bar ── */
.file-bar {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(99,102,241,0.05);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 8px;
    padding: 0.75rem 1rem;
    margin: 0.75rem 0;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #818cf8;
}
.file-bar span { color: #4a4860; }

/* ── Bullet compare ── */
.bullet-box {
    background: #0f0f1a;
    border: 1px solid #1e1e2e;
    border-radius: 10px;
    padding: 1.25rem;
}
.bullet-box.original { border-left: 3px solid #4a4860; }
.bullet-box.improved { border-left: 3px solid #10b981; }
.bullet-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.75rem;
}
.bullet-label.orig { color: #4a4860; }
.bullet-label.impr { color: #10b981; }
.bullet-text { font-size: 0.92rem; color: #a8a6c4; line-height: 1.6; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: #0a0a0f; }
::-webkit-scrollbar-thumb { background: #2e2e4e; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ── Hero Header ───────────────────────────────────────────────────────────────

st.markdown("""
<div class="hero">
    <div class="hero-badge">⚡ AI-Powered Career Intelligence</div>
    <h1>Resume<span>IQ</span></h1>
    <p>Extract skills, identify gaps, match jobs — get hired faster with AI-driven insights.</p>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown('<div class="section-label">Profile</div>', unsafe_allow_html=True)
    user_name = st.text_input("Name", value="Demo User", label_visibility="collapsed",
                               placeholder="Your name")
    user_email = st.text_input("Email", value="demo@example.com", label_visibility="collapsed",
                                placeholder="your@email.com")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">System</div>', unsafe_allow_html=True)

    try:
        r = requests.get(f"{API_URL}/", timeout=3)
        if r.status_code == 200:
            st.markdown('<span class="status-online">API Online</span>', unsafe_allow_html=True)
        else:
            st.markdown('<span class="status-offline">API Error</span>', unsafe_allow_html=True)
    except:
        st.markdown('<span class="status-offline">API Offline</span>', unsafe_allow_html=True)
        st.caption("Run: `uvicorn backend.main:app --reload`")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">How it works</div>', unsafe_allow_html=True)

    steps = [
        ("Upload", "your resume (PDF/DOCX/TXT)"),
        ("Extract", "AI identifies all your skills"),
        ("Match", "compare against job listings"),
        ("Analyse", "see gaps and missing skills"),
        ("Apply", "with targeted keywords"),
    ]
    for i, (bold, rest) in enumerate(steps, 1):
        st.markdown(f"""
        <div class="step">
            <div class="step-num">{i}</div>
            <div class="step-text"><strong>{bold}</strong> {rest}</div>
        </div>
        """, unsafe_allow_html=True)

# ── Session State ─────────────────────────────────────────────────────────────

for key in ["resume_id", "skills_data", "match_results"]:
    if key not in st.session_state:
        st.session_state[key] = None

# ── Tabs ──────────────────────────────────────────────────────────────────────

tab1, tab2, tab3, tab4 = st.tabs(["◈  Upload Resume", "◎  Job Matches", "＋  Add Jobs", "⌘  Improve Bullets"])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — UPLOAD
# ════════════════════════════════════════════════════════════════════════════

with tab1:
    st.markdown('<div class="section-label">Resume Upload</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Drop your resume here or click to browse",
        type=["pdf", "docx", "txt"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.markdown(f"""
        <div class="file-bar">
            <div>◈ {uploaded_file.name}</div>
            <span>{uploaded_file.size / 1024:.1f} KB</span>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⚡ Analyse Resume", type="primary", use_container_width=True):
            with st.spinner("Extracting skills with AI..."):
                try:
                    response = requests.post(
                        f"{API_URL}/upload-resume/",
                        files={"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)},
                        data={"user_name": user_name, "user_email": user_email},
                        timeout=60
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.resume_id = data["resume_id"]
                        st.session_state.skills_data = data["skills"]
                        st.session_state.match_results = None
                        st.success(f"Resume analysed — ID #{data['resume_id']}")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
                except requests.exceptions.ConnectionError:
                    st.error("Cannot reach backend. Is uvicorn running?")
                except Exception as e:
                    st.error(str(e))

    if st.session_state.skills_data:
        sd = st.session_state.skills_data

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-label">Profile Summary</div>', unsafe_allow_html=True)

        if sd.get("summary"):
            st.markdown(f'<div class="summary-card">{sd["summary"]}</div>', unsafe_allow_html=True)

        # Stats
        tech_count = len(sd.get("technical_skills", []))
        soft_count = len(sd.get("soft_skills", []))
        exp = sd.get("experience_years", "—")
        cert_count = len(sd.get("certifications", []))

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Experience", f"{exp} yrs" if str(exp).isdigit() else exp)
        with col2:
            st.metric("Technical Skills", tech_count)
        with col3:
            st.metric("Soft Skills", soft_count)
        with col4:
            st.metric("Certifications", cert_count)

        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)

        with col1:
            st.markdown('<div class="section-label">Technical Skills</div>', unsafe_allow_html=True)
            tech_skills = sd.get("technical_skills", [])
            if tech_skills:
                tags = "".join([f'<span class="tag tag-tech">{s}</span>' for s in tech_skills])
                st.markdown(f'<div class="tags-row">{tags}</div>', unsafe_allow_html=True)
            else:
                st.caption("None detected")

            st.markdown('<div class="section-label">Education</div>', unsafe_allow_html=True)
            for edu in sd.get("education", []):
                st.markdown(f'<div style="color:#a8a6c4;font-size:0.88rem;margin-bottom:4px;">· {edu}</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="section-label">Soft Skills</div>', unsafe_allow_html=True)
            soft_skills = sd.get("soft_skills", [])
            if soft_skills:
                tags = "".join([f'<span class="tag tag-soft">{s}</span>' for s in soft_skills])
                st.markdown(f'<div class="tags-row">{tags}</div>', unsafe_allow_html=True)
            else:
                st.caption("None detected")

            st.markdown('<div class="section-label">Previous Roles</div>', unsafe_allow_html=True)
            for title in sd.get("job_titles", []):
                st.markdown(f'<div style="color:#a8a6c4;font-size:0.88rem;margin-bottom:4px;">· {title}</div>', unsafe_allow_html=True)

            if sd.get("certifications"):
                st.markdown('<div class="section-label">Certifications</div>', unsafe_allow_html=True)
                for cert in sd["certifications"]:
                    st.markdown(f'<div style="color:#a8a6c4;font-size:0.88rem;margin-bottom:4px;">· {cert}</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("◎ Find Matching Jobs", type="primary", use_container_width=True):
            with st.spinner("Matching your profile against all jobs..."):
                try:
                    r = requests.post(f"{API_URL}/match-jobs/{st.session_state.resume_id}", timeout=120)
                    if r.status_code == 200:
                        st.session_state.match_results = r.json()
                        st.success("Matching complete — switch to the **Job Matches** tab.")
                    else:
                        st.error(f"Error: {r.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(str(e))

# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — JOB MATCHES
# ════════════════════════════════════════════════════════════════════════════

with tab2:
    if not st.session_state.match_results:
        st.markdown("""
        <div style="text-align:center;padding:4rem 2rem;color:#4a4860;">
            <div style="font-size:3rem;margin-bottom:1rem;">◎</div>
            <div style="font-family:'Syne',sans-serif;font-size:1.2rem;color:#6b6880;margin-bottom:0.5rem;">No matches yet</div>
            <div style="font-size:0.85rem;">Upload your resume and click "Find Matching Jobs"</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        matches = st.session_state.match_results.get("matches", [])
        valid = [m for m in matches if "error" not in m]

        st.markdown(f'<div class="section-label">{len(valid)} Jobs Ranked by Fit</div>', unsafe_allow_html=True)

        for i, job in enumerate(valid):
            score = job.get("match_score", 0)
            chance = job.get("apply_chance", "Unknown")
            pct = int(score * 100)

            level = "high" if score >= 0.7 else ("medium" if score >= 0.4 else "low")
            score_cls = f"score-{level}"

            if score >= 0.7:
                bar_color = "#10b981"
            elif score >= 0.4:
                bar_color = "#f59e0b"
            else:
                bar_color = "#ef4444"

            with st.expander(f"{'🟢' if score>=0.7 else '🟡' if score>=0.4 else '🔴'}  {job['title']}  ·  {job['company']}  —  {pct}%", expanded=(i==0)):

                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f'<div class="job-title">{job["title"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-company">{job["company"]}</div>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class="score-bar-bg">
                        <div class="score-bar-fill" style="width:{pct}%;background:{bar_color};"></div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="score-badge {score_cls}" style="margin-top:0.5rem;">{pct}% Match</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:0.7rem;color:#4a4860;margin-top:6px;text-align:center;">{chance} Chance</div>', unsafe_allow_html=True)

                c1, c2 = st.columns(2)

                with c1:
                    matching = job.get("matching_skills", [])
                    st.markdown('<div class="section-label">Matching Skills</div>', unsafe_allow_html=True)
                    if matching:
                        tags = "".join([f'<span class="tag tag-match">{s}</span>' for s in matching])
                        st.markdown(f'<div class="tags-row">{tags}</div>', unsafe_allow_html=True)
                    else:
                        st.caption("None matched")

                    missing = job.get("missing_skills", [])
                    st.markdown('<div class="section-label">Missing Skills</div>', unsafe_allow_html=True)
                    if missing:
                        tags = "".join([f'<span class="tag tag-missing">{s}</span>' for s in missing])
                        st.markdown(f'<div class="tags-row">{tags}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown('<span style="color:#10b981;font-size:0.85rem;">✓ No gaps — strong fit</span>', unsafe_allow_html=True)

                with c2:
                    keywords = job.get("keywords_to_add", [])
                    st.markdown('<div class="section-label">ATS Keywords to Add</div>', unsafe_allow_html=True)
                    if keywords:
                        tags = "".join([f'<span class="tag tag-keyword">{k}</span>' for k in keywords])
                        st.markdown(f'<div class="tags-row">{tags}</div>', unsafe_allow_html=True)

                    rec = job.get("recommendation", "")
                    if rec:
                        st.markdown(f'<div class="rec-box"><strong>AI Recommendation</strong>{rec}</div>', unsafe_allow_html=True)

                if job.get("source_url") and "example.com" not in job["source_url"]:
                    st.link_button("→ Apply Now", job["source_url"], use_container_width=True)

# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — ADD JOBS
# ════════════════════════════════════════════════════════════════════════════

with tab3:
    st.markdown('<div class="section-label">Add New Job Listing</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        job_title = st.text_input("Job Title *", placeholder="e.g. Senior Python Developer")
        job_company = st.text_input("Company *", placeholder="e.g. Google")
        job_url = st.text_input("Job URL", placeholder="https://...")
    with col2:
        job_skills = st.text_input("Required Skills", placeholder="Python, Django, PostgreSQL, Docker")
        job_description = st.text_area("Job Description *", height=175,
                                        placeholder="Paste the full job description here...")

    if st.button("＋ Add Job", type="primary"):
        if not job_title or not job_company or not job_description:
            st.error("Title, Company, and Description are required.")
        else:
            skills_list = [s.strip() for s in job_skills.split(",") if s.strip()] if job_skills else []
            try:
                r = requests.post(f"{API_URL}/jobs/", json={
                    "title": job_title, "company": job_company,
                    "description": job_description,
                    "required_skills": skills_list, "source_url": job_url
                }, timeout=10)
                if r.status_code == 200:
                    st.success(f"Job '{job_title}' added.")
                else:
                    st.error(f"Error: {r.json().get('detail')}")
            except Exception as e:
                st.error(str(e))

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Job Database</div>', unsafe_allow_html=True)

    try:
        r = requests.get(f"{API_URL}/jobs/", timeout=5)
        if r.status_code == 200:
            jobs = r.json()
            for job in jobs:
                with st.expander(f"{job['title']}  ·  {job['company']}"):
                    skills_str = ', '.join(job['required_skills']) if job['required_skills'] else 'Not specified'
                    st.markdown(f'<div style="font-family:\'DM Mono\',monospace;font-size:0.75rem;color:#6b6880;margin-bottom:8px;">{skills_str}</div>', unsafe_allow_html=True)
                    if job.get("source_url"):
                        st.caption(job["source_url"])
                    if st.button("Delete", key=f"del_{job['job_id']}"):
                        dr = requests.delete(f"{API_URL}/jobs/{job['job_id']}", timeout=5)
                        if dr.status_code == 200:
                            st.success("Removed.")
                            st.rerun()
    except Exception as e:
        st.error(f"Could not load jobs: {str(e)}")

# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — IMPROVE BULLETS
# ════════════════════════════════════════════════════════════════════════════

with tab4:
    st.markdown('<div class="section-label">AI Bullet Point Rewriter</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#6b6880;font-size:0.88rem;margin-bottom:1.5rem;">Paste a weak resume bullet and a job description. AI will rewrite it to be impactful, quantified, and ATS-optimised.</div>', unsafe_allow_html=True)

    bullet = st.text_area("Resume Bullet Point", placeholder="e.g. Worked on backend APIs using Python", height=90)
    jd = st.text_area("Target Job Description", placeholder="Paste the job description here...", height=160)

    if st.button("⌘ Rewrite Bullet", type="primary"):
        if not bullet or not jd:
            st.error("Both fields are required.")
        else:
            with st.spinner("Rewriting with AI..."):
                try:
                    r = requests.post(f"{API_URL}/improve-bullet/",
                                       json={"bullet_point": bullet, "job_description": jd}, timeout=30)
                    if r.status_code == 200:
                        data = r.json()
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"""
                            <div class="bullet-box original">
                                <div class="bullet-label orig">Before</div>
                                <div class="bullet-text">{data['original']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            st.markdown(f"""
                            <div class="bullet-box improved">
                                <div class="bullet-label impr">After — AI Enhanced</div>
                                <div class="bullet-text">{data['improved']}</div>
                            </div>
                            """, unsafe_allow_html=True)
                    else:
                        st.error(f"Error: {r.json().get('detail')}")
                except Exception as e:
                    st.error(str(e))

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown("""
<div style="margin-top:3rem;padding-top:1.5rem;border-top:1px solid #1e1e2e;
     text-align:center;font-family:'DM Mono',monospace;font-size:0.68rem;
     color:#2e2e4e;letter-spacing:0.1em;">
    RESUMEIQ  ·  FASTAPI + STREAMLIT  ·  AI-POWERED CAREER INTELLIGENCE
</div>
""", unsafe_allow_html=True)
