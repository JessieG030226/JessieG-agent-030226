import os
import io
import re
import time
import random
from datetime import datetime

import streamlit as st
import yaml
import pandas as pd

# ---------------------------
# Optional / Safe Imports
# ---------------------------
try:
    import google.generativeai as genai
    HAS_GENAI = True
except Exception:
    HAS_GENAI = False

try:
    from openai import OpenAI
    HAS_OPENAI = True
except Exception:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except Exception:
    HAS_ANTHROPIC = False

try:
    import fitz  # PyMuPDF
    HAS_PYMUPDF = True
except Exception:
    HAS_PYMUPDF = False

try:
    import pytesseract
    from PIL import Image
    HAS_TESSERACT = True
except Exception:
    HAS_TESSERACT = False


# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="Swissmed Flower V4.0 — WOW Edition",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ---------------------------
# WOW: I18N
# ---------------------------
I18N = {
    "English": {
        "app_title": "Swissmed Flower V4.0 — WOW Edition",
        "sidebar_title": "Swissmed Control Center",
        "language": "Language",
        "theme_mode": "Mode",
        "theme_light": "Light",
        "theme_dark": "Dark",
        "theme_style": "Style (Painter Theme)",
        "theme_spin": "Magic Wheel (Random Style)",
        "theme_jackpot": "Jackpot (3 Spins, pick best)",
        "api_keys": "API Keys",
        "api_env_using": "Using environment/secrets key (hidden).",
        "api_override": "Override / Paste a new key",
        "api_key_input": "Paste API Key",
        "models": "Models",
        "primary_provider": "Primary Provider",
        "primary_model": "Primary Model",
        "max_tokens": "Max tokens",
        "prompt": "Prompt",
        "tabs": {
            "dash": "📊 WOW Dashboard",
            "review": "🚀 Live Review",
            "agents": "🤖 Agent Hub",
            "notes": "📝 AI Note Keeper",
            "logs": "📜 Audit Logs",
        },
        "submission": {
            "title": "Submission Materials",
            "choose_input": "Choose input method",
            "paste": "Paste text/markdown",
            "upload": "Upload file (PDF/TXT/MD)",
            "paste_label": "Paste your submission text/markdown",
            "upload_label": "Upload submission materials",
            "ocr_title": "OCR / Text Extraction",
            "ocr_method": "Choose extraction method",
            "ocr_pages": "Pages to process (e.g., 1-3,5,10-12)",
            "ocr_run": "Run Extraction",
            "ocr_preview": "Extracted Text Preview",
            "ocr_warn_pdf": "PDF extraction requires PyMuPDF; OCR may require Tesseract.",
        },
        "pipeline": {
            "title": "Agent Pipeline Runner",
            "run_next": "Run next pending agent",
            "reset": "Reset pipeline run",
            "input_to_agent": "Input to this agent (editable)",
            "output_from_agent": "Output from this agent (editable for next agent)",
            "run_agent": "Run this agent",
            "status_ready": "Ready",
            "status_running": "Running",
            "status_done": "Done",
            "status_error": "Error",
            "view_mode": "View mode",
            "view_text": "Text",
            "view_md": "Markdown",
        },
        "dash": {
            "kpis": "KPIs",
            "pipeline_progress": "Pipeline progress",
            "completed": "Completed",
            "pending": "Pending",
            "mana": "Mana",
            "last_run": "Last run",
            "token_budget": "Token budget (max_tokens)",
            "wow_status": "WOW Status",
        },
        "agents": {
            "yaml_title": "agents.yaml",
            "yaml_reload": "Reload agents.yaml",
            "yaml_save": "Save agents.yaml",
            "yaml_ai_opt": "✨ AI Optimize YAML Configuration",
        },
        "notes": {
            "title": "AI Note Keeper",
            "input_title": "Note Input",
            "note_paste": "Paste note (text/markdown)",
            "note_upload": "Upload note (PDF/TXT/MD)",
            "organize": "✨ Organize into structured Markdown",
            "editor": "Note Editor",
            "keywords_title": "AI Keywords Highlighter",
            "keywords_input": "Keywords (comma-separated)",
            "keywords_color": "Highlight color",
            "apply_keywords": "Apply keyword highlights",
            "magics_title": "AI Magics",
        },
        "common": {
            "error_missing_key": "Missing API key for the selected provider.",
            "error_missing_sdk": "Missing SDK/library for the selected provider.",
            "success": "Success",
            "warning": "Warning",
            "info": "Info",
        },
    },
    "繁體中文": {
        "app_title": "Swissmed Flower V4.0 — WOW 版",
        "sidebar_title": "Swissmed 控制中心",
        "language": "語言",
        "theme_mode": "模式",
        "theme_light": "亮色",
        "theme_dark": "暗色",
        "theme_style": "風格（畫家主題）",
        "theme_spin": "魔法輪盤（隨機風格）",
        "theme_jackpot": "頭獎（旋轉三次選最佳）",
        "api_keys": "API 金鑰",
        "api_env_using": "使用環境變數/Secrets 金鑰（已隱藏）。",
        "api_override": "覆蓋 / 貼上新金鑰",
        "api_key_input": "貼上 API 金鑰",
        "models": "模型",
        "primary_provider": "主要供應商",
        "primary_model": "主要模型",
        "max_tokens": "最大 tokens",
        "prompt": "提示詞",
        "tabs": {
            "dash": "📊 WOW 儀表板",
            "review": "🚀 即時審查",
            "agents": "🤖 Agent 中心",
            "notes": "📝 AI 筆記管家",
            "logs": "📜 稽核紀錄",
        },
        "submission": {
            "title": "送審資料",
            "choose_input": "選擇輸入方式",
            "paste": "貼上文字/Markdown",
            "upload": "上傳檔案（PDF/TXT/MD）",
            "paste_label": "貼上送審資料文字/Markdown",
            "upload_label": "上傳送審資料",
            "ocr_title": "OCR / 文字擷取",
            "ocr_method": "選擇擷取方法",
            "ocr_pages": "處理頁碼（例如：1-3,5,10-12）",
            "ocr_run": "執行擷取",
            "ocr_preview": "擷取文字預覽",
            "ocr_warn_pdf": "PDF 擷取需要 PyMuPDF；OCR 可能需要 Tesseract。",
        },
        "pipeline": {
            "title": "Agent 流水線執行器",
            "run_next": "執行下一個待處理 Agent",
            "reset": "重置流水線",
            "input_to_agent": "本 Agent 輸入（可編輯）",
            "output_from_agent": "本 Agent 輸出（可編輯，供下一個 Agent 使用）",
            "run_agent": "執行此 Agent",
            "status_ready": "待命",
            "status_running": "執行中",
            "status_done": "完成",
            "status_error": "錯誤",
            "view_mode": "檢視模式",
            "view_text": "文字",
            "view_md": "Markdown",
        },
        "dash": {
            "kpis": "關鍵指標",
            "pipeline_progress": "流水線進度",
            "completed": "已完成",
            "pending": "待處理",
            "mana": "魔力值",
            "last_run": "最近執行",
            "token_budget": "Token 預算（max_tokens）",
            "wow_status": "WOW 狀態",
        },
        "agents": {
            "yaml_title": "agents.yaml",
            "yaml_reload": "重新載入 agents.yaml",
            "yaml_save": "儲存 agents.yaml",
            "yaml_ai_opt": "✨ AI 優化 YAML 設定",
        },
        "notes": {
            "title": "AI 筆記管家",
            "input_title": "筆記輸入",
            "note_paste": "貼上筆記（文字/Markdown）",
            "note_upload": "上傳筆記（PDF/TXT/MD）",
            "organize": "✨ 整理為結構化 Markdown",
            "editor": "筆記編輯器",
            "keywords_title": "AI 關鍵字上色",
            "keywords_input": "關鍵字（逗號分隔）",
            "keywords_color": "上色顏色",
            "apply_keywords": "套用關鍵字上色",
            "magics_title": "AI 魔法功能",
        },
        "common": {
            "error_missing_key": "所選供應商缺少 API 金鑰。",
            "error_missing_sdk": "所選供應商缺少 SDK/套件。",
            "success": "成功",
            "warning": "警告",
            "info": "提示",
        },
    },
}


