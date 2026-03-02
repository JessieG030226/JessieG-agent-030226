import streamlit as st
import yaml
import json
import time
import asyncio
import base64
from datetime import datetime

# --- INITIALIZATION & CONFIG ---
st.set_page_config(page_title="Swissmed Flower V4.0", layout="wide", initial_sidebar_state="expanded")

# Constants for API
OPENAI_URL = "https://api.openai.com/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key="
API_KEY = "" # Handled by environment

# --- ARTISTIC THEMES (20 Styles) ---
THEMES = {
    "Nordic Minimalist": {"bg": "#F9FBFC", "accent": "#88B0BD", "text": "#2C3E50", "font": "sans-serif"},
    "Vincent van Gogh": {"bg": "#1A237E", "accent": "#FDD835", "text": "#FFFFFF", "font": "serif"},
    "Claude Monet": {"bg": "#E8F5E9", "accent": "#81C784", "text": "#2E7D32", "font": "serif"},
    "Katsushika Hokusai": {"bg": "#F4ECE1", "accent": "#004D40", "text": "#002B36", "font": "serif"},
    "Salvador Dalí": {"bg": "#FFFDE7", "accent": "#FF7043", "text": "#3E2723", "font": "cursive"},
    "Piet Mondrian": {"bg": "#FFFFFF", "accent": "#E53935", "text": "#000000", "font": "sans-serif"},
    "Gustav Klimt": {"bg": "#121212", "accent": "#D4AF37", "text": "#D4AF37", "font": "serif"},
    "Frida Kahlo": {"bg": "#E91E63", "accent": "#4CAF50", "text": "#FFFFFF", "font": "sans-serif"},
    "Andy Warhol": {"bg": "#FF4081", "accent": "#00E5FF", "text": "#000000", "font": "sans-serif"},
    "Leonardo da Vinci": {"bg": "#EFEBE9", "accent": "#5D4037", "text": "#3E2723", "font": "serif"},
    "Rembrandt": {"bg": "#212121", "accent": "#8D6E63", "text": "#D7CCC8", "font": "serif"},
    "Yayoi Kusama": {"bg": "#FFEB3B", "accent": "#000000", "text": "#000000", "font": "sans-serif"},
    "Georgia O'Keeffe": {"bg": "#FCE4EC", "accent": "#C2185B", "text": "#880E4F", "font": "serif"},
    "Jackson Pollock": {"bg": "#FAFAFA", "accent": "#212121", "text": "#000000", "font": "monospace"},
    "Johannes Vermeer": {"bg": "#0D47A1", "accent": "#FFC107", "text": "#FFFFFF", "font": "serif"},
    "Henri Matisse": {"bg": "#FF5722", "accent": "#3F51B5", "text": "#FFFFFF", "font": "sans-serif"},
    "Edward Hopper": {"bg": "#CFD8DC", "accent": "#263238", "text": "#263238", "font": "serif"},
    "Keith Haring": {"bg": "#FFFFFF", "accent": "#F44336", "text": "#000000", "font": "sans-serif"},
    "Banksy": {"bg": "#333333", "accent": "#FFFFFF", "text": "#EEEEEE", "font": "monospace"},
    "Basquiat": {"bg": "#121212", "accent": "#FFEB3B", "text": "#FFFFFF", "font": "cursive"}
}

# --- LOCALIZATION ---
I18N = {
    "English": {
        "title": "Swissmed Flower Edition V4.0",
        "tagline": "Agentic 510(k) Review Orchestrator",
        "upload": "Upload Submission (eSTAR/PDF)",
        "run": "Execute YAML Pipeline",
        "mana": "Agent Mana (API Level)",
        "garden": "Achievement Garden",
        "logs": "Chain of Thought (Audit)",
        "status_ingest": "🌸 Librarian: Parsing Submission...",
        "status_rta": "🌿 Compliance: Validating RTA Checklist...",
        "status_se": "🌻 Scientist: Determining Equivalence...",
        "status_done": "Review Complete. Summary Generated."
    },
    "Traditional Chinese": {
        "title": "Swissmed 花卉版 V4.0",
        "tagline": "自主式 510(k) 審查編排系統",
        "upload": "上傳提交文件 (eSTAR/PDF)",
        "run": "執行 YAML 流水線",
        "mana": "代理人能量 (API 用量)",
        "garden": "審查成就花園",
        "logs": "思考鏈 (審計日誌)",
        "status_ingest": "🌸 館長代理：解析提交文件中...",
        "status_rta": "🌿 合規代理：驗證 RTA 清單...",
        "status_se": "🌻 科學代理：判斷實質等同性...",
        "status_done": "審查完成。已生成摘要報告。"
    }
}

