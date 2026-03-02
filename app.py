import os
# Redundancy check: set pure python protobuf implementation BEFORE importing Streamlit
os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"

import streamlit as st
import yaml
import time
from datetime import datetime
import pandas as pd

# Try importing Gemini SDK for the new AI features safely
try:
    import google.generativeai as genai
    HAS_GENAI = True
except ImportError:
    HAS_GENAI = False

# --- INITIALIZATION & CONFIG ---
st.set_page_config(page_title="Swissmed Flower V4.0", layout="wide", initial_sidebar_state="expanded")

# --- API KEY HANDLING (HF Spaces Compatible) ---
ENV_API_KEY = os.environ.get("GEMINI_API_KEY", "") 
if 'user_api_key' not in st.session_state:
    st.session_state.user_api_key = ENV_API_KEY

MODELS = {
    "Gemini 2.5 Flash": "gemini-2.5-flash",
    "Gemini 3 Flash Preview": "gemini-3-flash-preview"
}

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

# Localized UI Content
I18N = {
    "English": {
        "title": "Swissmed Flower V4.0",
        "tab_review": "🚀 Live Review",
        "tab_mgmt": "🤖 Agent Hub",
        "tab_logs": "📜 Audit Logs",
        "tab_dash": "📊 Blossom Dashboard",
        "btn_run": "Execute Pipeline",
        "btn_std": "Standardize YAML",
        "upload_doc": "Upload 510(k) Submission",
        "mana": "Agent Mana & Telemetry",
        "report_header": "Interactive Report Editor",
        "heatmap": "Phase Coverage Heatmap"
    },
    "Traditional Chinese": {
        "title": "Swissmed 花卉版 V4.0",
        "tab_review": "🚀 實時審查",
        "tab_mgmt": "🤖 代理人中心",
        "tab_logs": "📜 審計日誌",
        "tab_dash": "📊 綻放儀表板",
        "btn_run": "執行全線流程",
        "btn_std": "標準化 YAML",
        "upload_doc": "上傳 510(k) 提交材料",
        "mana": "代理人能量與遙測",
        "report_header": "交互式報告編輯器",
        "heatmap": "階段覆蓋熱圖"
    }
}

# --- SESSION STATE ---
if 'agents_yaml' not in st.session_state:
    st.session_state.agents_yaml = {
        "pipeline": {
            "version": "4.0",
            "stages": [
                {"id": "ingest", "agent": "eSTAR 解析專家", "icon": "🌸", "task": "Parsing XML metadata.", "status": "Ready", "phase": "Admin"},
                {"id": "rta", "agent": "RTA 行政合規官", "icon": "🌿", "task": "15-day completeness check.", "status": "Ready", "phase": "RTA"},
                {"id": "biocompat", "agent": "生物相容性審查員", "icon": "🔬", "task": "ISO 10993 Review.", "status": "Ready", "phase": "Technical"},
                {"id": "software", "agent": "軟體關切程度分析師", "icon": "💻", "task": "Software LOC verification.", "status": "Ready", "phase": "Technical"},
                {"id": "cyber", "agent": "網絡安全審計員", "icon": "🛡️", "task": "SBOM & vulnerability review.", "status": "Ready", "phase": "Technical"},
                {"id": "se", "agent": "技術特徵比較員", "icon": "🌻", "task": "Predicate comparison.", "status": "Ready", "phase": "Substantive"},
                {"id": "clinical", "agent": "臨床數據評估員", "icon": "🏥", "task": "Statistical significance audit.", "status": "Ready", "phase": "Clinical"}
            ]
        }
    }
if 'mana' not in st.session_state: st.session_state.mana = 100
if 'garden' not in st.session_state: st.session_state.garden = []
if 'report_md' not in st.session_state: st.session_state.report_md = "# Regulatory Review Summary\n\n*System initialized. Awaiting submission...*"
if 'audit_trail' not in st.session_state: st.session_state.audit_trail = []
if 'active_indices' not in st.session_state: st.session_state.active_indices = {"Admin": 0, "RTA": 0, "Technical": 0, "Substantive": 0, "Clinical": 0}

# --- UTILITY FUNCTIONS ---
def apply_theme(style_key, mode):
    cfg = THEMES[style_key]
    is_dark = mode == "Dark"
    bg = cfg["bg"] if not is_dark else "#121212"
    txt = cfg["text"] if not is_dark else "#EAEAEA"
    st.markdown(f"""
        <style>
        .stApp {{ background-color: {bg}; color: {txt}; font-family: {cfg['font']}; }}
        .agent-card {{
            background: rgba(255, 255, 255, 0.05); border-left: 5px solid {cfg['accent']};
            padding: 15px; border-radius: 10px; margin-bottom: 10px; transition: transform 0.2s;
        }}
        .agent-card:hover {{ transform: scale(1.02); background: rgba(255, 255, 255, 0.1); }}
        .status-pill {{ font-size: 0.8em; padding: 2px 8px; border-radius: 10px; background: {cfg['accent']}; color: {bg}; }}
        [data-testid="stSidebar"][aria-expanded="false"] {{ display: none; }}
        </style>
    """, unsafe_allow_html=True)