# ---------------------------
# WOW: 20 Painter Styles
# ---------------------------
PAINTER_STYLES = {
    "Nordic Minimalist": {"bg": "#F9FBFC", "accent": "#88B0BD", "text": "#1F2D3D", "font": "Inter, system-ui, sans-serif"},
    "Vincent van Gogh": {"bg": "#0B1B4D", "accent": "#FDD835", "text": "#FFFFFF", "font": "Georgia, serif"},
    "Claude Monet": {"bg": "#EAF7F0", "accent": "#65B891", "text": "#1F3A2E", "font": "Georgia, serif"},
    "Leonardo da Vinci": {"bg": "#F3EFE7", "accent": "#6D4C41", "text": "#2E1F1A", "font": "Garamond, serif"},
    "Pablo Picasso": {"bg": "#FAF1E6", "accent": "#1E88E5", "text": "#1B1B1B", "font": "Trebuchet MS, sans-serif"},
    "Salvador Dalí": {"bg": "#0F0F14", "accent": "#FF6D00", "text": "#F5F5F5", "font": "Georgia, serif"},
    "Rembrandt": {"bg": "#1B140F", "accent": "#C9A227", "text": "#F4E7D3", "font": "Garamond, serif"},
    "Johannes Vermeer": {"bg": "#0E2A47", "accent": "#E0B84A", "text": "#F2F6FA", "font": "Georgia, serif"},
    "Frida Kahlo": {"bg": "#0F2E24", "accent": "#FF3D7F", "text": "#F6FFF9", "font": "system-ui, sans-serif"},
    "Andy Warhol": {"bg": "#111111", "accent": "#FF2D95", "text": "#F8F8F8", "font": "Arial Black, sans-serif"},
    "Hokusai": {"bg": "#F7FBFF", "accent": "#1565C0", "text": "#0D1B2A", "font": "Georgia, serif"},
    "Jackson Pollock": {"bg": "#121212", "accent": "#7C4DFF", "text": "#ECECEC", "font": "system-ui, sans-serif"},
    "Gustav Klimt": {"bg": "#1A1510", "accent": "#D4AF37", "text": "#F7E7B4", "font": "Georgia, serif"},
    "Edvard Munch": {"bg": "#2A1A1F", "accent": "#FF5252", "text": "#F5E9E9", "font": "Georgia, serif"},
    "Georgia O’Keeffe": {"bg": "#FFF7F2", "accent": "#E85D75", "text": "#2D1B1E", "font": "system-ui, sans-serif"},
    "Caravaggio": {"bg": "#0E0B08", "accent": "#B71C1C", "text": "#F5F1EA", "font": "Garamond, serif"},
    "Paul Cézanne": {"bg": "#F6F0E6", "accent": "#2E7D32", "text": "#2A2A2A", "font": "Georgia, serif"},
    "Henri Matisse": {"bg": "#FFF3E0", "accent": "#00ACC1", "text": "#1A1A1A", "font": "system-ui, sans-serif"},
    "Yayoi Kusama": {"bg": "#FFFFFF", "accent": "#E53935", "text": "#111111", "font": "system-ui, sans-serif"},
    "Edward Hopper": {"bg": "#0B2239", "accent": "#FFCA28", "text": "#E9F2FA", "font": "Georgia, serif"},
}


# ---------------------------
# Model Catalog (multi-provider)
# ---------------------------
MODEL_CATALOG = {
    "Gemini": [
        ("gemini-2.5-flash", "Gemini 2.5 Flash"),
        ("gemini-3-flash-preview", "Gemini 3 Flash Preview"),
        ("gemini-2.5-flash-lite", "Gemini 2.5 Flash Lite"),
        ("gemini-3-pro-preview", "Gemini 3 Pro Preview"),
    ],
    "OpenAI": [
        ("gpt-4o-mini", "gpt-4o-mini"),
        ("gpt-4.1-mini", "gpt-4.1-mini"),
    ],
    "Anthropic": [
        ("claude-3-5-sonnet-latest", "Claude 3.5 Sonnet (latest)"),
        ("claude-3-5-haiku-latest", "Claude 3.5 Haiku (latest)"),
        ("claude-3-opus-latest", "Claude 3 Opus (latest)"),
    ],
    "xAI (Grok)": [
        ("grok-4-fast-reasoning", "grok-4-fast-reasoning"),
        ("grok-4-1-fast-non-reasoning", "grok-4-1-fast-non-reasoning"),
    ],
}

DEFAULT_MAX_TOKENS = 12000


# ---------------------------
# Session State Defaults
# ---------------------------
def ss_init(key, value):
    if key not in st.session_state:
        st.session_state[key] = value


ss_init("language", "English")
ss_init("theme_style", "Nordic Minimalist")
ss_init("theme_mode", "Light")
ss_init("mana", 100)
ss_init("garden", [])
ss_init("audit_trail", [])
ss_init("last_run_ts", None)

# API keys (loaded from secrets/env; do not show if present there)
def read_secret_or_env(name: str) -> str:
    try:
        if hasattr(st, "secrets") and name in st.secrets:
            return str(st.secrets[name] or "")
    except Exception:
        pass
    return os.environ.get(name, "") or ""


ss_init("GEMINI_API_KEY", read_secret_or_env("GEMINI_API_KEY"))
ss_init("OPENAI_API_KEY", read_secret_or_env("OPENAI_API_KEY"))
ss_init("ANTHROPIC_API_KEY", read_secret_or_env("ANTHROPIC_API_KEY"))
ss_init("XAI_API_KEY", read_secret_or_env("XAI_API_KEY"))  # for Grok (OpenAI-compatible base_url)

ss_init("primary_provider", "Gemini")
ss_init("primary_model", "gemini-2.5-flash")
ss_init("max_tokens", DEFAULT_MAX_TOKENS)
ss_init("global_prompt_prefix", "")

# Submission / extraction state
ss_init("submission_text", "")
ss_init("submission_filename", None)
ss_init("extracted_text", "")
ss_init("ocr_method", "Python (PyMuPDF extract)")
ss_init("ocr_pages", "1-3")

