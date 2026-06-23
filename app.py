"""AI Content Studio — HuggingFace-style UI."""

import streamlit as st
import os, json, base64
from datetime import datetime
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Content Studio",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
/* ── Base ── */
[data-testid="stAppViewContainer"] { background: #f9f9f9; }
[data-testid="stSidebar"] { background: #ffffff; border-right: 1px solid #e5e7eb; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1200px; }

/* ── Header ── */
.hf-header {
    display: flex; align-items: center; gap: 12px;
    padding: 1rem 0 0.5rem;
    border-bottom: 2px solid #FFD21E;
    margin-bottom: 1.5rem;
}
.hf-title { font-size: 1.6rem; font-weight: 700; color: #1f2937; margin: 0; }
.hf-badge {
    background: #FFD21E; color: #1f2937;
    font-size: 0.7rem; font-weight: 700;
    padding: 2px 8px; border-radius: 9999px;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.hf-badge-blue {
    background: #dbeafe; color: #1d4ed8;
    font-size: 0.7rem; font-weight: 600;
    padding: 2px 8px; border-radius: 9999px;
}

/* ── Cards ── */
.hf-card {
    background: #ffffff;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.hf-card-title {
    font-size: 0.8rem; font-weight: 600;
    color: #6b7280; text-transform: uppercase;
    letter-spacing: 0.08em; margin-bottom: 0.5rem;
}
.hf-prompt {
    font-family: 'SFMono-Regular', Consolas, monospace;
    font-size: 0.82rem; color: #1f2937;
    background: #f3f4f6; border-radius: 8px;
    padding: 0.8rem 1rem; line-height: 1.6;
    white-space: pre-wrap; word-break: break-word;
}

/* ── Metric ── */
.hf-metric {
    background: #ffffff; border: 1px solid #e5e7eb;
    border-radius: 10px; padding: 1rem;
    text-align: center;
}
.hf-metric-val { font-size: 1.8rem; font-weight: 700; color: #1f2937; }
.hf-metric-lbl { font-size: 0.75rem; color: #9ca3af; margin-top: 2px; }

/* ── Buttons ── */
div[data-testid="stButton"] > button {
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
}
div[data-testid="stButton"] > button[kind="primary"] {
    background: #FFD21E !important;
    color: #1f2937 !important;
    border: none !important;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #F5C400 !important;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: #f3f4f6; border-radius: 10px;
    padding: 4px; gap: 4px; border-bottom: none;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px; font-weight: 500;
    color: #6b7280; border: none;
    padding: 6px 16px;
}
.stTabs [aria-selected="true"] {
    background: #ffffff !important;
    color: #1f2937 !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

/* ── Sidebar ── */
.sidebar-section {
    font-size: 0.7rem; font-weight: 700;
    color: #9ca3af; text-transform: uppercase;
    letter-spacing: 0.1em; margin: 1rem 0 0.4rem;
}
.status-dot { width:8px; height:8px; border-radius:50%; display:inline-block; margin-right:6px; }
.dot-green { background: #22c55e; }
.dot-red { background: #ef4444; }

/* ── Image card ── */
.img-wrap { border-radius: 10px; overflow: hidden; border: 1px solid #e5e7eb; }

/* ── Tag ── */
.hf-tag {
    display:inline-block; background:#eff6ff; color:#3b82f6;
    border-radius:6px; padding:2px 8px;
    font-size:0.75rem; font-weight:500; margin:2px;
}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🎬 AI Content Studio")
    st.caption("v3.0 · Google Ecosystem")
    st.divider()

    groq_ok = bool(os.getenv("GROQ_API_KEY"))
    gem_ok  = bool(os.getenv("GEMINI_API_KEY"))

    st.markdown('<p class="sidebar-section">Статус API</p>', unsafe_allow_html=True)
    st.markdown(
        f'<span class="status-dot {"dot-green" if groq_ok else "dot-red"}"></span>Groq LLM<br>'
        f'<span class="status-dot {"dot-green" if gem_ok else "dot-red"}"></span>Google Imagen / Veo',
        unsafe_allow_html=True
    )

    st.markdown('<p class="sidebar-section">Настройки LLM</p>', unsafe_allow_html=True)
    provider = st.selectbox("Провайдер", ["groq","gemini","openai"], label_visibility="collapsed")
    os.environ["LLM_PROVIDER"] = provider

    st.markdown('<p class="sidebar-section">API Ключи</p>', unsafe_allow_html=True)
    gk = st.text_input("Groq API Key", value=os.getenv("GROQ_API_KEY",""), type="password")
    mk = st.text_input("Gemini API Key", value=os.getenv("GEMINI_API_KEY",""), type="password")
    if gk: os.environ["GROQ_API_KEY"] = gk
    if mk: os.environ["GEMINI_API_KEY"] = mk

    st.markdown('<p class="sidebar-section">Imagen</p>', unsafe_allow_html=True)
    img_model = st.selectbox("Модель", [
        "imagen-4.0-generate-001",
        "imagen-4.0-ultra-generate-001",
        "imagen-3.0-generate-001",
    ], label_visibility="collapsed")
    aspect = st.radio("Формат", ["16:9","9:16","1:1","4:3"], horizontal=True)
    os.environ["IMAGEN_MODEL"] = img_model

    st.divider()
    st.markdown('<p class="sidebar-section">Стоимость</p>', unsafe_allow_html=True)
    st.markdown("""
<small>
💬 Groq — **бесплатно**<br>
🖼️ Imagen — **$0.04/шт**<br>
🎥 Veo 720p — **$1.21/5сек**
</small>
""", unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hf-header">
  <span style="font-size:2rem">🎬</span>
  <span class="hf-title">AI Content Studio</span>
  <span class="hf-badge">Google Imagen 4</span>
  <span class="hf-badge-blue">Groq LLM</span>
  <span class="hf-badge-blue">Google Veo</span>
</div>
""", unsafe_allow_html=True)

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🚀  Генератор контента", "🖼️  Генератор изображений", "📋  История"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c_in, c_ref = st.columns([3, 1], gap="large")

    with c_in:
        st.markdown('<div class="hf-card-title">Тема видео</div>', unsafe_allow_html=True)
        topic = st.text_area("", placeholder="Например: 5 секретов богатых людей\nили: психология влияния\nили: как заработать $1000", height=110, label_visibility="collapsed")
        col_btn, col_chk = st.columns([2, 2])
        with col_btn:
            run_btn = st.button("▶  Создать контент", type="primary", use_container_width=True)
        with col_chk:
            gen_media = st.checkbox("🎨 Генерировать изображения сразу", value=False)

    with c_ref:
        st.markdown('<div class="hf-card-title">Фото-референс</div>', unsafe_allow_html=True)
        ref_file = st.file_uploader("", type=["jpg","jpeg","png","webp"], label_visibility="collapsed")
        if ref_file:
            st.image(Image.open(ref_file), use_container_width=True)
            st.caption("✅ Добавится к промтам")

    if run_btn:
        from main import run_pipeline
        ref_note = f", reference style from uploaded image" if ref_file else ""

        with st.spinner("Генерирую контент..."):
            try:
                result = run_pipeline(topic or "", gen_media)
            except Exception as e:
                st.error(f"Ошибка: {e}")
                st.stop()

        # Метрики
        score = result["inspection"].get("total", 0)
        m1, m2, m3, m4 = st.columns(4)
        for col, val, lbl in [
            (m1, score, "Оценка /100"),
            (m2, len(result["scenes"]), "Сцен"),
            (m3, "✅" if result["inspection"].get("passed") else "⚠️", "Инспекция"),
            (m4, len(result["photo_prompts"]), "Промтов"),
        ]:
            col.markdown(f'<div class="hf-metric"><div class="hf-metric-val">{val}</div><div class="hf-metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        r1, r2, r3, r4, r5 = st.tabs(["📝 Сценарий", "🎬 Сторибоард", "🖼️ Фото-промты", "🎥 Видео-промты", "📦 Паковка"])

        with r1:
            script_text = result["script"].get("full_script","")
            st.text_area("", script_text, height=280, label_visibility="collapsed")
            st.download_button("📥 Скачать сценарий", script_text, "script.txt", use_container_width=True)

        with r2:
            for s in result["scenes"]:
                with st.expander(f"Сцена {s['scene_number']}  ·  {s.get('duration_seconds','?')} сек  ·  {s.get('mood','')}"):
                    st.markdown(f"**Текст:** {s.get('narration','')}")
                    st.markdown(f"**Визуал:** {s.get('visual_description','')}")

        with r3:
            for item in result["photo_prompts"]:
                prompt = item["prompt"] + ref_note
                st.markdown(f'<div class="hf-card-title">Сцена {item["scene_number"]}</div>', unsafe_allow_html=True)
                st.code(prompt, language=None)
                ca, cb = st.columns(2)
                with ca:
                    if st.button(f"🎨 Генерировать изображение", key=f"genp_{item['scene_number']}"):
                        with st.spinner("Google Imagen..."):
                            from utils.google_image import generate_image
                            os.makedirs("generated_output/images", exist_ok=True)
                            out = f"generated_output/images/scene_{item['scene_number']:02d}.png"
                            p = generate_image(prompt, out, aspect_ratio=aspect)
                        if p and os.path.exists(p):
                            st.image(p, use_container_width=True)
                            with open(p,"rb") as f:
                                st.download_button("📥 Скачать", f.read(), os.path.basename(p), key=f"dls_{item['scene_number']}")

        with r4:
            for item in result["video_prompts"]:
                st.markdown(f'<div class="hf-card-title">Сцена {item["scene_number"]}</div>', unsafe_allow_html=True)
                st.code(item["prompt"], language=None)

        with r5:
            pkg = result["packaging"]
            st.markdown("#### 🎯 Заголовки")
            for i, t in enumerate(pkg.get("titles",[]), 1):
                c1, c2 = st.columns([5,1])
                with c1: st.markdown(f"**{i}.** {t}")
                with c2: st.code(t, language=None)

            st.markdown("#### 🏷️ Превью тексты")
            for t in pkg.get("thumbnail_texts",[]): st.info(t)

            st.markdown("#### #️⃣ Хэштеги")
            tags = " ".join(pkg.get("hashtags",[]))
            st.code(tags)

            st.divider()
            c1, c2 = st.columns(2)
            c1.download_button("📥 JSON", json.dumps(result, ensure_ascii=False, indent=2),
                               f"result_{datetime.now():%Y%m%d_%H%M%S}.json", "application/json", use_container_width=True)
            report = f"AI CONTENT STUDIO\n{'='*50}\n{result['idea'].get('idea','')}\n\n{result['script'].get('full_script','')}\n\nОценка: {result['inspection'].get('total')}/100\n\n{chr(10).join(pkg.get('titles',[]))}\n\n{tags}"
            c2.download_button("📥 Текст", report, f"report_{datetime.now():%Y%m%d_%H%M%S}.txt", use_container_width=True)

        if gen_media:
            imgs = sorted([f for f in os.listdir("generated_output/images") if f.endswith((".png",".jpg"))]) if os.path.exists("generated_output/images") else []
            if imgs:
                st.markdown("---\n#### 🖼️ Сгенерированные изображения")
                cols = st.columns(3)
                for i, name in enumerate(imgs):
                    p = os.path.join("generated_output/images", name)
                    with cols[i%3]:
                        st.image(p, use_container_width=True)
                        with open(p,"rb") as f:
                            st.download_button("📥", f.read(), name, key=f"gi_{i}")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("#### Прямая генерация через Google Imagen 4")

    ci1, ci2 = st.columns([3, 2], gap="large")

    with ci1:
        ref2 = st.file_uploader("📎 Референсное фото (опционально)", type=["jpg","jpeg","png","webp"], key="ref2")
        if ref2:
            st.image(Image.open(ref2), use_container_width=True)

        ip = st.text_area("✏️ Промт", placeholder="3D Pixar style, cinematic...", height=100)

        st.caption("Быстрые стили:")
        sc = st.columns(4)
        STYLES = {
            "🎭 Pixar":    "3D Pixar animation style, vibrant colors, cinematic lighting, 8k",
            "📸 Фото":     "photorealistic, professional photography, 8k, sharp focus",
            "🎨 Аниме":    "anime style, detailed illustration, vibrant, Studio Ghibli",
            "🎬 Cinematic":"cinematic film still, dramatic lighting, anamorphic lens, 4k",
        }
        for i,(lbl,sty) in enumerate(STYLES.items()):
            with sc[i]:
                if st.button(lbl, use_container_width=True, key=f"sty{i}"):
                    st.session_state["sty"] = sty
        sty = st.session_state.get("sty","")
        full_p = f"{ip}, {sty}".strip(", ") if sty else ip
        if sty: st.caption(f"+ {sty}")

        n_img = st.slider("Количество", 1, 4, 1)
        go = st.button("🎨 Генерировать", type="primary", use_container_width=True)

    with ci2:
        if go and full_p:
            from utils.google_image import generate_image
            os.makedirs("generated_output/images", exist_ok=True)
            prog = st.progress(0)
            for i in range(n_img):
                with st.spinner(f"{i+1}/{n_img}..."):
                    ts = datetime.now().strftime("%H%M%S%f")[:10]
                    out = f"generated_output/images/img_{ts}_{i}.png"
                    p = generate_image(full_p, out, aspect_ratio=aspect)
                prog.progress((i+1)/n_img)
                if p and os.path.exists(p):
                    st.image(p, use_container_width=True)
                    with open(p,"rb") as f:
                        st.download_button("📥 Скачать", f.read(), os.path.basename(p), key=f"mi_{i}")
            prog.empty()
        elif go:
            st.warning("Введите промт")
        else:
            st.markdown('<div style="text-align:center;padding:3rem;color:#9ca3af;border:2px dashed #e5e7eb;border-radius:12px">Изображение появится здесь</div>', unsafe_allow_html=True)

    # Галерея
    st.markdown("---\n#### 🗂️ Галерея")
    imgs_dir = "generated_output/images"
    all_imgs = sorted([f for f in os.listdir(imgs_dir) if f.endswith((".png",".jpg"))], reverse=True) if os.path.exists(imgs_dir) else []
    if all_imgs:
        gcols = st.columns(5)
        for i, name in enumerate(all_imgs[:20]):
            p = os.path.join(imgs_dir, name)
            with gcols[i%5]:
                st.image(p, use_container_width=True)
                with open(p,"rb") as f:
                    st.download_button("📥", f.read(), name, key=f"gal{i}")
    else:
        st.info("Галерея пуста — сгенерируйте первое изображение.")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("#### История генераций")
    rdir = "generated_output"
    os.makedirs(rdir, exist_ok=True)
    files = sorted([f for f in os.listdir(rdir) if f.startswith("result_") and f.endswith(".json")], reverse=True)
    if files:
        sel = st.selectbox("Выберите", files, format_func=lambda x: x.replace("result_","").replace(".json",""))
        with open(os.path.join(rdir, sel), encoding="utf-8") as f:
            h = json.load(f)
        hm1, hm2, hm3 = st.columns(3)
        hm1.metric("Оценка", f"{h['inspection'].get('total','?')}/100")
        hm2.metric("Сцен", len(h.get("scenes",[])))
        hm3.metric("Дата", h.get("timestamp","")[:8])
        st.info(h["idea"].get("idea",""))
        with st.expander("Сценарий"): st.text(h["script"].get("full_script",""))
        with st.expander("Промты"):
            for p in h.get("photo_prompts",[]):
                st.code(p["prompt"], language=None)
        with st.expander("Хэштеги"):
            st.code(" ".join(h.get("packaging",{}).get("hashtags",[])))
        st.download_button("📥 Скачать JSON", json.dumps(h, ensure_ascii=False, indent=2), sel, "application/json")
    else:
        st.info("История пуста.")

# ─── FOOTER ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown('<p style="text-align:center;color:#9ca3af;font-size:0.8rem">AI Content Studio · Groq + Google Imagen 4 + Veo · 2026</p>', unsafe_allow_html=True)
