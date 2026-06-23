"""AI Content Studio — Higgsfield-style dark UI."""

import streamlit as st
import os, json
from datetime import datetime
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Content Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
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

/* ── FILE UPLOADER — button only, no drag zone ── */
[data-testid="stFileUploader"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: #141414 !important;
    border: 1px solid #2a2a2a !important;
    border-radius: 10px !important;
    padding: 0.5rem !important;
    min-height: unset !important;
}
/* hide drag-drop instructional text, keep only button */
[data-testid="stFileUploaderDropzone"] > div > span,
[data-testid="stFileUploaderDropzone"] > div > small {
    display: none !important;
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
</style>
""", unsafe_allow_html=True)

# ─── NAV ──────────────────────────────────────────────────────────────────────
groq_ok = bool(os.getenv("GROQ_API_KEY"))
gem_ok  = bool(os.getenv("GEMINI_API_KEY"))

st.markdown(f"""
<div class="hg-nav">
  <span class="hg-logo">AI STUDIO</span>
  <div style="flex:1"></div>
  <span style="font-size:0.75rem;color:#555">
    <span class="dot {'dot-g' if groq_ok else 'dot-r'}"></span>Groq&nbsp;&nbsp;
    <span class="dot {'dot-g' if gem_ok else 'dot-r'}"></span>Imagen
  </span>
</div>
""", unsafe_allow_html=True)

# ─── SIDEBAR (settings) ───────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Настройки")
    provider = st.selectbox("LLM", ["groq","gemini","openai"])
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
    # Выбор провайдера чата
    chat_prov_cols = st.columns([3,1])
    with chat_prov_cols[0]:
        st.markdown('<div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:0.3rem">Чат с AI</div>', unsafe_allow_html=True)
    with chat_prov_cols[1]:
        chat_provider = st.selectbox("", ["gemini","groq"], label_visibility="collapsed", key="chat_prov")
    model_label = "Gemini 1.5 Flash" if chat_provider == "gemini" else "Llama3-70b"
    st.markdown(f'<div style="color:#555;font-size:0.9rem;margin-bottom:1.5rem">{model_label} · Помощник по контенту</div>', unsafe_allow_html=True)

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Привет! Я AI-ассистент для создания контента. Могу помочь с идеями для видео, написать сценарий, придумать хэштеги или ответить на любой вопрос. Что создаём?"}
        ]

    # Отображение истории чата
    for msg in st.session_state.chat_messages:
        is_user = msg["role"] == "user"
        bg = "#1a1a1a" if is_user else "#141414"
        border = "#333" if is_user else "#C8FF00"
        align = "flex-end" if is_user else "flex-start"
        label = "Ты" if is_user else "AI"
        label_color = "#888" if is_user else "#C8FF00"
        st.markdown(f"""
<div style="display:flex;justify-content:{align};margin:0.4rem 0">
  <div style="max-width:75%;background:{bg};border:1px solid {border};border-radius:12px;padding:0.75rem 1rem">
    <div style="font-size:0.65rem;color:{label_color};font-weight:700;margin-bottom:0.3rem;text-transform:uppercase;letter-spacing:0.08em">{label}</div>
    <div style="color:#e0e0e0;font-size:0.9rem;line-height:1.6;white-space:pre-wrap">{msg["content"]}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # Быстрые промты
    st.markdown("<br>", unsafe_allow_html=True)
    quick_col = st.columns(4)
    quick_prompts = [
        "💡 Придумай идею для вирусного видео",
        "✍️ Напиши хук для Reels",
        "📦 Придумай 5 хэштегов",
        "🎬 Структура сценария 60 сек",
    ]
    for i, qp in enumerate(quick_prompts):
        with quick_col[i]:
            if st.button(qp, use_container_width=True, key=f"qp{i}"):
                st.session_state["chat_input_prefill"] = qp.split(" ", 1)[1]
                st.rerun()

    # Поле ввода
    prefill = st.session_state.pop("chat_input_prefill", "")
    chat_cols = st.columns([8, 1])
    with chat_cols[0]:
        user_input = st.text_input("", value=prefill, placeholder="Напиши сообщение...", label_visibility="collapsed", key="chat_input")
    with chat_cols[1]:
        send_btn = st.button("➤", type="primary", use_container_width=True)

    if (send_btn or (user_input and st.session_state.get("_last_chat") != user_input)) and user_input.strip():
        st.session_state["_last_chat"] = user_input
        st.session_state.chat_messages.append({"role": "user", "content": user_input})

        # Запрос к AI
        import requests as req
        chat_prov = st.session_state.get("chat_prov", "gemini")
        sys_prompt = "Ты профессиональный AI-ассистент для создания вирусного контента для TikTok, YouTube Shorts и Instagram Reels. Отвечай на русском языке, кратко и по делу. Помогаешь с идеями, сценариями, промтами для изображений, хэштегами."

        try:
            with st.spinner("AI думает..."):
                if chat_prov == "gemini":
                    api_key = os.getenv("GEMINI_API_KEY")
                    if not api_key:
                        raise ValueError("GEMINI_API_KEY не найден")
                    model_name = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"
                    # Собираем историю в формат Gemini
                    contents = []
                    for m in st.session_state.chat_messages:
                        role = "user" if m["role"] == "user" else "model"
                        contents.append({"role": role, "parts": [{"text": m["content"]}]})
                    payload = {
                        "system_instruction": {"parts": [{"text": sys_prompt}]},
                        "contents": contents,
                        "generationConfig": {"maxOutputTokens": 1024, "temperature": 0.8}
                    }
                    resp = req.post(url, json=payload, params={"key": api_key}, timeout=30)
                    if resp.status_code == 200:
                        reply = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                    else:
                        raise ValueError(f"Gemini {resp.status_code}: {resp.text[:200]}")
                else:
                    api_key = os.getenv("GROQ_API_KEY")
                    if not api_key:
                        raise ValueError("GROQ_API_KEY не найден")
                    messages_payload = [{"role": "system", "content": sys_prompt}] + \
                        [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat_messages]
                    resp = req.post(
                        "https://api.groq.com/openai/v1/chat/completions",
                        json={"model": os.getenv("GROQ_MODEL","llama3-70b-8192"), "messages": messages_payload, "max_tokens": 1024, "temperature": 0.8},
                        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                        timeout=30
                    )
                    if resp.status_code == 200:
                        reply = resp.json()["choices"][0]["message"]["content"]
                    else:
                        raise ValueError(f"Groq {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            reply = f"⚠️ Ошибка: {e}"

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
        st.rerun()

    # Кнопка очистки чата
    if len(st.session_state.chat_messages) > 1:
        if st.button("🗑 Очистить чат", key="clear_chat"):
            st.session_state.chat_messages = [st.session_state.chat_messages[0]]
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — BATCH GENERATION
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div style="font-size:1.8rem;font-weight:900;color:#fff;margin-bottom:0.3rem">Пакетная генерация</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#555;font-size:0.9rem;margin-bottom:1.5rem">Imagen 4 · Veo 3 · Все сцены за один запуск</div>', unsafe_allow_html=True)

    from utils.batch import estimate_batch_cost

    # ── Настройки пакета ──
    bp1, bp2, bp3, bp4 = st.columns(4)
    with bp1:
        batch_mode = st.radio("Что генерировать", ["🖼️ Только фото", "🎥 Только видео", "🖼️+🎥 Всё"], horizontal=False)
    with bp2:
        batch_aspect = st.radio("Формат фото", ["16:9","9:16","1:1","4:3"])
    with bp3:
        batch_dur = st.select_slider("Длительность видео", [5, 8], value=5)
        batch_res = st.radio("Разрешение", ["720p","1080p"])
    with bp4:
        batch_source = st.radio("Источник промтов", ["Последняя генерация", "Ввести вручную"])

    st.divider()

    # ── Промты ──
    batch_prompts = []

    if batch_source == "Последняя генерация":
        rdir = "generated_output"
        files = sorted([f for f in os.listdir(rdir) if f.startswith("result_") and f.endswith(".json")], reverse=True) if os.path.exists(rdir) else []
        if files:
            with open(os.path.join(rdir, files[0]), encoding="utf-8") as f:
                last = json.load(f)
            key = "video_prompts" if "Видео" in batch_mode else "photo_prompts"
            raw = last.get(key, last.get("photo_prompts", []))
            batch_prompts = [{"scene_number": p["scene_number"], "prompt": p["prompt"]} for p in raw]
            st.markdown(f'<div style="color:#C8FF00;font-size:0.8rem;margin-bottom:0.5rem">✓ Загружено {len(batch_prompts)} промтов из: {files[0]}</div>', unsafe_allow_html=True)
            for p in batch_prompts:
                st.markdown(f'<div style="background:#141414;border:1px solid #222;border-radius:8px;padding:0.5rem 0.8rem;margin:3px 0;font-size:0.78rem;color:#888"><b style="color:#C8FF00">#{p["scene_number"]}</b> {p["prompt"][:120]}...</div>', unsafe_allow_html=True)
        else:
            st.warning("Нет сохранённых генераций. Сначала запусти Генератор.")
    else:
        st.markdown('<div style="color:#888;font-size:0.8rem;margin-bottom:0.4rem">Введи промты (каждый с новой строки, нумерация автоматическая)</div>', unsafe_allow_html=True)
        manual_text = st.text_area("", height=200, label_visibility="collapsed",
                                   placeholder="3D Pixar style, hero stands on mountain top, cinematic\n3D Pixar style, city lights at night, aerial view\n...")
        if manual_text.strip():
            batch_prompts = [{"scene_number": i+1, "prompt": p.strip()}
                             for i, p in enumerate(manual_text.strip().split("\n")) if p.strip()]

    # ── Стоимость ──
    if batch_prompts:
        n = len(batch_prompts)
        do_img = "фото" in batch_mode or "Всё" in batch_mode
        do_vid = "видео" in batch_mode or "Всё" in batch_mode
        cost = estimate_batch_cost(n if do_img else 0, batch_dur, batch_res)
        vid_cost = estimate_batch_cost(n if do_vid else 0, batch_dur, batch_res)

        cm1, cm2, cm3, cm4 = st.columns(4)
        cm1.markdown(f'<div class="hg-metric"><div class="hg-metric-val">{n}</div><div class="hg-metric-lbl">Сцен</div></div>', unsafe_allow_html=True)
        if do_img:
            cm2.markdown(f'<div class="hg-metric"><div class="hg-metric-val" style="color:#4a9">${n*0.04:.2f}</div><div class="hg-metric-lbl">Imagen (фото)</div></div>', unsafe_allow_html=True)
        if do_vid:
            cm3.markdown(f'<div class="hg-metric"><div class="hg-metric-val" style="color:#f80">${n * estimate_batch_cost(1, batch_dur, batch_res)["total"]:.2f}</div><div class="hg-metric-lbl">Veo (видео)</div></div>', unsafe_allow_html=True)
        total = (n*0.04 if do_img else 0) + (n * estimate_batch_cost(1, batch_dur, batch_res)["total"] if do_vid else 0)
        cm4.markdown(f'<div class="hg-metric"><div class="hg-metric-val" style="color:#C8FF00">${total:.2f}</div><div class="hg-metric-lbl">Итого</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        start_btn = st.button("⚡  ЗАПУСТИТЬ ПАКЕТ", type="primary", use_container_width=True)

        if start_btn:
            from utils.batch import batch_generate_images, batch_generate_videos

            # Прогресс-таблица
            st.markdown('<div style="color:#C8FF00;font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;margin:1rem 0 0.5rem">Прогресс</div>', unsafe_allow_html=True)
            status_placeholders = {}
            for p in batch_prompts:
                ph = st.empty()
                ph.markdown(f'<div style="background:#141414;border:1px solid #333;border-radius:8px;padding:0.5rem 1rem;margin:3px 0;font-size:0.82rem;color:#555">⏳ Сцена {p["scene_number"]} — ожидание...</div>', unsafe_allow_html=True)
                status_placeholders[p["scene_number"]] = ph

            img_results, vid_results = [], []

            # Генерация фото
            if do_img:
                st.markdown('<div style="color:#888;font-size:0.78rem;margin:0.5rem 0">🖼️ Генерирую изображения...</div>', unsafe_allow_html=True)
                def img_cb(scene_num, status, path):
                    icon = "✅" if status == "ok" else "❌"
                    color = "#C8FF00" if status == "ok" else "#ff4444"
                    status_placeholders[scene_num].markdown(
                        f'<div style="background:#141414;border:1px solid {color}33;border-radius:8px;padding:0.5rem 1rem;margin:3px 0;font-size:0.82rem;color:{color}">{icon} Сцена {scene_num} — фото {"готово" if status == "ok" else "ошибка"}</div>',
                        unsafe_allow_html=True)
                img_results = batch_generate_images(batch_prompts, batch_aspect, img_cb)

            # Генерация видео
            if do_vid:
                st.markdown('<div style="color:#888;font-size:0.78rem;margin:0.5rem 0">🎥 Запускаю Veo (все сцены параллельно)...</div>', unsafe_allow_html=True)
                def vid_cb(scene_num, status, path):
                    icon = "✅" if status == "ok" else ("⏰" if status == "timeout" else "❌")
                    color = "#C8FF00" if status == "ok" else ("#ff8800" if status == "timeout" else "#ff4444")
                    label = {"ok": "видео готово", "timeout": "таймаут", "error": "ошибка"}.get(status, status)
                    status_placeholders[scene_num].markdown(
                        f'<div style="background:#141414;border:1px solid {color}33;border-radius:8px;padding:0.5rem 1rem;margin:3px 0;font-size:0.82rem;color:{color}">{icon} Сцена {scene_num} — {label}</div>',
                        unsafe_allow_html=True)
                vid_results = batch_generate_videos(batch_prompts, batch_dur, batch_res, vid_cb)

            # Результаты
            st.markdown("<br>", unsafe_allow_html=True)
            ok_img = sum(1 for r in img_results if r.get("status") == "ok")
            ok_vid = sum(1 for r in vid_results if r.get("status") == "ok")
            st.markdown(f'<div style="background:#141414;border:1px solid #C8FF00;border-radius:12px;padding:1rem 1.5rem;font-size:0.9rem;color:#fff">✅ Готово: <b style="color:#C8FF00">{ok_img} фото</b> · <b style="color:#C8FF00">{ok_vid} видео</b></div>', unsafe_allow_html=True)

            # Галерея результатов
            if img_results:
                st.markdown('<div class="hg-gallery-title">Сгенерированные фото</div>', unsafe_allow_html=True)
                gcols = st.columns(3)
                for i, r in enumerate([x for x in img_results if x.get("image_path") and os.path.exists(x["image_path"])]):
                    with gcols[i % 3]:
                        st.image(r["image_path"], use_container_width=True)
                        st.caption(f"Сцена {r['scene_number']}")
                        with open(r["image_path"], "rb") as f:
                            st.download_button("📥", f.read(), os.path.basename(r["image_path"]), key=f"bi{i}")

            if vid_results:
                st.markdown('<div class="hg-gallery-title">Сгенерированные видео</div>', unsafe_allow_html=True)
                for r in [x for x in vid_results if x.get("video_path") and os.path.exists(x["video_path"])]:
                    st.video(r["video_path"])
                    with open(r["video_path"], "rb") as f:
                        st.download_button(f"📥 Скачать видео сцена {r['scene_number']}", f.read(),
                                           os.path.basename(r["video_path"]), key=f"bv{r['scene_number']}")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown('<br><div style="text-align:center;color:#333;font-size:0.75rem;border-top:1px solid #1a1a1a;padding-top:1rem">AI Content Studio · Groq + Google Imagen 4 + Veo</div>', unsafe_allow_html=True)