# Pipeline / agents state
ss_init("agents_yaml_path", "agents.yaml")
ss_init("skill_path", "SKILL.md")
ss_init("agents_yaml", None)
ss_init("pipeline_state", {})  # per stage: status, prompt, model/provider, in/out text
ss_init("active_report_md", "# Regulatory Summary\n\n*Awaiting submission...*")

# Notes state
ss_init("note_text", "")
ss_init("note_md", "")
ss_init("note_keywords", "")
ss_init("note_keyword_color", "#FF7F50")  # coral
ss_init("note_highlighted_md", "")


# ---------------------------
# Utilities: Logging & Parsing
# ---------------------------
def log_event(action: str, details: str = "", stage_id: str = ""):
    st.session_state.audit_trail.append(
        {
            "ts": datetime.utcnow().isoformat(timespec="seconds") + "Z",
            "action": action,
            "stage_id": stage_id,
            "details": details[:5000],
        }
    )


def parse_pages(pages_str: str, max_pages: int) -> list[int]:
    """
    Parse pages like "1-3,5,10-12" into 1-indexed page numbers.
    Clamps to [1, max_pages].
    """
    pages_str = (pages_str or "").strip()
    if not pages_str:
        return []
    out = set()
    parts = [p.strip() for p in pages_str.split(",") if p.strip()]
    for p in parts:
        if "-" in p:
            a, b = p.split("-", 1)
            try:
                a_i, b_i = int(a), int(b)
            except Exception:
                continue
            if a_i > b_i:
                a_i, b_i = b_i, a_i
            for k in range(a_i, b_i + 1):
                if 1 <= k <= max_pages:
                    out.add(k)
        else:
            try:
                k = int(p)
                if 1 <= k <= max_pages:
                    out.add(k)
            except Exception:
                continue
    return sorted(out)


def clamp_int(val, lo, hi, default):
    try:
        v = int(val)
        return max(lo, min(hi, v))
    except Exception:
        return default