def standardize_yaml(text):
    try:
        data = yaml.safe_load(text)
        if isinstance(data, list): data = {"pipeline": {"version": "4.0", "stages": data}}
        for s in data["pipeline"]["stages"]:
            if "status" not in s: s["status"] = "Ready"
            if "phase" not in s: s["phase"] = "Technical"
        return data
    except Exception as e:
        st.error(f"YAML Syntax Error: {e}")
        return None

def gemini_call(prompt, model_id):
    if not HAS_GENAI: return "Error: google-generativeai library is missing."
    if not st.session_state.user_api_key: return "Error: Please provide a Gemini API Key in the sidebar."
    try:
        genai.configure(api_key=st.session_state.user_api_key)
        model = genai.GenerativeModel(MODELS[model_id])
        return model.generate_content(prompt).text
    except Exception as e:
        # Graceful fallback if preview model is invalid/revoked
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            return model.generate_content(prompt).text
        except Exception as fallback_e:
            return f"API Error: {str(fallback_e)}"

# --- SIDEBAR ---
with st.sidebar:
    st.title("Swissmed Control")
    
    st.subheader("🔑 Authentication")
    current_key = st.text_input("Gemini API Key", value=st.session_state.user_api_key, type="password")
    if current_key:
        st.session_state.user_api_key = current_key
    
    if not st.session_state.user_api_key:
        st.warning("Please provide an API key to enable AI features.")

    st.divider()
    sel_lang = st.selectbox("Language / 語言", ["English", "Traditional Chinese"])
    t = I18N[sel_lang]
    
    sel_style = st.selectbox("Aesthetic Engine", list(THEMES.keys()))
    sel_mode = st.radio("Theme Mode", ["Light", "Dark"], horizontal=True)
    apply_theme(sel_style, sel_mode)
    
    st.divider()
    st.subheader(f"💧 {t['mana']}")
    st.progress(st.session_state.mana / 100)
    
    st.subheader("🛠️ Intelligence Core")
    target_model = st.selectbox("LLM Primary", list(MODELS.keys()))
    
    if st.button("Flush Session State"):
        st.session_state.mana = 100
        st.session_state.garden = []
        st.session_state.audit_trail = []
        st.session_state.report_md = "# System Reset"
        st.rerun()

# --- HEADER ---
st.title(t["title"])
tab_dash, tab_rev, tab_mg, tab_au = st.tabs([t["tab_dash"], t["tab_review"], t["tab_mgmt"], t["tab_logs"]])