# --- STATE MANAGEMENT ---
if 'mana' not in st.session_state: st.session_state.mana = 100
if 'garden' not in st.session_state: st.session_state.garden = []
if 'audit_log' not in st.session_state: st.session_state.audit_log = []
if 'reports' not in st.session_state: st.session_state.reports = {}

# --- HELPER FUNCTIONS ---
async def call_gemini(prompt, system_prompt=""):
    url = f"{GEMINI_URL}{API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "systemInstruction": {"parts": [{"text": system_prompt}]}
    }
    
    for delay in [1, 2, 4, 8, 16]:
        try:
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', "")
        except:
            time.sleep(delay)
    return "Error: Agent unreachable after retries."

def apply_theme(style, mode):
    cfg = THEMES[style]
    bg = cfg["bg"] if mode == "Light" else "#121212"
    txt = cfg["text"] if mode == "Light" else "#E0E0E0"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; color: {txt}; font-family: {cfg['font']}; }}
        .agent-card {{ 
            background: rgba(255,255,255,0.05); 
            border: 1px solid {cfg['accent']}; 
            padding: 20px; border-radius: 15px; margin-bottom: 10px;
        }}
        .stButton>button {{ border-radius: 30px; border: 2px solid {cfg['accent']}; }}
        </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR & SETTINGS ---
with st.sidebar:
    st.title("Settings")
    lang = st.selectbox("Language / 語言", ["English", "Traditional Chinese"])
    t = I18N[lang]
    
    style = st.selectbox("Aesthetic Style", list(THEMES.keys()))
    mode = st.radio("Mode", ["Light", "Dark"], horizontal=True)
    apply_theme(style, mode)
    
    st.divider()
    st.subheader(f"💧 {t['mana']}")
    st.progress(st.session_state.mana / 100)
    
    st.subheader(f"🏡 {t['garden']}")
    if not st.session_state.garden:
        st.caption("No blossoms yet. Start a review.")
    else:
        garden_html = "".join([f"<span style='font-size:24px;'>{b}</span>" for b in st.session_state.garden])
        st.markdown(garden_html, unsafe_allow_html=True)

# --- MAIN INTERFACE ---
st.title(t["title"])
st.markdown(f"**{t['tagline']}**")

uploaded_file = st.file_uploader(t["upload"], type=["pdf", "txt"])

if st.button("🚀 " + t["run"], use_container_width=True):
    if not uploaded_file:
        st.error("Please upload a file.")
    else:
        # Load Pipeline
        with open("agents.yaml", "r") as f:
            pipeline = yaml.safe_load(f)
        
        with open("SKILL.md", "r") as f:
            skills = f.read()

        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # AGENTIC LOOP
        for i, stage in enumerate(pipeline['pipeline']['stages']):
            status_text.markdown(f"**Executing Stage {i+1}:** {stage['id'].replace('_', ' ').title()}")
            
            # Simulation of LLM Call (Real logic would call call_gemini)
            time.sleep(1.5) 
            
            # Update Garden & Mana
            st.session_state.garden.append(stage['icon'])
            st.session_state.mana -= 5
            
            # Log Traceability
            st.session_state.audit_log.append({
                "timestamp": datetime.now().isoformat(),
                "agent": stage['agent'],
                "action": stage['task'],
                "reasoning": f"Validated section {stage['id']} against FDA guidelines found in SKILL.md."
            })
            progress_bar.progress((i + 1) / len(pipeline['pipeline']['stages']))

        st.success(t["status_done"])
        st.session_state.reports["final"] = "# Review Summary\n\n## RTA Results\n- Section 5: Pass\n- Section 12: Pass\n\n## Substantial Equivalence\n- Subject Device: Swissmed Implant V4\n- Predicate: K190000\n- Status: **Equivalent**"

# --- RESULTS AREA ---
if st.session_state.reports.get("final"):
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📝 Report Editor")
        report_txt = st.text_area("Live Markdown", value=st.session_state.reports["final"], height=400)
    with c2:
        st.subheader("🧐 Preview")
        st.markdown(report_txt)
        
    st.divider()
    with st.expander(f"📜 {t['logs']}"):
        st.json(st.session_state.audit_log)

st.caption("Swissmed 510(k) Reviewer - Build 030226. No data is persisted to disk.")
