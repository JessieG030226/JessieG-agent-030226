import os
import streamlit as st
import yaml
import time
from datetime import datetime
import pandas as pd

# Try importing Gemini SDK safely
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# --- INITIALIZATION & CONFIG ---
st.set_page_config(page_title="Swissmed Flower V4.0", layout="wide", initial_sidebar_state="expanded")

# --- API KEY HANDLING (Streamlit Secrets Compatible) ---
# It will first look in st.secrets, then OS env, then fallback to empty
if 'user_api_key' not in st.session_state:
    if "GEMINI_API_KEY" in st.secrets:
        st.session_state.user_api_key = st.secrets["GEMINI_API_KEY"]
    else:
        st.session_state.user_api_key = os.environ.get("GEMINI_API_KEY", "")

MODELS = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 3 Flash Preview": "gemini-3-flash-preview"
}

# --- ARTISTIC THEMES ---
THEMES = {
    "Nordic Minimalist": {"bg": "#F9FBFC", "accent": "#88B0BD", "text": "#2C3E50", "font": "sans-serif"},
    "Vincent van Gogh": {"bg": "#1A237E", "accent": "#FDD835", "text": "#FFFFFF", "font": "serif"},
    "Claude Monet": {"bg": "#E8F5E9", "accent": "#81C784", "text": "#2E7D32", "font": "serif"},
    "Leonardo da Vinci": {"bg": "#EFEBE9", "accent": "#5D4037", "text": "#3E2723", "font": "serif"}
}

# Localized UI Content
I18N = {
    "English": {
        "title": "Swissmed Flower V4.0",
        "tab_review": "🚀 Live Review",
        "tab_mgmt": "🤖 Agent Hub",
        "tab_logs": "📜 Audit Logs",
        "tab_dash": "📊 Blossom Dashboard",
        "btn_run": "Execute Pipeline"
    }
}

# --- SESSION STATE ---
if 'agents_yaml' not in st.session_state:
    st.session_state.agents_yaml = {
        "pipeline": {
            "version": "4.0",
            "stages": [
                {"id": "rta", "agent": "RTA Admin", "icon": "🌿", "task": "Completeness check.", "status": "Ready", "phase": "RTA"},
                {"id": "software", "agent": "Software Analyst", "icon": "💻", "task": "Software LOC verification.", "status": "Ready", "phase": "Technical"},
                {"id": "cyber", "agent": "Cyber Auditor", "icon": "🛡️", "task": "SBOM review.", "status": "Ready", "phase": "Technical"}
            ]
        }
    }
if 'mana' not in st.session_state: st.session_state.mana = 100
if 'garden' not in st.session_state: st.session_state.garden = []
if 'report_md' not in st.session_state: st.session_state.report_md = "# Regulatory Summary\n\n*Awaiting submission...*"
if 'audit_trail' not in st.session_state: st.session_state.audit_trail = []

# --- UTILITY FUNCTIONS ---
def apply_theme(style_key, mode):
    cfg = THEMES.get(style_key, THEMES["Nordic Minimalist"])
    is_dark = mode == "Dark"
    bg = cfg["bg"] if not is_dark else "#121212"
    txt = cfg["text"] if not is_dark else "#EAEAEA"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; color: {txt}; font-family: {cfg['font']}; }}
        .agent-card {{
            background: rgba(255, 255, 255, 0.05); border-left: 5px solid {cfg['accent']};
            padding: 15px; border-radius: 10px; margin-bottom: 10px;
        }}
        .status-pill {{ font-size: 0.8em; padding: 2px 8px; border-radius: 10px; background: {cfg['accent']}; color: {bg}; }}
        </style>
    """, unsafe_allow_html=True)

def gemini_call(prompt, model_id):
    if not HAS_GENAI: return "Error: Google SDK missing."
    if not st.session_state.user_api_key: return "Error: Missing API Key."
    try:
        genai.configure(api_key=st.session_state.user_api_key)
        model = genai.GenerativeModel(MODELS[model_id])
        return model.generate_content(prompt).text
    except Exception as e:
        return f"API Error: {str(e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.title("Swissmed Control")
    current_key = st.text_input("Gemini API Key", value=st.session_state.user_api_key, type="password")
    if current_key: st.session_state.user_api_key = current_key
    
    sel_lang = st.selectbox("Language", ["English"])
    t = I18N[sel_lang]
    
    sel_style = st.selectbox("Theme", list(THEMES.keys()))
    sel_mode = st.radio("Mode", ["Light", "Dark"], horizontal=True)
    apply_theme(sel_style, sel_mode)
    
    target_model = st.selectbox("LLM Primary", list(MODELS.keys()))

# --- HEADER & TABS ---
st.title(t["title"])
tab_dash, tab_rev, tab_mg, tab_au = st.tabs([t["tab_dash"], t["tab_review"], t["tab_mgmt"], t["tab_logs"]])

# --- TAB: DASHBOARD ---
with tab_dash:
    stages = st.session_state.agents_yaml["pipeline"]["stages"]
    cols = st.columns(3)
    for idx, s in enumerate(stages):
        with cols[idx % 3]:
            st.markdown(f"""
            <div class="agent-card">
                <b>{s['icon']} {s['agent']}</b><br>
                <span class="status-pill">{s['status']}</span><br>
                <small>{s['task']}</small>
            </div>
            """, unsafe_allow_html=True)

# --- TAB: LIVE REVIEW ---
with tab_rev:
    c1, c2 = st.columns([1, 1])
    with c1:
        file = st.file_uploader("Upload 510(k) Document")
        if file and st.button("🔮 Run AI Risk Pre-Assessment"):
            with st.spinner("Analyzing..."):
                res = gemini_call(f"Assess document: {file.name}", target_model)
                st.info(res)
        
        st.divider()
        if st.button("🚀 " + t["btn_run"]):
            if not file: st.warning("Upload a file first.")
            else:
                with st.status("Executing Pipeline..."):
                    for s in stages:
                        st.write(f"Running {s['agent']}...")
                        time.sleep(0.5)
                        if s['icon'] not in st.session_state.garden: st.session_state.garden.append(s['icon'])
                        st.session_state.audit_trail.append({"Agent": s['agent'], "Phase": s['phase']})
                    st.session_state.report_md = f"# Review: {file.name}\nCompleted."

    with c2:
        st.text_area("Live Report Editor", value=st.session_state.report_md, height=400, key="report_editor_box")

# --- TAB: MANAGEMENT ---
with tab_mg:
    if st.button("✨ AI Optimize YAML Configuration"):
        with st.spinner("Analyzing YAML..."):
            yaml_str = yaml.dump(st.session_state.agents_yaml)
            res = gemini_call(f"Suggest improvements for this agent config:\n{yaml_str}", target_model)
            st.success(res)
    st.text_area("YAML Config", yaml.dump(st.session_state.agents_yaml), height=300)

# --- TAB: LOGS ---
with tab_au:
    if st.session_state.audit_trail:
        st.dataframe(pd.DataFrame(st.session_state.audit_trail), use_container_width=True)

if st.session_state.garden:
    st.markdown(f"### 🌸 Achievement Blossoms: {' '.join(st.session_state.garden)}")
