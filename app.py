"""AI Content Studio — Higgsfield-style dark UI."""

import streamlit as st
import os, json
from datetime import datetime
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from utils.llm import call_llm, parse_json_response

load_dotenv()

st.set_page_config(
    page_title="AI Content Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

* { font-family: 'Inter', sans-serif !important; }

[data-testid="stAppViewContainer"] { background: #0a0a0a; }
[data-testid="stSidebar"] { background: #111111; border-right: 1px solid #222; }
[data-testid="stHeader"] { background: transparent; display: none; }
[data-testid="collapsedControl"] { display: none; }
.block-container { padding: 0 2rem 3rem; max-width: 100%; }


/* ── TOP NAV ── */
.hg-nav {
    background: #0a0a0a;
    border-bottom: 1px solid #1f1f1f;
    padding: 0.9rem 2rem;
    display: flex;
    align-items: center;
    gap: 2rem;
    margin: 0 -2rem 2rem;
    position: sticky; top: 0; z-index: 100;
}
.hg-logo {
    font-size: 1.1rem; font-weight: 900;
    color: #ffffff; letter-spacing: -0.02em;
    background: #C8FF00; color: #000;
    padding: 4px 10px; border-radius: 6px;
    margin-right: 1rem;
}
.hg-navlink {
    color: #888; font-size: 0.85rem; font-weight: 500;
    cursor: pointer; transition: color 0.2s;
    text-decoration: none;
}
.hg-navlink:hover { color: #fff; }
.hg-navlink.active { color: #fff; font-weight: 600; }
.hg-badge-new {
    background: #C8FF00; color: #000;
    font-size: 0.6rem; font-weight: 800;
    padding: 1px 5px; border-radius: 4px;
    margin-left: 4px; vertical-align: middle;
}

/* ── CARDS ── */
.hg-card {
    background: #141414;
    border: 1px solid #222;
    border-radius: 14px;
    overflow: hidden;
    transition: border-color 0.2s, transform 0.2s;
    cursor: pointer;
    position: relative;
}
.hg-card:hover {
    border-color: #C8FF00;
    transform: translateY(-2px);
}
.hg-card-body { padding: 1rem 1.2rem 1.2rem; }
.hg-card-label {
    font-size: 0.65rem; font-weight: 700;
    color: #C8FF00; text-transform: uppercase;
    letter-spacing: 0.1em; margin-bottom: 0.3rem;
}
.hg-card-title {
    font-size: 0.9rem; font-weight: 700;
    color: #ffffff; margin-bottom: 0.2rem;
}
.hg-card-desc { font-size: 0.78rem; color: #666; line-height: 1.4; }

/* ── PROMPT BOX ── */
.hg-prompt {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    font-family: 'SFMono-Regular', Consolas, monospace !important;
    font-size: 0.8rem; color: #d4d4d4;
    line-height: 1.6; white-space: pre-wrap;
    margin-bottom: 0.5rem;
}
.hg-scene-num {
    font-size: 0.65rem; font-weight: 700;
    color: #555; text-transform: uppercase;
    letter-spacing: 0.1em; margin-bottom: 0.4rem;
}

/* ── METRIC ── */
.hg-metric {
    background: #141414; border: 1px solid #222;
    border-radius: 12px; padding: 1.2rem;
    text-align: center;
}
.hg-metric-val { font-size: 2rem; font-weight: 800; color: #C8FF00; }
.hg-metric-lbl { font-size: 0.72rem; color: #555; margin-top: 4px; font-weight: 500; }

/* ── BUTTONS ── */
div[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    border: 1px solid #333 !important;
    background: #1a1a1a !important;
    color: #fff !important;
    transition: all 0.15s !important;
}
div[data-testid="stButton"] > button:hover {
    border-color: #C8FF00 !important;
    color: #C8FF00 !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: #C8FF00 !important;
    color: #000 !important;
    border: none !important;
    font-weight: 700 !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #aadd00 !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
    background: #141414; border-radius: 10px;
    padding: 4px; gap: 2px;
    border: 1px solid #222;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; color: #666;
    font-weight: 500; font-size: 0.85rem;
}
.stTabs [aria-selected="true"] {
    background: #262626 !important;
    color: #C8FF00 !important;
    font-weight: 700 !important;
}

/* ── INPUTS ── */
[data-testid="stTextArea"] textarea,
[data-testid="stTextInput"] input {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    color: #e5e5e5 !important;
    font-size: 0.9rem !important;
}
[data-testid="stTextArea"] textarea:focus,
[data-testid="stTextInput"] input:focus {
    border-color: #C8FF00 !important;
    box-shadow: 0 0 0 2px rgba(200,255,0,0.1) !important;
}

/* ── SELECTBOX ── */
[data-testid="stSelectbox"] > div > div {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 8px !important;
    color: #e5e5e5 !important;
}

/* ── FILE UPLOADER — drag & drop zone ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #0f0f0f !important;
    border: 1px dashed #333 !important;
    border-radius: 10px !important;
    padding: 0.8rem !important;
    min-height: unset !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color: #C8FF00 !important;
}
[data-testid="stFileUploaderDropzone"] > div > span {
    color: #555 !important;
    font-size: 0.78rem !important;
}
[data-testid="stFileUploaderDropzone"] > div > small {
    color: #333 !important;
    font-size: 0.7rem !important;
}
[data-testid="stFileUploaderDropzone"] > div > button {
    width: 100% !important;
    background: #1a1a1a !important;
    color: #C8FF00 !important;
    border: 1px solid #C8FF00 !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    padding: 0.5rem 1rem !important;
}

/* ── GALLERY GRID ── */
.hg-gallery-title {
    font-size: 0.7rem; font-weight: 700;
    color: #555; text-transform: uppercase;
    letter-spacing: 0.1em; margin: 1.5rem 0 0.8rem;
}

/* ── STATUS DOTS ── */
.dot { width:7px; height:7px; border-radius:50%; display:inline-block; margin-right:5px; }
.dot-g { background:#C8FF00; }
.dot-r { background:#ff4444; }

/* ── TAG ── */
.hg-tag {
    display:inline-block; background:#1a1a1a;
    border:1px solid #333; color:#888;
    border-radius:6px; padding:3px 10px;
    font-size:0.72rem; font-weight:500; margin:2px;
    cursor:pointer;
}
.hg-tag:hover { border-color:#C8FF00; color:#C8FF00; }

label { color: #888 !important; }
h1,h2,h3,h4 { color: #fff !important; }
p { color: #ccc; }
[data-testid="stExpander"] { background: #141414 !important; border: 1px solid #222 !important; border-radius: 10px !important; }
[data-testid="stExpander"] summary { color: #ccc !important; }
[data-testid="stMarkdownContainer"] p { color: #ccc; }
[data-testid="stCheckbox"] label { color: #ccc !important; }
[data-testid="stRadio"] label { color: #ccc !important; }
[data-testid="stSelectbox"] label { color: #888 !important; }
[data-testid="stFileUploader"] label { color: #888 !important; }
.stSpinner > div { border-top-color: #C8FF00 !important; }
[data-testid="stProgress"] > div > div { background: #C8FF00 !important; }
code { background: #1e1e1e !important; color: #C8FF00 !important; border-radius: 6px !important; }
[data-testid="stCodeBlock"] { background: #141414 !important; border: 1px solid #2a2a2a !important; border-radius: 10px !important; }
[data-testid="stCodeBlock"] code { color: #e0e0e0 !important; }
/* Большое окно чата */
section[data-testid="stMain"] .stChatMessageContainer {
    max-height: 520px !important;
    overflow-y: auto !important;
}
/* Поле ввода чата снизу */
.stChatInputContainer {
    border-top: 1px solid #1a1a1a !important;
    padding-top: 0.5rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─── DIRS ─────────────────────────────────────────────────────────────────────
_BASE = os.path.dirname(os.path.abspath(__file__))
BRAIN_DIR  = os.path.join(_BASE, "brain")
IMAGES_DIR = os.path.join(_BASE, "generated_output", "images")
VIDEOS_DIR = os.path.join(_BASE, "generated_output", "videos")
for _d in [BRAIN_DIR, IMAGES_DIR, VIDEOS_DIR]:
    os.makedirs(_d, exist_ok=True)

MEMORY_FILE = os.path.join(BRAIN_DIR, "agent_memory.txt")
ERRORS_FILE = os.path.join(BRAIN_DIR, "agent_errors.txt")


def load_brain() -> str:
    texts = []
    for fname in sorted(os.listdir(BRAIN_DIR)):
        if fname.endswith(".txt") and fname not in ("README.txt",):
            try:
                with open(os.path.join(BRAIN_DIR, fname), encoding="utf-8") as f:
                    texts.append(f"=== {fname} ===\n{f.read()}")
            except:
                pass
    return "\n\n".join(texts)


def agent_remember(insight: str):
    """Агент записывает новое знание в память."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(MEMORY_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}] {insight}\n")


def agent_log_error(error: str):
    """Агент записывает ошибку чтобы не повторять."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ERRORS_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}] ОШИБКА: {error}\n")


# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div style="font-size:1.2rem;font-weight:900;color:#fff;padding:0.5rem 0 1rem;border-bottom:1px solid #222;margin-bottom:1rem">🎬 AI Studio</div>', unsafe_allow_html=True)

    # ── API статус ──
    groq_ok = bool(os.getenv("GROQ_API_KEY"))
    gem_ok  = bool(os.getenv("GEMINI_API_KEY"))
    st.markdown(f"""
<div style="font-size:0.7rem;color:#555;margin-bottom:1rem">
  <span style="color:{'#C8FF00' if groq_ok else '#ff4444'}">●</span> Groq &nbsp;
  <span style="color:{'#C8FF00' if gem_ok else '#ff4444'}">●</span> Gemini
</div>""", unsafe_allow_html=True)

    # ── ПАПКА: МОЗГИ ──
    with st.expander("🧠 Знания агента", expanded=True):
        brain_files = [f for f in sorted(os.listdir(BRAIN_DIR)) if f.endswith(".txt")]
        up = st.file_uploader("Перетащи или выбери файл (.txt, .pdf)", type=["txt","pdf"], key="sb_brain_up", label_visibility="collapsed")
        if up:
            if up.name.lower().endswith(".pdf"):
                try:
                    import PyPDF2, io
                    reader = PyPDF2.PdfReader(io.BytesIO(up.read()))
                    text = "\n\n".join(p.extract_text() or "" for p in reader.pages)
                    save_name = up.name.replace(".pdf", ".txt")
                    with open(os.path.join(BRAIN_DIR, save_name), "w", encoding="utf-8") as f:
                        f.write(f"[Источник: {up.name}]\n\n{text}")
                    st.success(f"✅ PDF → {save_name} ({len(reader.pages)} стр.)")
                except Exception as e:
                    st.error(f"Ошибка PDF: {e}")
            else:
                with open(os.path.join(BRAIN_DIR, up.name), "wb") as f:
                    f.write(up.read())
                st.success(f"✅ {up.name}")
            st.rerun()
        for bf in brain_files:
            bcols = st.columns([5, 1])
            icon = "📋" if bf.startswith("agent_") else "📄"
            bcols[0].markdown(f'<div style="font-size:0.78rem;color:#aaa">{icon} {bf}</div>', unsafe_allow_html=True)
            with open(os.path.join(BRAIN_DIR, bf), "rb") as f:
                bcols[1].download_button("↓", f.read(), bf, key=f"dl_b_{bf}", use_container_width=True)

    # ── ПАПКА: ИЗОБРАЖЕНИЯ ──
    with st.expander("🖼️ Изображения", expanded=False):
        img_files = sorted([f for f in os.listdir(IMAGES_DIR) if f.lower().endswith((".png",".jpg",".jpeg"))], reverse=True)
        if img_files:
            for imf in img_files[:20]:
                ic1, ic2 = st.columns([5, 1])
                ic1.markdown(f'<div style="font-size:0.78rem;color:#aaa">🖼 {imf}</div>', unsafe_allow_html=True)
                with open(os.path.join(IMAGES_DIR, imf), "rb") as f:
                    ic2.download_button("↓", f.read(), imf, key=f"dl_i_{imf}", use_container_width=True)
        else:
            st.markdown('<div style="font-size:0.75rem;color:#444">Нет изображений</div>', unsafe_allow_html=True)

    # ── ПАПКА: ВИДЕО ──
    with st.expander("🎥 Видео", expanded=False):
        vid_files = sorted([f for f in os.listdir(VIDEOS_DIR) if f.lower().endswith(".mp4")], reverse=True)
        if vid_files:
            for vf in vid_files[:10]:
                vc1, vc2 = st.columns([5, 1])
                vc1.markdown(f'<div style="font-size:0.78rem;color:#aaa">🎬 {vf}</div>', unsafe_allow_html=True)
                with open(os.path.join(VIDEOS_DIR, vf), "rb") as f:
                    vc2.download_button("↓", f.read(), vf, key=f"dl_v_{vf}", use_container_width=True)
        else:
            st.markdown('<div style="font-size:0.75rem;color:#444">Нет видео</div>', unsafe_allow_html=True)

    # ── ЗАГРУЗКА ФОТО/ВИДЕО В ПАПКИ ──
    with st.expander("📤 Загрузить файлы", expanded=False):
        up_img = st.file_uploader("Фото в images/", type=["jpg","jpeg","png"], key="sb_up_img", label_visibility="collapsed")
        if up_img:
            with open(os.path.join(IMAGES_DIR, up_img.name), "wb") as f:
                f.write(up_img.read())
            st.success(f"✅ {up_img.name} → images/")
            st.rerun()
        up_vid = st.file_uploader("Видео в videos/", type=["mp4","mov"], key="sb_up_vid", label_visibility="collapsed")
        if up_vid:
            with open(os.path.join(VIDEOS_DIR, up_vid.name), "wb") as f:
                f.write(up_vid.read())
            st.success(f"✅ {up_vid.name} → videos/")
            st.rerun()

    st.divider()
    st.markdown(f'<div style="font-size:0.62rem;color:#2a2a2a;word-break:break-all">{_BASE}</div>', unsafe_allow_html=True)


# ─── NAV ──────────────────────────────────────────────────────────────────────
groq_ok = bool(os.getenv("GROQ_API_KEY"))
gem_ok  = bool(os.getenv("GEMINI_API_KEY"))

st.markdown(f"""
<div class="hg-nav">
  <span class="hg-logo">AI STUDIO</span>
  <div style="flex:1"></div>
  <span style="font-size:0.75rem;color:#555">
    <span class="dot {'dot-g' if groq_ok else 'dot-r'}"></span>Groq&nbsp;&nbsp;
    <span class="dot {'dot-g' if gem_ok else 'dot-r'}"></span>Gemini/Imagen
  </span>
</div>
""", unsafe_allow_html=True)

# Показываем предупреждение если ключи не найдены
if not groq_ok and not gem_ok:
    st.error("""
**API ключи не найдены!**

Создай файл `.env` в папке `C:\\Users\\tahir\\EMO\\` со следующим содержимым:

```
LLM_PROVIDER=gemini
GEMINI_API_KEY=твой_ключ_от_aistudio.google.com
GROQ_API_KEY=твой_ключ_от_console.groq.com
GROQ_MODEL=llama3-70b-8192
IMAGEN_MODEL=imagen-4.0-generate-001
VEO_MODEL=veo-3.0-generate-preview
VEO_RESOLUTION=720p
VEO_DURATION_SECONDS=5
```

Потом **перезапусти** `streamlit run app.py`
""")
elif not groq_ok:
    st.warning("⚠️ GROQ_API_KEY не найден — используется Gemini")
elif not gem_ok:
    st.warning("⚠️ GEMINI_API_KEY не найден — изображения и видео недоступны")

# ─── SIDEBAR (settings) ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Настройки")
    provider = st.selectbox("LLM", ["gemini","groq","openai"])
    os.environ["LLM_PROVIDER"] = provider

    gk = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY",""), type="password")
    mk = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY",""), type="password")
    if gk: os.environ["GROQ_API_KEY"] = gk
    if mk: os.environ["GEMINI_API_KEY"] = mk

    st.divider()
    img_model = st.selectbox("Imagen модель", [
        "imagen-4.0-generate-001",
        "imagen-4.0-ultra-generate-001",
        "imagen-3.0-generate-001",
    ])
    aspect = st.radio("Формат", ["16:9","9:16","1:1","4:3"], horizontal=True)
    os.environ["IMAGEN_MODEL"] = img_model

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs(["🚀  Генератор", "🖼️  Изображения", "📋  История", "💬  Чат", "⚡  Пакет"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    cl, cr = st.columns([3, 1], gap="large")

    with cl:
        st.markdown('<div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:0.3rem">Создай вирусный контент</div>', unsafe_allow_html=True)
        st.markdown('<div style="color:#555;font-size:0.9rem;margin-bottom:1.5rem">Идея → Сценарий → Сторибоард → Промты → Изображения</div>', unsafe_allow_html=True)

        topic = st.text_area("", placeholder="Введи тему...\n\nНапример: 5 секретов богатых людей\nили: психология влияния\nили: как заработать первый миллион", height=130, label_visibility="collapsed")

        cb1, cb2 = st.columns([2,2])
        with cb1:
            run_btn = st.button("▶  СОЗДАТЬ КОНТЕНТ", type="primary", use_container_width=True)
        with cb2:
            gen_media = st.checkbox("🎨 Генерировать изображения", value=False)

    with cr:
        st.markdown('<div style="color:#555;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem">Фото-референс</div>', unsafe_allow_html=True)
        ref_file = st.file_uploader("📎 Загрузить референс", type=["jpg","jpeg","png","webp"])
        if ref_file:
            st.image(Image.open(ref_file), use_container_width=True)
            st.markdown('<div style="color:#C8FF00;font-size:0.75rem;margin-top:0.3rem">✓ Добавится к промтам</div>', unsafe_allow_html=True)

    if run_btn:
        from main import run_pipeline
        ref_note = ", reference style from uploaded image" if ref_file else ""
        prog_bar = st.progress(0, text="Генерирую идею...")
        try:
            with st.spinner(""):
                prog_bar.progress(10, "Генерирую идею...")
                from main import generate_idea, write_script, inspect_script, create_storyboard, generate_photo_prompts, generate_video_prompts, generate_packaging
                idea = generate_idea(topic or None)
                prog_bar.progress(25, "Пишу сценарий...")
                script = write_script(idea)
                prog_bar.progress(40, "Инспектирую...")
                inspection = inspect_script(script)
                prog_bar.progress(55, "Создаю сторибоард...")
                scenes = create_storyboard(script)
                prog_bar.progress(70, "Генерирую промты...")
                photo_prompts = generate_photo_prompts(scenes)
                video_prompts = generate_video_prompts(photo_prompts)
                prog_bar.progress(85, "Паковка...")
                packaging = generate_packaging(idea, script)
                prog_bar.progress(100, "Готово!")
                result = {"idea": idea, "script": script, "inspection": inspection,
                          "scenes": scenes, "photo_prompts": photo_prompts,
                          "video_prompts": video_prompts, "packaging": packaging,
                          "timestamp": datetime.now().strftime('%Y%m%d_%H%M%S')}
                os.makedirs("generated_output", exist_ok=True)
                with open(f"generated_output/result_{result['timestamp']}.json","w",encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception as e:
            st.error(f"Ошибка: {e}")
            st.stop()
        prog_bar.empty()

        st.markdown("<br>", unsafe_allow_html=True)

        # Метрики
        score = result["inspection"].get("total", 0)
        color = "#C8FF00" if score >= 80 else "#ff8800" if score >= 60 else "#ff4444"
        m1,m2,m3,m4 = st.columns(4)
        for col, val, lbl, c in [
            (m1, score, "Оценка /100", color),
            (m2, len(result["scenes"]), "Сцен", "#C8FF00"),
            (m3, "✓ ОК" if result["inspection"].get("passed") else "⚠ Слабо", "Инспекция", "#C8FF00" if result["inspection"].get("passed") else "#ff8800"),
            (m4, len(result["photo_prompts"]), "Промтов", "#C8FF00"),
        ]:
            col.markdown(f'<div class="hg-metric"><div class="hg-metric-val" style="color:{c}">{val}</div><div class="hg-metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        r1,r2,r3,r4,r5 = st.tabs(["📝 Сценарий","🎬 Сторибоард","🖼️ Фото-промты","🎥 Видео-промты","📦 Паковка"])

        with r1:
            st.text_area("", result["script"].get("full_script",""), height=300, label_visibility="collapsed")
            st.download_button("📥 Скачать", result["script"].get("full_script",""), "script.txt", use_container_width=True)

        with r2:
            for s in result["scenes"]:
                with st.expander(f"▶  Сцена {s['scene_number']}  ·  {s.get('duration_seconds','?')} сек  ·  {s.get('mood','')}"):
                    st.markdown(f"<span style='color:#888'>Текст:</span> <span style='color:#ddd'>{s.get('narration','')}</span>", unsafe_allow_html=True)
                    st.markdown(f"<span style='color:#888'>Визуал:</span> <span style='color:#ddd'>{s.get('visual_description','')}</span>", unsafe_allow_html=True)

        with r3:
            for item in result["photo_prompts"]:
                prompt = item["prompt"] + ref_note
                st.markdown(f'<div class="hg-scene-num">Сцена {item["scene_number"]}</div>', unsafe_allow_html=True)
                st.code(prompt, language=None)
                ca, cb = st.columns(2)
                with ca:
                    if st.button(f"🎨 Генерировать изображение", key=f"gp{item['scene_number']}"):
                        with st.spinner("Google Imagen 4..."):
                            from utils.google_image import generate_image
                            os.makedirs("generated_output/images", exist_ok=True)
                            out = f"generated_output/images/scene_{item['scene_number']:02d}.png"
                            p = generate_image(prompt, out, aspect_ratio=aspect)
                        if p and os.path.exists(p):
                            st.image(p, use_container_width=True)
                            with open(p,"rb") as f:
                                st.download_button("📥", f.read(), os.path.basename(p), key=f"dp{item['scene_number']}")

        with r4:
            for item in result["video_prompts"]:
                st.markdown(f'<div class="hg-scene-num">Сцена {item["scene_number"]}</div>', unsafe_allow_html=True)
                st.code(item["prompt"], language=None)

        with r5:
            pkg = result["packaging"]
            st.markdown('<div style="color:#C8FF00;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:0.8rem">Заголовки</div>', unsafe_allow_html=True)
            for i, t in enumerate(pkg.get("titles",[]), 1):
                c1,c2 = st.columns([5,1])
                with c1: st.markdown(f'<div style="color:#fff;font-size:0.95rem;padding:0.5rem 0"><b>{i}.</b> {t}</div>', unsafe_allow_html=True)
                with c2: st.code(t, language=None)

            st.markdown('<div style="color:#C8FF00;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:1rem 0 0.5rem">Хэштеги</div>', unsafe_allow_html=True)
            tags = " ".join(pkg.get("hashtags",[]))
            st.code(tags)

            st.divider()
            c1,c2 = st.columns(2)
            c1.download_button("📥 JSON", json.dumps(result, ensure_ascii=False, indent=2), f"result_{result['timestamp']}.json", "application/json", use_container_width=True)
            report = f"AI CONTENT STUDIO\n{'='*50}\n{result['idea'].get('idea','')}\n\n{result['script'].get('full_script','')}\n\nОценка: {result['inspection'].get('total')}/100\n\n{chr(10).join(pkg.get('titles',[]))}\n\n{tags}"
            c2.download_button("📥 Текст", report, f"report_{result['timestamp']}.txt", use_container_width=True)

        # Медиа
        if gen_media:
            imgs = sorted([f for f in os.listdir("generated_output/images") if f.endswith((".png",".jpg"))]) if os.path.exists("generated_output/images") else []
            if imgs:
                st.markdown('<div class="hg-gallery-title">Сгенерированные изображения</div>', unsafe_allow_html=True)
                gcols = st.columns(3)
                for i, name in enumerate(imgs):
                    p = os.path.join("generated_output/images", name)
                    with gcols[i%3]:
                        st.image(p, use_container_width=True)
                        with open(p,"rb") as f:
                            st.download_button("📥", f.read(), name, key=f"gm{i}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — IMAGE GENERATOR
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:0.3rem">Генератор изображений</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#555;font-size:0.9rem;margin-bottom:1.5rem">Google Imagen 4 · Прямая генерация</div>', unsafe_allow_html=True)

    ci1, ci2 = st.columns([1, 1], gap="large")

    # Соотношение сторон → CSS размеры для превью
    ASPECT_CSS = {
        "16:9": ("100%", "56.25%"),   # width, padding-bottom
        "9:16": ("56.25%", "100%"),
        "1:1":  ("100%", "100%"),
        "4:3":  ("100%", "75%"),
    }

    with ci1:
        ref2 = st.file_uploader("📎 Загрузить фото", type=["jpg","jpeg","png","webp"], key="ref2")
        if ref2:
            st.image(Image.open(ref2), use_container_width=True)

        ip = st.text_area("", placeholder="Опиши изображение...\n\n3D Pixar style, cinematic scene of...", height=120, label_visibility="collapsed", key="ip2")

        st.markdown('<div style="color:#555;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin:0.8rem 0 0.5rem">Быстрые стили</div>', unsafe_allow_html=True)
        STYLES = {
            "🎭 Pixar 3D":    "3D Pixar animation style, vibrant colors, cinematic lighting, 8k",
            "📸 Фото":        "photorealistic, professional photography, 8k, sharp focus",
            "🎨 Аниме":       "anime style, detailed illustration, vibrant, Studio Ghibli",
            "🎬 Cinematic":   "cinematic film still, dramatic lighting, anamorphic lens, 4k",
        }
        sc = st.columns(2)
        for i,(lbl,sty) in enumerate(STYLES.items()):
            with sc[i%2]:
                if st.button(lbl, use_container_width=True, key=f"sty{i}"):
                    st.session_state["sty"] = sty
        sty = st.session_state.get("sty","")
        full_p = f"{ip}, {sty}".strip(", ") if sty and ip else (ip or sty)
        if sty:
            st.markdown(f'<div style="background:#141414;border:1px solid #C8FF00;border-radius:8px;padding:0.5rem 0.8rem;font-size:0.75rem;color:#C8FF00;margin-top:0.5rem">+ {sty}</div>', unsafe_allow_html=True)

        n_img = st.select_slider("Количество", [1,2,3,4], value=1)
        gcols_btn = st.columns([3,1])
        with gcols_btn[0]:
            go = st.button("🎨  ГЕНЕРИРОВАТЬ", type="primary", use_container_width=True)
        with gcols_btn[1]:
            if st.button("🗑", use_container_width=True, help="Сбросить результат"):
                st.session_state.pop("gen_images", None)

    with ci2:
        st.markdown('<div style="color:#555;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem">Результат</div>', unsafe_allow_html=True)

        if go and full_p:
            st.session_state.pop("gen_images", None)
            from utils.google_image import generate_image
            os.makedirs("generated_output/images", exist_ok=True)
            prog = st.progress(0)
            generated = []
            for i in range(n_img):
                with st.spinner(f"Генерирую {i+1}/{n_img}..."):
                    ts = datetime.now().strftime("%H%M%S%f")[:12]
                    out = f"generated_output/images/img_{ts}_{i}.png"
                    p = generate_image(full_p, out, aspect_ratio=aspect)
                prog.progress((i+1)/n_img)
                if p and os.path.exists(p):
                    generated.append(p)
            prog.empty()
            st.session_state["gen_images"] = generated
        elif go:
            st.warning("Введи промт")

        # Вычисляем CSS для текущего aspect ratio
        ar = aspect  # берём из sidebar
        max_w = "320px" if ar == "9:16" else "100%"
        img_style = f"max-width:{max_w};border-radius:10px;display:block;margin:0 auto"

        gen_imgs = st.session_state.get("gen_images", [])
        if gen_imgs:
            for i, p in enumerate(gen_imgs):
                if os.path.exists(p):
                    st.image(p, use_container_width=(ar != "9:16"), width=300 if ar == "9:16" else None)
                    with open(p,"rb") as f:
                        st.download_button(f"📥 Скачать {i+1}", f.read(), os.path.basename(p), key=f"mi{i}", use_container_width=True)
        else:
            st.markdown("""
<div style="border:2px dashed #222;border-radius:14px;padding:4rem 2rem;text-align:center;color:#333;font-size:0.85rem">
  Изображение появится здесь
</div>""", unsafe_allow_html=True)

    # Галерея
    imgs_dir = "generated_output/images"
    all_imgs = sorted([f for f in os.listdir(imgs_dir) if f.endswith((".png",".jpg"))], reverse=True) if os.path.exists(imgs_dir) else []
    if all_imgs:
        st.markdown('<div class="hg-gallery-title">Галерея</div>', unsafe_allow_html=True)
        gcols = st.columns(5)
        for i, name in enumerate(all_imgs[:20]):
            p = os.path.join(imgs_dir, name)
            with gcols[i%5]:
                st.image(p, use_container_width=True)
                with open(p,"rb") as f:
                    st.download_button("📥", f.read(), name, key=f"gal{i}")
    else:
        st.markdown('<div style="border:2px dashed #1a1a1a;border-radius:14px;padding:3rem;text-align:center;color:#333;margin-top:2rem">Галерея пуста</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — HISTORY
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:1.5rem">История генераций</div>', unsafe_allow_html=True)
    rdir = "generated_output"
    os.makedirs(rdir, exist_ok=True)
    files = sorted([f for f in os.listdir(rdir) if f.startswith("result_") and f.endswith(".json")], reverse=True)

    if files:
        sel = st.selectbox("", files, format_func=lambda x: x.replace("result_","").replace(".json",""), label_visibility="collapsed")
        with open(os.path.join(rdir, sel), encoding="utf-8") as f:
            h = json.load(f)

        hm1,hm2,hm3 = st.columns(3)
        hm1.markdown(f'<div class="hg-metric"><div class="hg-metric-val">{h["inspection"].get("total","?")}</div><div class="hg-metric-lbl">Оценка /100</div></div>', unsafe_allow_html=True)
        hm2.markdown(f'<div class="hg-metric"><div class="hg-metric-val">{len(h.get("scenes",[]))}</div><div class="hg-metric-lbl">Сцен</div></div>', unsafe_allow_html=True)
        hm3.markdown(f'<div class="hg-metric"><div class="hg-metric-val">{h.get("timestamp","")[:8]}</div><div class="hg-metric-lbl">Дата</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f'<div style="background:#141414;border:1px solid #C8FF00;border-radius:10px;padding:1rem 1.2rem;color:#fff;font-size:0.95rem">{h["idea"].get("idea","")}</div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        with st.expander("📝 Сценарий"):
            st.markdown(f'<div style="color:#ccc;font-size:0.85rem;line-height:1.7">{h["script"].get("full_script","")}</div>', unsafe_allow_html=True)
        with st.expander("🖼️ Промты"):
            for p in h.get("photo_prompts",[]):
                st.code(p["prompt"], language=None)
        with st.expander("📦 Хэштеги"):
            st.code(" ".join(h.get("packaging",{}).get("hashtags",[])))

        st.download_button("📥 Скачать JSON", json.dumps(h, ensure_ascii=False, indent=2), sel, "application/json", use_container_width=True)
    else:
        st.markdown('<div style="border:2px dashed #1a1a1a;border-radius:14px;padding:4rem;text-align:center;color:#333">История пуста — запусти генерацию</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — CHAT
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    # Заголовок + провайдер
    chat_prov_cols = st.columns([3,1])
    with chat_prov_cols[0]:
        st.markdown('<div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:0.3rem">🧠 Чат с AI</div>', unsafe_allow_html=True)
    with chat_prov_cols[1]:
        chat_provider = st.selectbox("", ["groq","gemini"], label_visibility="collapsed", key="chat_prov")
    brain_files_count = len([f for f in os.listdir(BRAIN_DIR) if f.endswith(".txt")])
    model_label = "Llama 3.1-8b" if chat_provider == "groq" else "Gemini 2.0 Flash"
    status_txt = f"📚 {brain_files_count} файлов в базе знаний" if brain_files_count else "База знаний пуста — загрузи .txt в сайдбаре"
    st.markdown(f'<div style="color:#555;font-size:0.85rem;margin-bottom:1rem">{model_label} · {status_txt}</div>', unsafe_allow_html=True)

    # ── ИСТОРИЯ ЧАТА ─────────────────────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Привет! Загрузи .txt файлы в 🧠 Знания агента (слева) — и я буду действовать строго по твоей системе. Пиши — помогу с контентом."}
        ]

    for msg in st.session_state.chat_messages:
        is_user = msg["role"] == "user"
        bg = "#1a1a1a" if is_user else "#141414"
        border = "#333" if is_user else "#C8FF00"
        align = "flex-end" if is_user else "flex-start"
        label = "Ты" if is_user else "AI"
        label_color = "#888" if is_user else "#C8FF00"
        img_note = '<div style="font-size:0.72rem;color:#C8FF00;margin-bottom:0.3rem">📎 + фото референс</div>' if msg.get("has_image") else ""
        st.markdown(f"""
<div style="display:flex;justify-content:{align};margin:0.5rem 0">
  <div style="max-width:82%;background:{bg};border:1px solid {border};border-radius:14px;padding:0.85rem 1.1rem">
    <div style="font-size:0.65rem;color:{label_color};font-weight:700;margin-bottom:0.3rem;text-transform:uppercase;letter-spacing:0.08em">{label}</div>
    {img_note}
    <div style="color:#e0e0e0;font-size:0.92rem;line-height:1.7;white-space:pre-wrap">{msg["content"]}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── ФОТО РЕФЕРЕНС + ОЧИСТИТЬ ─────────────────────────────────
    ref_col1, ref_col2 = st.columns([5, 1])
    with ref_col1:
        chat_ref = st.file_uploader("📎 Фото референс", type=["jpg","jpeg","png","webp"], key="chat_ref", label_visibility="collapsed")
    with ref_col2:
        if len(st.session_state.chat_messages) > 1:
            if st.button("🗑", key="clear_chat", use_container_width=True, help="Очистить чат"):
                st.session_state.chat_messages = [st.session_state.chat_messages[0]]
                st.rerun()
    if chat_ref:
        st.image(Image.open(chat_ref), width=160)

    # ── ПОЛЕ ВВОДА ───────────────────────────────────────────────
    user_input = st.chat_input("Напиши сообщение... (Enter отправляет)", key="chat_input")

    if user_input and user_input.strip():
        has_ref = chat_ref is not None
        st.session_state.chat_messages.append({"role": "user", "content": user_input, "has_image": has_ref})

        chat_prov = st.session_state.get("chat_prov", "groq")
        brain_content = load_brain()
        ref_note = "\n\nПользователь прислал фото-референс — учти его при создании контента." if has_ref else ""

        if brain_content:
            sys_prompt = f"""Ты AI-агент для создания контента. Действуй СТРОГО по системе из базы знаний ниже.
После каждого ответа мысленно запоминай ключевые инсайты.
Отвечай на русском языке.

БАЗА ЗНАНИЙ:
{brain_content[:7000]}

Если вопрос не касается базы знаний — скажи: "Этой информации нет в базе знаний."{ref_note}"""
        else:
            sys_prompt = f"Ты профессиональный AI-ассистент по созданию вирусного контента для TikTok, YouTube Shorts и Instagram Reels. Отвечай на русском языке.{ref_note}"

        try:
            with st.spinner("AI думает..."):
                history_text = ""
                for m in st.session_state.chat_messages[:-1]:
                    role = "Пользователь" if m["role"] == "user" else "AI"
                    history_text += f"{role}: {m['content']}\n"
                full_prompt = (history_text + f"Пользователь: {user_input}") if history_text else user_input
                reply = call_llm(full_prompt, system_prompt=sys_prompt, provider=chat_prov)

            # Агент записывает ключевые знания из диалога
            if len(st.session_state.chat_messages) % 5 == 0:
                try:
                    insight_prompt = f"Извлеки 1-2 ключевых инсайта из этого диалога (одна строка):\nВопрос: {user_input}\nОтвет: {reply[:300]}"
                    insight = call_llm(insight_prompt, system_prompt="Ты архивариус. Кратко запиши суть.", provider=chat_prov)
                    agent_remember(insight.strip()[:200])
                except:
                    pass

        except Exception as e:
            reply = f"⚠️ Ошибка: {e}"
            agent_log_error(f"{user_input[:80]} → {str(e)[:120]}")

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — BATCH GENERATION
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:0.3rem">Сторибоард · Пакетная генерация</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#555;font-size:0.9rem;margin-bottom:1.5rem">Imagen 4 · Veo 3 · Все сцены за один запуск</div>', unsafe_allow_html=True)

    from utils.batch import estimate_batch_cost, estimate_video_cost

    # ── Загрузка данных ──
    rdir = "generated_output"
    os.makedirs(rdir, exist_ok=True)
    result_files = sorted([f for f in os.listdir(rdir) if f.startswith("result_") and f.endswith(".json")], reverse=True)

    if not result_files:
        st.markdown('<div style="border:2px dashed #1a1a1a;border-radius:14px;padding:4rem;text-align:center;color:#555">Нет данных — сначала запусти <b style="color:#C8FF00">Генератор</b></div>', unsafe_allow_html=True)
    else:
        # Выбор генерации
        sel_file = st.selectbox("", result_files,
                                format_func=lambda x: x.replace("result_","").replace(".json",""),
                                label_visibility="collapsed", key="batch_sel")
        with open(os.path.join(rdir, sel_file), encoding="utf-8") as f:
            bdata = json.load(f)

        photo_prompts_raw = bdata.get("photo_prompts", [])
        video_prompts_raw = bdata.get("video_prompts", [])
        scenes_raw        = bdata.get("scenes", [])

        # Индексы для быстрого поиска
        vid_prompt_map = {p["scene_number"]: p["prompt"] for p in video_prompts_raw}
        scene_map      = {s["scene_number"]: s for s in scenes_raw}

        # ── Настройки ──
        cfg1, cfg2, cfg3, cfg4 = st.columns(4)
        with cfg1:
            batch_aspect = st.radio("Формат", ["16:9","9:16","1:1","4:3"], horizontal=True, key="ba")
        with cfg2:
            batch_dur = st.select_slider("Длительность", [5, 8], value=5, key="bd")
        with cfg3:
            batch_res = st.radio("Разрешение", ["720p","1080p"], horizontal=True, key="br")
        with cfg4:
            n = len(photo_prompts_raw)
            img_cost = n * 0.04
            vid_cost_total = n * estimate_video_cost(batch_dur, batch_res)
            st.markdown(f'<div class="hg-metric" style="margin-top:0"><div class="hg-metric-val" style="font-size:1.2rem;color:#C8FF00">${img_cost:.2f} + ${vid_cost_total:.2f}</div><div class="hg-metric-lbl">фото + видео ({n} сцен)</div></div>', unsafe_allow_html=True)

        st.divider()

        # ════════════════════════════════════════════════════
        # СТОРИБОАРД — сетка сцен
        # ════════════════════════════════════════════════════
        st.markdown('<div style="color:#C8FF00;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:1rem">Сторибоард</div>', unsafe_allow_html=True)

        COLS = 3
        sb_cols = st.columns(COLS)

        for idx, pp in enumerate(photo_prompts_raw):
            n_scene = pp["scene_number"]
            img_path = f"generated_output/images/scene_{n_scene:02d}.png"
            vid_path = f"generated_output/videos/scene_{n_scene:02d}.mp4"
            scene_info = scene_map.get(n_scene, {})
            vid_prompt  = vid_prompt_map.get(n_scene, pp["prompt"])

            with sb_cols[idx % COLS]:
                # Номер сцены + длительность
                _dur = scene_info.get("duration_seconds", "?")
                _mood = scene_info.get("mood", "")
                st.markdown(f'<div style="color:#C8FF00;font-size:0.65rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.3rem">СЦЕНА {n_scene} · {_dur} сек · {_mood}</div>', unsafe_allow_html=True)

                # Фото (если есть — показать, иначе заглушка)
                if os.path.exists(img_path):
                    st.image(img_path, use_container_width=True)
                    with open(img_path, "rb") as fh:
                        st.download_button("📥 фото", fh.read(), f"scene_{n_scene:02d}.png", key=f"sb_dl_img_{n_scene}")
                else:
                    st.markdown(f'''
<div style="background:#0f0f0f;border:2px dashed #2a2a2a;border-radius:10px;
            aspect-ratio:16/9;display:flex;align-items:center;justify-content:center;
            color:#333;font-size:0.75rem;text-align:center;padding:1rem">
  🖼️ Сцена {n_scene}<br>фото не сгенерировано
</div>''', unsafe_allow_html=True)

                # Видео (если есть)
                if os.path.exists(vid_path):
                    st.video(vid_path)
                    with open(vid_path, "rb") as fh:
                        st.download_button("📥 видео", fh.read(), f"scene_{n_scene:02d}.mp4", key=f"sb_dl_vid_{n_scene}")

                # Описание сцены
                if scene_info.get("narration"):
                    st.markdown(f'<div style="color:#666;font-size:0.72rem;font-style:italic;margin:0.4rem 0 0.2rem;line-height:1.4">🎙 {scene_info["narration"][:100]}...</div>', unsafe_allow_html=True)

                # Видео промт
                st.markdown(f'<div style="background:#0d0d0d;border:1px solid #1e1e1e;border-radius:8px;padding:0.5rem 0.7rem;font-size:0.7rem;color:#555;line-height:1.5;margin-bottom:1rem">{vid_prompt[:180]}{"..." if len(vid_prompt)>180 else ""}</div>', unsafe_allow_html=True)

        st.divider()

        # ── Кнопки запуска ──
        btn_c1, btn_c2, btn_c3 = st.columns(3)
        with btn_c1:
            run_img_btn = st.button("🖼️  ГЕНЕРИРОВАТЬ ФОТО", type="primary", use_container_width=True)
        with btn_c2:
            run_vid_btn = st.button("🎥  ГЕНЕРИРОВАТЬ ВИДЕО", type="primary", use_container_width=True)
        with btn_c3:
            run_all_btn = st.button("⚡  ВСЁ СРАЗУ", type="primary", use_container_width=True)

        do_img_now = run_img_btn or run_all_btn
        do_vid_now = run_vid_btn or run_all_btn

        if do_img_now or do_vid_now:
            from utils.batch import batch_generate_images, batch_generate_videos

            batch_input = [{"scene_number": p["scene_number"], "prompt": p["prompt"]}
                           for p in photo_prompts_raw]
            vid_input   = [{"scene_number": p["scene_number"], "prompt": p["prompt"]}
                           for p in video_prompts_raw]

            st.markdown('<div style="color:#C8FF00;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:1rem 0 0.5rem">Прогресс</div>', unsafe_allow_html=True)

            # Строки прогресса по сценам
            prog_rows = {}
            for p in photo_prompts_raw:
                ph = st.empty()
                ph.markdown(f'<div style="background:#141414;border:1px solid #333;border-radius:8px;padding:0.4rem 1rem;margin:2px 0;font-size:0.8rem;color:#444">⏳ Сцена {p["scene_number"]}...</div>', unsafe_allow_html=True)
                prog_rows[p["scene_number"]] = ph

            def _upd(sn, status, path, kind):
                icons = {"ok":"✅","error":"❌","timeout":"⏰","pending":"⏳"}
                colors = {"ok":"#C8FF00","error":"#ff4444","timeout":"#ff8800","pending":"#444"}
                labels = {"ok":"готово","error":"ошибка","timeout":"таймаут","pending":"..."}
                ic = icons.get(status,"⏳"); cl = colors.get(status,"#444"); lb = labels.get(status,status)
                prog_rows[sn].markdown(
                    f'<div style="background:#141414;border:1px solid {cl}33;border-radius:8px;padding:0.4rem 1rem;margin:2px 0;font-size:0.8rem;color:{cl}">{ic} Сцена {sn} {kind} — {lb}</div>',
                    unsafe_allow_html=True)

            img_results, vid_results = [], []

            if do_img_now:
                img_results = batch_generate_images(batch_input, batch_aspect,
                                                    lambda sn, st_, p: _upd(sn, st_, p, "фото"))

            if do_vid_now:
                vid_results = batch_generate_videos(vid_input, batch_dur, batch_res,
                                                    lambda sn, st_, p: _upd(sn, st_, p, "видео"))

            ok_img = sum(1 for r in img_results if r.get("status") == "ok")
            ok_vid = sum(1 for r in vid_results if r.get("status") == "ok")
            st.markdown(f'<div style="background:#141414;border:1px solid #C8FF00;border-radius:12px;padding:1rem 1.5rem;font-size:0.9rem;color:#fff;margin-top:1rem">✅ Готово: <b style="color:#C8FF00">{ok_img} фото</b> · <b style="color:#C8FF00">{ok_vid} видео</b> — обнови страницу чтобы увидеть в сторибоарде</div>', unsafe_allow_html=True)

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown('<br><div style="text-align:center;color:#333;font-size:0.75rem;border-top:1px solid #1a1a1a;padding-top:1rem">AI Content Studio · Groq + Google Imagen 4 + Veo</div>', unsafe_allow_html=True)
