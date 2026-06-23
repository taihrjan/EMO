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

/* скрыть дублирующиеся элементы */
[data-testid="stFileUploaderDropzoneInput"] + div { display: none; }
section[data-testid="stFileUploaderDropzone"] > div > div:nth-child(2) { display: none; }

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

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
    background: #141414;
    border: 2px dashed #2a2a2a;
    border-radius: 12px;
    padding: 1rem;
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
[data-testid="stFileUploader"] { background: #141414 !important; border: 2px dashed #2a2a2a !important; border-radius: 12px !important; }
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
tab1, tab2, tab3 = st.tabs(["🚀  Генератор", "🖼️  Изображения", "📋  История"])

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
        ref_file = st.file_uploader("", type=["jpg","jpeg","png","webp"], label_visibility="collapsed")
        if ref_file:
            st.image(Image.open(ref_file), use_container_width=True)
            st.markdown('<div style="color:#C8FF00;font-size:0.75rem;margin-top:0.3rem">✓ Добавится к промтам</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
<div style="border:2px dashed #2a2a2a;border-radius:12px;padding:2rem;text-align:center;color:#444;font-size:0.8rem">
  📎 Перетащи фото<br>сюда
</div>""", unsafe_allow_html=True)

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

    with ci1:
        ref2 = st.file_uploader("📎 Референсное фото", type=["jpg","jpeg","png","webp"], key="ref2")
        if ref2:
            st.image(Image.open(ref2), use_container_width=True)

        ip = st.text_area("", placeholder="Опиши изображение...\n\n3D Pixar style, cinematic scene of...", height=120, label_visibility="collapsed", key="ip2")

        # Быстрые стили — карточки
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
        go = st.button("🎨  ГЕНЕРИРОВАТЬ", type="primary", use_container_width=True)

    with ci2:
        st.markdown('<div style="color:#555;font-size:0.72rem;font-weight:700;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.8rem">Результат</div>', unsafe_allow_html=True)
        result_area = st.empty()

        if go and full_p:
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
            if generated:
                for i, p in enumerate(generated):
                    st.image(p, use_container_width=True)
                    with open(p,"rb") as f:
                        st.download_button(f"📥 Скачать {i+1}", f.read(), os.path.basename(p), key=f"mi{i}")
        elif go:
            st.warning("Введи промт")
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

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown('<br><div style="text-align:center;color:#333;font-size:0.75rem;border-top:1px solid #1a1a1a;padding-top:1rem">AI Content Studio · Groq + Google Imagen 4 + Veo</div>', unsafe_allow_html=True)