# ---------------------------
# WOW Theme CSS
# ---------------------------
def apply_theme(style_key: str, mode: str):
    cfg = PAINTER_STYLES.get(style_key, PAINTER_STYLES["Nordic Minimalist"])
    is_dark = (mode == "Dark")

    bg = "#0E1117" if is_dark else cfg["bg"]
    card_bg = "rgba(255,255,255,0.06)" if is_dark else "rgba(0,0,0,0.03)"
    text = "#EAEAEA" if is_dark else cfg["text"]
    accent = cfg["accent"]
    subtle = "rgba(255,255,255,0.08)" if is_dark else "rgba(0,0,0,0.06)"

    st.markdown(
        f"""
        <style>
          :root {{
            --wow-bg: {bg};
            --wow-text: {text};
            --wow-accent: {accent};
            --wow-card: {card_bg};
            --wow-subtle: {subtle};
            --wow-font: {cfg["font"]};
          }}
          .stApp {{
            background: var(--wow-bg);
            color: var(--wow-text);
            font-family: var(--wow-font);
          }}
          /* WOW header glow */
          .wow-title {{
            font-weight: 800;
            letter-spacing: 0.4px;
            line-height: 1.05;
            margin: 0.2rem 0 0.2rem 0;
            text-shadow: 0 0 18px color-mix(in srgb, var(--wow-accent) 30%, transparent);
          }}
          .wow-subtitle {{
            opacity: 0.85;
            margin-top: 0.2rem;
          }}
          /* Cards */
          .wow-card {{
            background: var(--wow-card);
            border: 1px solid var(--wow-subtle);
            border-left: 6px solid var(--wow-accent);
            padding: 14px 14px;
            border-radius: 14px;
          }}
          .wow-pill {{
            display: inline-block;
            padding: 2px 10px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 700;
            background: color-mix(in srgb, var(--wow-accent) 22%, transparent);
            border: 1px solid color-mix(in srgb, var(--wow-accent) 45%, transparent);
            margin-right: 8px;
          }}
          .wow-mini {{
            opacity: 0.85;
            font-size: 12.5px;
          }}
          .wow-divider {{
            height: 1px;
            background: var(--wow-subtle);
            margin: 10px 0 10px 0;
          }}
          /* Coral keyword highlight */
          .kw {{
            color: {st.session_state.note_keyword_color};
            font-weight: 800;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ---------------------------
# Provider Calls (No codegen; actual runtime calling)
# ---------------------------
def read_skill_md(path: str) -> str:
    try:
        if path and os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    except Exception:
        pass
    return ""


def require_api_key_for(provider: str) -> str:
    if provider == "Gemini":
        return st.session_state.get("GEMINI_API_KEY", "")
    if provider == "OpenAI":
        return st.session_state.get("OPENAI_API_KEY", "")
    if provider == "Anthropic":
        return st.session_state.get("ANTHROPIC_API_KEY", "")
    if provider.startswith("xAI"):
        return st.session_state.get("XAI_API_KEY", "")
    return ""


def call_llm(provider: str, model: str, user_prompt: str, max_tokens: int, system_prompt: str = "") -> str:
    """
    Unified LLM caller. Returns text response or error string.
    """
    api_key = require_api_key_for(provider)
    if not api_key:
        return f"Error: {I18N[st.session_state.language]['common']['error_missing_key']} ({provider})"

    max_tokens = clamp_int(max_tokens, 1, 200000, DEFAULT_MAX_TOKENS)
    full_prompt = user_prompt if not system_prompt else f"{system_prompt}\n\n---\n\n{user_prompt}"

    # Gemini
    if provider == "Gemini":
        if not HAS_GENAI:
            return f"Error: {I18N[st.session_state.language]['common']['error_missing_sdk']} (google-generativeai)"
        try:
            genai.configure(api_key=api_key)
            # Prefer system_instruction if SKILL provided; else plain prompt
            if system_prompt.strip():
                m = genai.GenerativeModel(model_name=model, system_instruction=system_prompt)
                resp = m.generate_content(user_prompt)
            else:
                m = genai.GenerativeModel(model_name=model)
                resp = m.generate_content(full_prompt)
            return getattr(resp, "text", "") or str(resp)
        except Exception as e:
            return f"API Error (Gemini): {e}"

    # OpenAI
    if provider == "OpenAI":
        if not HAS_OPENAI:
            return f"Error: {I18N[st.session_state.language]['common']['error_missing_sdk']} (openai)"
        try:
            client = OpenAI(api_key=api_key)
            # Use chat.completions for compatibility
            messages = []
            if system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=min(max_tokens, 16384),
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"API Error (OpenAI): {e}"

    # Anthropic
    if provider == "Anthropic":
        if not HAS_ANTHROPIC:
            return f"Error: {I18N[st.session_state.language]['common']['error_missing_sdk']} (anthropic)"
        try:
            client = anthropic.Anthropic(api_key=api_key)
            # Anthropic uses "system" separately in some APIs
            resp = client.messages.create(
                model=model,
                system=system_prompt or None,
                max_tokens=min(max_tokens, 8192),
                messages=[{"role": "user", "content": user_prompt}],
            )
            # content is list of blocks
            chunks = []
            for b in resp.content:
                if getattr(b, "type", "") == "text":
                    chunks.append(b.text)
            return "\n".join(chunks).strip()
        except Exception as e:
            return f"API Error (Anthropic): {e}"

    # xAI Grok (OpenAI-compatible)
    if provider.startswith("xAI"):
        if not HAS_OPENAI:
            return f"Error: {I18N[st.session_state.language]['common']['error_missing_sdk']} (openai)"
        try:
            client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
            messages = []
            if system_prompt.strip():
                messages.append({"role": "system", "content": system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=min(max_tokens, 8192),
            )
            return resp.choices[0].message.content or ""
        except Exception as e:
            return f"API Error (xAI): {e}"

    return f"Error: Unsupported provider ({provider})."


# ---------------------------
# OCR / Extraction
# ---------------------------
def pdf_extract_text_pymupdf(pdf_bytes: bytes, pages_1idx: list[int]) -> str:
    if not HAS_PYMUPDF:
        return "Error: PyMuPDF not available. Add 'pymupdf' to requirements."
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        max_pages = doc.page_count
        if not pages_1idx:
            pages_1idx = list(range(1, max_pages + 1))
        chunks = []
        for p in pages_1idx:
            if 1 <= p <= max_pages:
                page = doc.load_page(p - 1)
                text = page.get_text("text")
                chunks.append(f"\n\n=== Page {p} ===\n{text}".strip())
        return "\n".join(chunks).strip()
    except Exception as e:
        return f"Error extracting PDF text: {e}"


def pdf_render_page_png(pdf_bytes: bytes, page_1idx: int, dpi: int = 200) -> bytes:
    if not HAS_PYMUPDF:
        raise RuntimeError("PyMuPDF not available")
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    if not (1 <= page_1idx <= doc.page_count):
        raise ValueError("Page out of range")
    page = doc.load_page(page_1idx - 1)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    return pix.tobytes("png")


def pdf_ocr_tesseract(pdf_bytes: bytes, pages_1idx: list[int]) -> str:
    if not HAS_PYMUPDF:
        return "Error: PyMuPDF not available."
    if not HAS_TESSERACT:
        return "Error: Tesseract not available. Install pytesseract + system tesseract binary."
    try:
        # Render each page -> OCR
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        max_pages = doc.page_count
        if not pages_1idx:
            pages_1idx = list(range(1, max_pages + 1))

        chunks = []
        for p in pages_1idx:
            if 1 <= p <= max_pages:
                png = pdf_render_page_png(pdf_bytes, p, dpi=250)
                img = Image.open(io.BytesIO(png))
                txt = pytesseract.image_to_string(img)
                chunks.append(f"\n\n=== Page {p} (OCR) ===\n{txt}".strip())
        return "\n".join(chunks).strip()
    except Exception as e:
        return f"Error during Tesseract OCR: {e}"


def pdf_ocr_llm_gemini(pdf_bytes: bytes, pages_1idx: list[int], model: str, api_key: str) -> str:
    if not HAS_GENAI:
        return "Error: google-generativeai not available."
    if not HAS_PYMUPDF:
        return "Error: PyMuPDF not available (required to render page images for LLM OCR)."
    if not api_key:
        return "Error: Missing Gemini API key."
    try:
        genai.configure(api_key=api_key)
        m = genai.GenerativeModel(model_name=model)

        # Render each page -> send image to Gemini with a strict extraction prompt
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        max_pages = doc.page_count
        if not pages_1idx:
            pages_1idx = list(range(1, max_pages + 1))

        chunks = []
        for p in pages_1idx:
            if 1 <= p <= max_pages:
                png = pdf_render_page_png(pdf_bytes, p, dpi=250)
                prompt = (
                    "You are an OCR engine. Extract all readable text from the image exactly. "
                    "Preserve headings and bullet structure. Do NOT summarize. "
                    "Return plain text only."
                )
                resp = m.generate_content(
                    [
                        prompt,
                        {"mime_type": "image/png", "data": png},
                    ]
                )
                txt = getattr(resp, "text", "") or ""
                chunks.append(f"\n\n=== Page {p} (LLM OCR) ===\n{txt}".strip())

        return "\n".join(chunks).strip()
    except Exception as e:
        return f"Error during Gemini LLM OCR: {e}"


def read_uploaded_text(file) -> str:
    """
    Reads TXT/MD directly; for PDF we rely on extraction methods.
    """
    try:
        name = (file.name or "").lower()
        data = file.getvalue()
        if name.endswith(".txt") or name.endswith(".md") or name.endswith(".markdown"):
            # Attempt utf-8 first
            try:
                return data.decode("utf-8")
            except Exception:
                return data.decode("latin-1", errors="ignore")
        return ""
    except Exception as e:
        return f"Error reading upload: {e}"


# ---------------------------
# Agents YAML Load/Save
# ---------------------------
DEFAULT_AGENTS = {
    "pipeline": {
        "version": "4.0",
        "stages": [
            {
                "id": "rta",
                "agent": "RTA Admin",
                "icon": "🌿",
                "task": "Completeness check and missing-items detection.",
                "phase": "RTA",
            },
            {
                "id": "software",
                "agent": "Software Analyst",
                "icon": "💻",
                "task": "Software documentation/LOC verification and risk notes.",
                "phase": "Technical",
            },
            {
                "id": "cyber",
                "agent": "Cyber Auditor",
                "icon": "🛡️",
                "task": "SBOM review, vulnerability posture, and cybersecurity controls.",
                "phase": "Technical",
            },
        ]
    }
}


def load_agents_yaml(path: str):
    if path and os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or DEFAULT_AGENTS
        except Exception as e:
            log_event("agents_yaml_load_error", str(e))
            return DEFAULT_AGENTS
    return DEFAULT_AGENTS


def save_agents_yaml(path: str, data: dict):
    try:
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
        log_event("agents_yaml_saved", path)
        return True, ""
    except Exception as e:
        return False, str(e)


if st.session_state.agents_yaml is None:
    st.session_state.agents_yaml = load_agents_yaml(st.session_state.agents_yaml_path)


def ensure_pipeline_state():
    """
    Create per-stage runtime state (status, prompt override, model/provider, in/out buffers).
    """
    stages = st.session_state.agents_yaml.get("pipeline", {}).get("stages", [])
    for s in stages:
        sid = s.get("id", "")
        if sid not in st.session_state.pipeline_state:
            st.session_state.pipeline_state[sid] = {
                "status": "Ready",
                "provider": st.session_state.primary_provider,
                "model": st.session_state.primary_model,
                "max_tokens": st.session_state.max_tokens,
                "prompt": f"You are {s.get('agent','Agent')}. Task: {s.get('task','')}\n\n"
                          f"Return a structured markdown report with clear headings, bullet points, and action items.",
                "input": "",
                "output": "",
                "started_at": None,
                "ended_at": None,
                "error": "",
            }


ensure_pipeline_state()


# ---------------------------
# Sidebar: WOW Controls
# ---------------------------
t = I18N[st.session_state.language]

with st.sidebar:
    st.markdown(f"### {t['sidebar_title']}")

    # Language
    st.session_state.language = st.selectbox(
        t["language"],
        options=list(I18N.keys()),
        index=list(I18N.keys()).index(st.session_state.language),
    )
    t = I18N[st.session_state.language]  # refresh after change

    # Theme selection + magic wheel
    st.markdown("### WOW UI")
    c_spin1, c_spin2 = st.columns(2)
    with c_spin1:
        if st.button(t["theme_spin"], use_container_width=True):
            st.session_state.theme_style = random.choice(list(PAINTER_STYLES.keys()))
            log_event("theme_spin", st.session_state.theme_style)
    with c_spin2:
        if st.button(t["theme_jackpot"], use_container_width=True):
            picks = random.sample(list(PAINTER_STYLES.keys()), k=min(3, len(PAINTER_STYLES)))
            # "Jackpot": pick the most contrasty accent vs bg (simple heuristic)
            def score(style):
                cfg = PAINTER_STYLES[style]
                return len(cfg["accent"]) + len(cfg["bg"])
            st.session_state.theme_style = sorted(picks, key=score, reverse=True)[0]
            log_event("theme_jackpot", f"picks={picks} winner={st.session_state.theme_style}")

    st.session_state.theme_style = st.selectbox(
        t["theme_style"],
        options=list(PAINTER_STYLES.keys()),
        index=list(PAINTER_STYLES.keys()).index(st.session_state.theme_style),
    )
    st.session_state.theme_mode = st.radio(
        t["theme_mode"],
        options=[t["theme_light"], t["theme_dark"]],
        index=0 if st.session_state.theme_mode == "Light" else 1,
        horizontal=True,
    )
    # normalize mode to "Light"/"Dark"
    st.session_state.theme_mode = "Light" if st.session_state.theme_mode == t["theme_light"] else "Dark"

    apply_theme(st.session_state.theme_style, st.session_state.theme_mode)

    st.markdown("### " + t["api_keys"])

    def api_key_widget(env_name: str, label: str, session_key: str):
        existing = read_secret_or_env(env_name)
        has_hidden = bool(existing)
        if has_hidden:
            st.caption(f"{label}: {t['api_env_using']}")
            override = st.checkbox(f"{label}: {t['api_override']}", value=False)
            if override:
                val = st.text_input(label, value="", type="password", placeholder=t["api_key_input"])
                if val:
                    st.session_state[session_key] = val
                    log_event("api_key_override_set", f"{env_name} overridden")
            else:
                # keep current secret/env value (but do not display)
                st.session_state[session_key] = existing
        else:
            val = st.text_input(label, value=st.session_state.get(session_key, ""), type="password", placeholder=t["api_key_input"])
            st.session_state[session_key] = val

    api_key_widget("GEMINI_API_KEY", "Gemini API Key", "GEMINI_API_KEY")
    api_key_widget("OPENAI_API_KEY", "OpenAI API Key", "OPENAI_API_KEY")
    api_key_widget("ANTHROPIC_API_KEY", "Anthropic API Key", "ANTHROPIC_API_KEY")
    api_key_widget("XAI_API_KEY", "xAI API Key", "XAI_API_KEY")

    st.markdown("### " + t["models"])
    st.session_state.primary_provider = st.selectbox(
        t["primary_provider"],
        options=list(MODEL_CATALOG.keys()),
        index=list(MODEL_CATALOG.keys()).index(st.session_state.primary_provider),
    )
    provider_models = MODEL_CATALOG[st.session_state.primary_provider]
    model_ids = [m[0] for m in provider_models]
    model_labels = [m[1] for m in provider_models]
    default_idx = model_ids.index(st.session_state.primary_model) if st.session_state.primary_model in model_ids else 0
    picked_label = st.selectbox(t["primary_model"], options=model_labels, index=default_idx)
    st.session_state.primary_model = provider_models[model_labels.index(picked_label)][0]

    st.session_state.max_tokens = st.number_input(
        t["max_tokens"], min_value=256, max_value=200000, value=int(st.session_state.max_tokens), step=256
    )

    st.session_state.global_prompt_prefix = st.text_area(
        t["prompt"],
        value=st.session_state.global_prompt_prefix,
        height=120,
        placeholder="Optional global prefix applied to each agent prompt (e.g., formatting rules, tone, constraints).",
    )


# ---------------------------
# Header
# ---------------------------
st.markdown(f"<h1 class='wow-title'>{t['app_title']}</h1>", unsafe_allow_html=True)
st.markdown(
    "<div class='wow-subtitle'>WOW UI • Multi-provider LLMs • Agent-by-agent editing • OCR & Note Keeper • Hugging Face Spaces + Streamlit</div>",
    unsafe_allow_html=True,
)


# ---------------------------
# Tabs
# ---------------------------
tabs = st.tabs([t["tabs"]["dash"], t["tabs"]["review"], t["tabs"]["agents"], t["tabs"]["notes"], t["tabs"]["logs"]])
tab_dash, tab_review, tab_agents, tab_notes, tab_logs = tabs


# ---------------------------
# WOW Dashboard
# ---------------------------
with tab_dash:
    stages = st.session_state.agents_yaml.get("pipeline", {}).get("stages", [])
    ensure_pipeline_state()

    completed = sum(1 for s in stages if st.session_state.pipeline_state.get(s["id"], {}).get("status") == "Done")
    pending = len(stages) - completed
    progress = (completed / len(stages)) if stages else 0.0

    st.markdown(f"### {t['dash']['kpis']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(t["dash"]["pipeline_progress"], f"{int(progress * 100)}%")
    c2.metric(t["dash"]["completed"], str(completed))
    c3.metric(t["dash"]["pending"], str(pending))
    c4.metric(t["dash"]["mana"], str(st.session_state.mana))

    c5, c6, c7 = st.columns(3)
    c5.metric(t["dash"]["token_budget"], str(int(st.session_state.max_tokens)))
    c6.metric(t["dash"]["last_run"], st.session_state.last_run_ts or "—")
    c7.metric(t["dash"]["wow_status"], "Blooming" if completed else "Seedling")

    st.progress(progress)

    st.markdown("### " + "Interactive Pipeline Cards")
    cols = st.columns(3)
    for idx, s in enumerate(stages):
        sid = s.get("id", "")
        ps = st.session_state.pipeline_state.get(sid, {})
        status = ps.get("status", "Ready")
        pill = status
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="wow-card">
                  <div style="display:flex; align-items:center; justify-content:space-between;">
                    <div>
                      <div style="font-size:16px; font-weight:800;">{s.get("icon","")} {s.get("agent","Agent")}</div>
                      <div class="wow-mini">{s.get("phase","")}</div>
                    </div>
                    <div class="wow-pill">{pill}</div>
                  </div>
                  <div class="wow-divider"></div>
                  <div class="wow-mini">{s.get("task","")}</div>
                  <div class="wow-divider"></div>
                  <div class="wow-mini"><b>Provider/Model:</b> {ps.get("provider","")} / {ps.get("model","")}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    if st.session_state.garden:
        st.markdown("### 🌸 Achievement Blossoms")
        st.write(" ".join(st.session_state.garden))


# ---------------------------
# Live Review: Submission + OCR + Pipeline Runner + Report Editor
# ---------------------------
with tab_review:
    ensure_pipeline_state()
    stages = st.session_state.agents_yaml.get("pipeline", {}).get("stages", [])

    left, right = st.columns([1.05, 1.0], gap="large")

    with left:
        st.markdown(f"### {t['submission']['title']}")

        input_mode = st.radio(
            t["submission"]["choose_input"],
            options=[t["submission"]["paste"], t["submission"]["upload"]],
            horizontal=True,
        )

        uploaded = None
        if input_mode == t["submission"]["paste"]:
            st.session_state.submission_text = st.text_area(
                t["submission"]["paste_label"],
                value=st.session_state.submission_text,
                height=220,
            )
            st.session_state.submission_filename = "pasted_submission.md"
        else:
            uploaded = st.file_uploader(
                t["submission"]["upload_label"],
                type=["pdf", "txt", "md", "markdown"],
            )
            if uploaded is not None:
                st.session_state.submission_filename = uploaded.name
                # For txt/md: read directly. For pdf: use extraction panel below.
                direct_text = read_uploaded_text(uploaded)
                if direct_text:
                    st.session_state.submission_text = direct_text

        st.markdown(f"### {t['submission']['ocr_title']}")
        if uploaded is not None and (uploaded.name or "").lower().endswith(".pdf"):
            st.caption(t["submission"]["ocr_warn_pdf"])

        ocr_methods = [
            "Python (PyMuPDF extract)",
            "Python OCR (Tesseract)",
            "LLM OCR (Gemini: gemini-2.5-flash)",
            "LLM OCR (Gemini: gemini-3-flash-preview)",
        ]
        st.session_state.ocr_method = st.selectbox(
            t["submission"]["ocr_method"],
            options=ocr_methods,
            index=ocr_methods.index(st.session_state.ocr_method) if st.session_state.ocr_method in ocr_methods else 0,
        )
        st.session_state.ocr_pages = st.text_input(t["submission"]["ocr_pages"], value=st.session_state.ocr_pages)

        run_extract = st.button(t["submission"]["ocr_run"], use_container_width=True)

        if run_extract:
            if uploaded is None:
                st.warning("Upload a PDF to extract/OCR, or paste text directly above.")
            else:
                name = (uploaded.name or "").lower()
                if not name.endswith(".pdf"):
                    st.info("Non-PDF file uploaded; reading as text where possible.")
                else:
                    pdf_bytes = uploaded.getvalue()
                    pages = []
                    if HAS_PYMUPDF:
                        try:
                            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
                            pages = parse_pages(st.session_state.ocr_pages, doc.page_count)
                        except Exception:
                            pages = []
                    else:
                        pages = []

                    with st.status("Extracting...", expanded=False) as status:
                        if st.session_state.ocr_method == "Python (PyMuPDF extract)":
                            out = pdf_extract_text_pymupdf(pdf_bytes, pages)
                        elif st.session_state.ocr_method == "Python OCR (Tesseract)":
                            out = pdf_ocr_tesseract(pdf_bytes, pages)
                        elif st.session_state.ocr_method == "LLM OCR (Gemini: gemini-2.5-flash)":
                            out = pdf_ocr_llm_gemini(pdf_bytes, pages, "gemini-2.5-flash", st.session_state.GEMINI_API_KEY)
                        else:
                            out = pdf_ocr_llm_gemini(pdf_bytes, pages, "gemini-3-flash-preview", st.session_state.GEMINI_API_KEY)

                        st.session_state.extracted_text = out
                        # By default, feed extracted text into submission_text (user can edit)
                        if out and not out.startswith("Error:"):
                            st.session_state.submission_text = out
                            log_event("submission_extracted", f"method={st.session_state.ocr_method} pages={pages}")
                            status.update(label="Extraction done", state="complete")
                        else:
                            log_event("submission_extract_error", out)
                            status.update(label="Extraction error", state="error")

        st.markdown(f"#### {t['submission']['ocr_preview']}")
        st.text_area(
            label="",
            value=(st.session_state.extracted_text or "")[:20000],
            height=200,
        )

        st.markdown(f"### {t['pipeline']['title']}")

        # Global controls
        c_run, c_reset = st.columns([1, 1])
        with c_reset:
            if st.button(t["pipeline"]["reset"], use_container_width=True):
                for s in stages:
                    sid = s["id"]
                    st.session_state.pipeline_state[sid]["status"] = "Ready"
                    st.session_state.pipeline_state[sid]["input"] = ""
                    st.session_state.pipeline_state[sid]["output"] = ""
                    st.session_state.pipeline_state[sid]["error"] = ""
                    st.session_state.pipeline_state[sid]["started_at"] = None
                    st.session_state.pipeline_state[sid]["ended_at"] = None
                st.session_state.active_report_md = "# Regulatory Summary\n\n*Awaiting submission...*"
                st.session_state.garden = []
                log_event("pipeline_reset", "All stages reset")
                st.rerun()

        def build_agent_input(sid: str, idx: int) -> str:
            # For first agent: use submission_text. Later: use previous stage output.
            if idx == 0:
                return st.session_state.submission_text or ""
            prev_sid = stages[idx - 1]["id"]
            prev_out = st.session_state.pipeline_state[prev_sid].get("output", "")
            return prev_out or ""

        def agent_prompt_render(sid: str) -> str:
            ps = st.session_state.pipeline_state[sid]
            prefix = (st.session_state.global_prompt_prefix or "").strip()
            base = (ps.get("prompt") or "").strip()
            if prefix:
                return f"{prefix}\n\n---\n\n{base}"
            return base

        def run_stage(stage_idx: int):
            s = stages[stage_idx]
            sid = s["id"]
            ps = st.session_state.pipeline_state[sid]

            # Prepare input: user-editable; if empty set default
            if not (ps.get("input") or "").strip():
                ps["input"] = build_agent_input(sid, stage_idx)

            ps["status"] = "Running"
            ps["started_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
            log_event("agent_started", f"{ps['provider']} / {ps['model']}", stage_id=sid)

            skill = read_skill_md(st.session_state.skill_path)

            user_payload = (
                f"## Agent\n{ s.get('agent','') }\n\n"
                f"## Task\n{ s.get('task','') }\n\n"
                f"## Submission / Context\n{ ps['input'] }\n\n"
                f"## Instructions\n{agent_prompt_render(sid)}\n"
            )

            out = call_llm(
                provider=ps["provider"],
                model=ps["model"],
                user_prompt=user_payload,
                max_tokens=int(ps["max_tokens"]),
                system_prompt=skill,
            )

            if out.startswith("Error:") or out.startswith("API Error"):
                ps["status"] = "Error"
                ps["error"] = out
                log_event("agent_error", out, stage_id=sid)
            else:
                ps["status"] = "Done"
                ps["output"] = out
                ps["ended_at"] = datetime.utcnow().isoformat(timespec="seconds") + "Z"
                st.session_state.last_run_ts = ps["ended_at"]
                log_event("agent_done", f"chars={len(out)}", stage_id=sid)
                # achievements
                icon = s.get("icon")
                if icon and icon not in st.session_state.garden:
                    st.session_state.garden.append(icon)
                st.session_state.mana = max(0, st.session_state.mana - 5)

                # Update live report to the latest output by default
                st.session_state.active_report_md = out

            st.session_state.pipeline_state[sid] = ps

        with c_run:
            if st.button(t["pipeline"]["run_next"], use_container_width=True):
                # find next pending
                next_idx = None
                for i, s in enumerate(stages):
                    if st.session_state.pipeline_state[s["id"]]["status"] == "Ready":
                        next_idx = i
                        break
                if next_idx is None:
                    st.info("All agents completed.")
                else:
                    with st.status("Executing next agent...", expanded=True):
                        run_stage(next_idx)
                    st.rerun()

        # Stage-by-stage panels (editable prompts / tokens / models / IO)
        for i, s in enumerate(stages):
            sid = s["id"]
            ps = st.session_state.pipeline_state[sid]

            with st.expander(f"{s.get('icon','')} {s.get('agent','Agent')} — {ps.get('status','')}", expanded=(i == 0)):
                top = st.columns([1.2, 1.2, 0.8])
                with top[0]:
                    ps["provider"] = st.selectbox(
                        "Provider",
                        options=list(MODEL_CATALOG.keys()),
                        index=list(MODEL_CATALOG.keys()).index(ps.get("provider", st.session_state.primary_provider)),
                        key=f"prov_{sid}",
                    )
                with top[1]:
                    pm = MODEL_CATALOG[ps["provider"]]
                    pm_ids = [x[0] for x in pm]
                    pm_labels = [x[1] for x in pm]
                    # pick current if exists else primary
                    current = ps.get("model", "")
                    if current not in pm_ids:
                        current = pm_ids[0]
                    ps["model"] = pm_ids[pm_ids.index(current)]
                    picked = st.selectbox(
                        "Model",
                        options=pm_labels,
                        index=pm_ids.index(ps["model"]),
                        key=f"model_{sid}",
                    )
                    ps["model"] = pm[pm_labels.index(picked)][0]
                with top[2]:
                    ps["max_tokens"] = st.number_input(
                        "max_tokens",
                        min_value=256,
                        max_value=200000,
                        value=int(ps.get("max_tokens", st.session_state.max_tokens)),
                        step=256,
                        key=f"mt_{sid}",
                    )

                st.markdown("**Agent prompt (editable):**")
                ps["prompt"] = st.text_area(
                    label="",
                    value=ps.get("prompt", ""),
                    height=160,
                    key=f"prompt_{sid}",
                )

                # Input / Output editing
                io_cols = st.columns(2)
                with io_cols[0]:
                    view_mode_in = st.radio(
                        t["pipeline"]["view_mode"],
                        [t["pipeline"]["view_text"], t["pipeline"]["view_md"]],
                        horizontal=True,
                        key=f"view_in_{sid}",
                    )
                    default_in = ps.get("input", "").strip() or build_agent_input(sid, i)
                    ps["input"] = st.text_area(
                        t["pipeline"]["input_to_agent"],
                        value=default_in,
                        height=220,
                        key=f"in_{sid}",
                    )
                with io_cols[1]:
                    view_mode_out = st.radio(
                        t["pipeline"]["view_mode"],
                        [t["pipeline"]["view_text"], t["pipeline"]["view_md"]],
                        horizontal=True,
                        key=f"view_out_{sid}",
                    )
                    ps["output"] = st.text_area(
                        t["pipeline"]["output_from_agent"],
                        value=ps.get("output", ""),
                        height=220,
                        key=f"out_{sid}",
                    )

                # Run button for this agent
                b_cols = st.columns([1, 2])
                with b_cols[0]:
                    if st.button(t["pipeline"]["run_agent"], use_container_width=True, key=f"run_{sid}"):
                        with st.status(f"Running {s.get('agent','Agent')}...", expanded=True):
                            run_stage(i)
                        st.rerun()

                # Error panel
                if ps.get("status") == "Error":
                    st.error(ps.get("error", "Unknown error"))

                # Save back
                st.session_state.pipeline_state[sid] = ps

    with right:
        st.markdown("### Live Report (Editable)")
        view = st.radio("View", ["Markdown", "Text"], horizontal=True, index=0)
        st.session_state.active_report_md = st.text_area(
            "Report Editor",
            value=st.session_state.active_report_md,
            height=520,
        )
        if view == "Markdown":
            st.markdown("---")
            st.markdown(st.session_state.active_report_md, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### WOW Status Indicators")
        stages = st.session_state.agents_yaml.get("pipeline", {}).get("stages", [])
        done = sum(1 for s in stages if st.session_state.pipeline_state[s["id"]]["status"] == "Done")
        total = max(1, len(stages))
        st.progress(done / total)
        st.caption(f"Stages done: {done}/{total} • Mana: {st.session_state.mana}/100")


# ---------------------------
# Agent Hub: YAML + AI Optimize
# ---------------------------
with tab_agents:
    ensure_pipeline_state()
    st.markdown("### " + t["agents"]["yaml_title"])

    c1, c2, c3 = st.columns([1, 1, 1.2])
    with c1:
        if st.button(t["agents"]["yaml_reload"], use_container_width=True):
            st.session_state.agents_yaml = load_agents_yaml(st.session_state.agents_yaml_path)
            ensure_pipeline_state()
            log_event("agents_yaml_reloaded", st.session_state.agents_yaml_path)
            st.rerun()

    # YAML editor
    yaml_str = yaml.safe_dump(st.session_state.agents_yaml, sort_keys=False, allow_unicode=True)
    edited = st.text_area("YAML", value=yaml_str, height=380)

    with c2:
        if st.button(t["agents"]["yaml_save"], use_container_width=True):
            try:
                data = yaml.safe_load(edited) or DEFAULT_AGENTS
                ok, err = save_agents_yaml(st.session_state.agents_yaml_path, data)
                if ok:
                    st.session_state.agents_yaml = data
                    ensure_pipeline_state()
                    st.success(t["common"]["success"])
                    st.rerun()
                else:
                    st.error(err)
            except Exception as e:
                st.error(str(e))

    with c3:
        if st.button(t["agents"]["yaml_ai_opt"], use_container_width=True):
            provider = st.session_state.primary_provider
            model = st.session_state.primary_model
            skill = read_skill_md(st.session_state.skill_path)
            prompt = (
                "You are a senior agent-orchestration architect.\n"
                "Improve the following agents.yaml while preserving all stages and intent.\n"
                "Focus on: clarity, consistent stage IDs, richer task descriptions, output contracts, and risk controls.\n"
                "Return ONLY YAML.\n\n"
                f"---\nCurrent YAML:\n{edited}"
            )
            with st.spinner("Optimizing YAML..."):
                out = call_llm(provider, model, prompt, st.session_state.max_tokens, system_prompt=skill)
            st.markdown("#### AI Suggestion (copy/paste)")
            st.code(out, language="yaml")
            log_event("yaml_ai_optimize", f"provider={provider} model={model}")

    st.markdown("---")
    st.markdown("### Skill File (SKILL.md)")
    st.caption("Loaded at runtime and passed as system instructions where supported.")
    skill_text = read_skill_md(st.session_state.skill_path)
    st.text_area("SKILL.md (read-only)", value=skill_text, height=200, disabled=True)


# ---------------------------
# AI Note Keeper (Original + Added Features)
# ---------------------------
def highlight_keywords(md: str, keywords_csv: str, color_hex: str) -> str:
    md = md or ""
    keys = [k.strip() for k in (keywords_csv or "").split(",") if k.strip()]
    if not keys:
        return md

    # Apply longest-first to reduce nested partials
    keys_sorted = sorted(keys, key=len, reverse=True)

    def repl(match):
        txt = match.group(0)
        return f"<span class='kw' style='color:{color_hex};'>{txt}</span>"

    out = md
    for k in keys_sorted:
        # word-ish boundary but allow medical tokens with slashes/hyphens
        pattern = re.compile(rf"(?i)(?<!\w)({re.escape(k)})(?!\w)")
        out = pattern.sub(repl, out)
    return out


with tab_notes:
    st.markdown(f"### {t['notes']['title']}")

    left, right = st.columns([1.05, 1.0], gap="large")

    with left:
        st.markdown(f"#### {t['notes']['input_title']}")

        note_mode = st.radio("Input", ["Paste", "Upload"], horizontal=True)
        note_upload = None

        if note_mode == "Paste":
            st.session_state.note_text = st.text_area(
                t["notes"]["note_paste"],
                value=st.session_state.note_text,
                height=220,
            )
        else:
            note_upload = st.file_uploader(
                t["notes"]["note_upload"],
                type=["pdf", "txt", "md", "markdown"],
                key="note_upload",
            )
            if note_upload is not None:
                name = (note_upload.name or "").lower()
                if name.endswith(".pdf"):
                    # default to PyMuPDF extract all pages if available
                    if HAS_PYMUPDF:
                        st.session_state.note_text = pdf_extract_text_pymupdf(note_upload.getvalue(), pages_1idx=[])
                    else:
                        st.session_state.note_text = "Error: PyMuPDF not available for PDF note extraction."
                else:
                    st.session_state.note_text = read_uploaded_text(note_upload)

        organize = st.button(t["notes"]["organize"], use_container_width=True)

        if organize:
            provider = st.session_state.primary_provider
            model = st.session_state.primary_model
            skill = read_skill_md(st.session_state.skill_path)
            prompt = (
                "Transform the following raw notes into organized Markdown.\n"
                "Requirements:\n"
                "1) Use clear headings and subheadings\n"
                "2) Add a short executive summary at top\n"
                "3) Add a keyword list section\n"
                "4) Preserve facts; do not invent data\n"
                "5) Prefer bullet lists for action items and risks\n\n"
                f"RAW NOTES:\n{st.session_state.note_text}"
            )
            with st.spinner("Organizing note..."):
                out = call_llm(provider, model, prompt, st.session_state.max_tokens, system_prompt=skill)
            st.session_state.note_md = out
            log_event("note_organized", f"provider={provider} model={model}")

        st.markdown("---")
        st.markdown(f"#### {t['notes']['keywords_title']}")
        st.session_state.note_keywords = st.text_input(t["notes"]["keywords_input"], value=st.session_state.note_keywords)
        st.session_state.note_keyword_color = st.color_picker(t["notes"]["keywords_color"], value=st.session_state.note_keyword_color)
        if st.button(t["notes"]["apply_keywords"], use_container_width=True):
            st.session_state.note_highlighted_md = highlight_keywords(
                st.session_state.note_md, st.session_state.note_keywords, st.session_state.note_keyword_color
            )
            log_event("note_keywords_applied", st.session_state.note_keywords)

        st.markdown("---")
        st.markdown(f"#### {t['notes']['magics_title']}")

        # 6 original-style "AI Magics" (created here) + 3 additional new ones = 9 total
        magics = [
            ("AI Keywords", "Extract 20-40 keywords and suggest 3 color groups for highlighting."),
            ("AI Summary", "Write a 10-bullet executive summary; each bullet <= 18 words."),
            ("AI Action Items", "Extract action items with owner/priority/due-date placeholders in a table."),
            ("AI Risk Radar", "Identify risks, severity, mitigations; return a markdown table."),
            ("AI Compliance Matrix", "Map claims/requirements to evidence found in the note; highlight gaps."),
            ("AI Q&A Builder", "Create 15 reviewer-style questions and ideal short answers grounded in the text."),
            # 3 additional features requested (new):
            ("AI Traceability Map (NEW)", "Create a traceability map: Requirement -> Evidence quote -> Location -> Confidence."),
            ("AI Red Flags Detector (NEW)", "Detect contradictory statements, missing definitions, unclear scope, and list red flags."),
            ("AI TOC + Glossary Builder (NEW)", "Generate a table of contents and a glossary of terms/acronyms from the note."),
        ]
        magic_name = st.selectbox("Choose Magic", options=[m[0] for m in magics])
        magic_desc = dict(magics)[magic_name]
        st.caption(magic_desc)

        if st.button("Cast Magic", use_container_width=True):
            provider = st.session_state.primary_provider
            model = st.session_state.primary_model
            skill = read_skill_md(st.session_state.skill_path)
            base = st.session_state.note_md or st.session_state.note_text
            prompt = (
                f"Magic: {magic_name}\n"
                f"Goal: {magic_desc}\n\n"
                "Return markdown only. Use tables where helpful. Quote source phrases when making claims.\n\n"
                f"INPUT:\n{base}"
            )
            with st.spinner("Casting..."):
                out = call_llm(provider, model, prompt, st.session_state.max_tokens, system_prompt=skill)
            # append to note markdown
            st.session_state.note_md = (st.session_state.note_md or "").rstrip() + "\n\n---\n\n" + out
            # re-apply highlight if configured
            st.session_state.note_highlighted_md = highlight_keywords(
                st.session_state.note_md, st.session_state.note_keywords, st.session_state.note_keyword_color
            )
            log_event("note_magic_cast", f"{magic_name} provider={provider} model={model}")

    with right:
        st.markdown(f"#### {t['notes']['editor']}")
        view = st.radio("View", ["Markdown (render)", "Markdown (raw)", "Text"], horizontal=True, index=0)

        if view == "Text":
            st.session_state.note_text = st.text_area("Note Text", value=st.session_state.note_text, height=560)
        elif view == "Markdown (raw)":
            st.session_state.note_md = st.text_area("Note Markdown", value=st.session_state.note_md, height=560)
        else:
            # Render highlighted markdown with coral keyword styling
            rendered = st.session_state.note_highlighted_md or highlight_keywords(
                st.session_state.note_md, st.session_state.note_keywords, st.session_state.note_keyword_color
            )
            st.markdown(rendered or "*No note yet.*", unsafe_allow_html=True)


# ---------------------------
# Audit Logs
# ---------------------------
with tab_logs:
    st.markdown("### Audit Trail")
    if st.session_state.audit_trail:
        df = pd.DataFrame(st.session_state.audit_trail)
        st.dataframe(df, use_container_width=True, height=420)
    else:
        st.info("No audit events yet.")

    st.markdown("---")
    st.markdown("### Runtime Diagnostics")
    diag = {
        "HAS_GENAI": HAS_GENAI,
        "HAS_OPENAI": HAS_OPENAI,
        "HAS_ANTHROPIC": HAS_ANTHROPIC,
        "HAS_PYMUPDF": HAS_PYMUPDF,
        "HAS_TESSERACT": HAS_TESSERACT,
        "theme_style": st.session_state.theme_style,
        "theme_mode": st.session_state.theme_mode,
        "language": st.session_state.language,
        "primary_provider": st.session_state.primary_provider,
        "primary_model": st.session_state.primary_model,
        "max_tokens": int(st.session_state.max_tokens),
        "agents_yaml_path": st.session_state.agents_yaml_path,
        "skill_path": st.session_state.skill_path,
    }
    st.json(diag)