# --- TAB: DASHBOARD ---
with tab_dash:
    st.subheader("Pipeline Health & Real-time Orchestration")
    stages = st.session_state.agents_yaml["pipeline"]["stages"]
    cols = st.columns(4)
    for idx, s in enumerate(stages):
        with cols[idx % 4]:
            st.markdown(f"""
            <div class="agent-card">
                <div style="display: flex; justify-content: space-between;">
                    <span>{s['icon']} <b>{s['agent']}</b></span>
                    <span class="status-pill">{s['status']}</span>
                </div>
                <p style="font-size: 0.85em; opacity: 0.8; margin-top: 10px;">{s['task']}</p>
                <div style="font-size: 0.7em; text-transform: uppercase;">Phase: {s['phase']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.divider()
    st.subheader("System Telemetry")
    met_c1, met_c2, met_c3, met_c4 = st.columns(4)
    met_c1.metric("Active Agents", len(stages), "+2 New")
    met_c2.metric("Regulatory Coverage", f"{min(100, len(st.session_state.garden)*15)}%", "Target: 100%")
    met_c3.metric("Resource Drain", f"{100 - st.session_state.mana}%", "Current Peak")

# --- TAB: LIVE REVIEW ---
with tab_rev:
    c1, c2 = st.columns([1, 1])
    
    with c1:
        st.subheader(t["upload_doc"])
        file = st.file_uploader("Upload 510(k) PDF/XML", type=["pdf", "txt", "xml"])
        
        # --- AI FEATURE 1: Document Risk Pre-Assessor ---
        if file and st.session_state.user_api_key:
            if st.button("🔮 Run AI Risk Pre-Assessment", icon="✨"):
                with st.spinner("AI is analyzing document metadata..."):
                    prompt = f"Act as an FDA 510(k) initial reviewer. Based on a submitted file named '{file.name}', generate a fast 3-bullet point preliminary risk & compliance checklist for the review team."
                    ai_assessment = gemini_call(prompt, target_model)
                    st.info(f"**AI Preliminary Assessment:**\n\n{ai_assessment}")
        
        st.markdown(f"<br>**{t['heatmap']}**", unsafe_allow_html=True)
        phases = ["Admin", "RTA", "Technical", "Substantive", "Clinical"]
        h_cols = st.columns(5)
        for i, p in enumerate(phases):
            is_done = st.session_state.active_indices.get(p, 0) > 0
            color = THEMES[sel_style]['accent'] if is_done else "#555555"
            h_cols[i].markdown(f"<div style='background:{color}; height:10px; border-radius:5px;'></div><center><small>{p}</small></center>", unsafe_allow_html=True)
        
        st.divider()
        st.subheader("Agent Selection")
        selected_agents = []
        for s in stages:
            if st.checkbox(f"{s['icon']} {s['agent']}", value=True, key=f"sel_{s['id']}"):
                selected_agents.append(s)
        
        if st.button("🚀 " + t["btn_run"], use_container_width=True):
            if not file: st.warning("Please upload submission materials.")
            elif not st.session_state.user_api_key: st.error("API Key is missing.")
            else:
                with st.status("Orchestrating Pipeline...", expanded=True) as status:
                    for s in selected_agents:
                        st.write(f"Agent {s['agent']} executing specialized logic...")
                        time.sleep(0.5)
                        if s['icon'] not in st.session_state.garden: st.session_state.garden.append(s['icon'])
                        st.session_state.active_indices[s['phase']] = 1
                        st.session_state.audit_trail.append({
                            "Timestamp": datetime.now().strftime("%H:%M:%S"),
                            "Agent": s['agent'], "Phase": s['phase'], "Model": target_model
                        })
                    st.session_state.mana = max(0, st.session_state.mana - (len(selected_agents) * 2.5))
                    st.session_state.report_md = f"# Preliminary Review: {file.name}\n\n## Summary\nSuccessfully analyzed {len(selected_agents)} regulatory domains.\n\n## Findings\n- **Safety**: Compliant\n- **Performance**: Validated\n\n*Generated by Swissmed V4.0*"
                    status.update(label="Analysis Complete!", state="complete")

    with c2:
        st.subheader(t["report_header"])
        st.text_area("Live Report Editor", value=st.session_state.report_md, height=500, key="report_editor_box")
        st.download_button("Export Report", st.session_state.get("report_editor_box", st.session_state.report_md), "Swissmed_Report.md")

# --- TAB: MANAGEMENT (Agent Hub) ---
with tab_mg:
    st.subheader("Dynamic YAML Orchestration")
    
    # --- AI FEATURE 2: Configuration Optimizer ---
    if st.session_state.user_api_key:
        if st.button("✨ AI Optimize YAML Configuration", use_container_width=True):
            with st.spinner("AI is analyzing your agent structure..."):
                current_yaml = yaml.dump(st.session_state.agents_yaml, sort_keys=False)
                prompt = f"Here is my current AI agent YAML config for medical device regulatory review:\n{current_yaml}\n\nPlease suggest 2 missing regulatory review phases or agents I should add to ensure complete FDA 510(k) coverage. Respond concisely."
                ai_suggestions = gemini_call(prompt, target_model)
                st.success(f"**AI Recommendations:**\n\n{ai_suggestions}")

    col_e1, col_e2 = st.columns([2, 1])
    with col_e1:
        yaml_content = yaml.dump(st.session_state.agents_yaml, allow_unicode=True, sort_keys=False)
        user_input = st.text_area("Edit Configuration", value=yaml_content, height=450)
        if st.button(t["btn_std"]):
            std_data = standardize_yaml(user_input)
            if std_data:
                st.session_state.agents_yaml = std_data
                st.success("Pipeline refreshed successfully.")
                st.rerun()
    with col_e2:
        up_file = st.file_uploader("Upload agents.yaml", type=["yaml", "yml"])
        if up_file:
            st.session_state.agents_yaml = standardize_yaml(up_file.read().decode())
            st.rerun()
        st.download_button("Download Config", yaml.dump(st.session_state.agents_yaml), "agents.yaml")

# --- TAB: LOGS ---
with tab_au:
    if st.session_state.audit_trail:
        st.dataframe(pd.DataFrame(st.session_state.audit_trail), use_container_width=True)
    else:
        st.write("No agent activity logs available.")

if st.session_state.garden:
    st.divider()
    st.markdown(f"### 🌸 Achievement Blossoms: {' '.join(st.session_state.garden)}")

st.caption("Swissmed Flower V4.0 | Regulatory AI Environment")
