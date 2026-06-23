# CLAUDE.md — Обучение AI-агента

> Читается автоматически при каждом старте сессии Claude Code.
> Содержит полный контекст для работы БЕЗ лишних вопросов.

---

## 👤 КТО ТАКОЙ ПОЛЬЗОВАТЕЛЬ

**Tahir** — создатель вирусного контента для TikTok / YouTube Shorts / Instagram Reels.

**Что он делает:**
- Генерирует идеи и сценарии для коротких видео (60–90 сек)
- Создаёт изображения через Google Imagen 4 для сторибордов и превью
- Генерирует видео через Google Veo
- Работает на Windows, запускает через Streamlit в браузере
- Хочет всё готовое, без лишних шагов

**Стиль общения:**
- Пишет кратко, caps lock, без знаков препинания
- Если пишет "ЗАВЕДИ", "СДЕЛАЙ", "ВСТАВЛЯЙ" — просто делать, не объяснять
- Не задавать уточняющих вопросов — действовать на основе контекста
- Отвечать коротко и по делу

---

## 🏗️ АРХИТЕКТУРА ПРОЕКТА

```
EMO/
├── CLAUDE.md              # ← ты здесь (инструкции агента)
├── main.py                # 7-стадийный пайплайн
├── app.py                 # Streamlit UI (ГЛАВНОЕ приложение)
├── requirements.txt
├── .env                   # API-ключи
├── utils/
│   ├── llm.py             # Groq / Gemini / OpenAI
│   ├── google_image.py    # Google Imagen 4
│   └── google_video.py    # Google Veo
└── generated_output/
    ├── images/            # PNG сцены
    └── videos/            # MP4 сцены
```

---

## 🔑 API КЛЮЧИ (актуальные)

```env
GROQ_API_KEY=gsk_...        # console.groq.com
GEMINI_API_KEY=AIzaSy...    # aistudio.google.com/apikey
FAL_API_KEY=...             # fal.ai/dashboard/keys
IMAGEN_MODEL=imagen-4.0-generate-001
VEO_MODEL=veo-3.0-generate-preview
VEO_RESOLUTION=720p
VEO_DURATION_SECONDS=5
LLM_PROVIDER=groq
GROQ_MODEL=llama3-70b-8192
```

**ВАЖНО:** Ключи хранятся только в `.env` (в .gitignore). Никогда не коммитить.
Если пользователь даёт новые ключи — сразу обновлять `.env`.

---

## 🚀 КАК ЗАПУСКАТЬ

### На Windows (основной способ)
```powershell
cd C:\Users\tahir\EMO
git pull origin claude/festive-davinci-ibp14q
streamlit run app.py
```
Открывается браузер на `http://localhost:8501`

### В контейнере (только тест, без API)
```bash
python main.py --topic "тема"  # работает в demo-режиме
```
**В контейнере API заблокированы** — groq, gemini, fal.ai недоступны.
Всё реальное — только на Windows пользователя.

---

## 🎬 7-СТАДИЙНЫЙ ПАЙПЛАЙН

```python
from main import run_pipeline

result = run_pipeline(
    topic="5 секретов богатых людей",
    generate_media=True   # True = Imagen + Veo
)
```

| Stage | Функция | Выход |
|-------|---------|-------|
| 1 | `generate_idea()` | idea, hook, viral_element |
| 2 | `write_script()` | full_script (5 актов) |
| 3 | `inspect_script()` | score 0–100, passed |
| 4 | `create_storyboard()` | 5 сцен |
| 5 | `generate_photo_prompts()` | 5 Pixar-промтов |
| 6 | `generate_video_prompts()` | 5 промтов + camera motion |
| 7 | `generate_packaging()` | 3 заголовка, хэштеги |

---

## 🖼️ GOOGLE IMAGEN 4

```python
from utils.google_image import generate_image

path = generate_image(
    prompt="3D Pixar style, cinematic, 8k",
    save_path="generated_output/images/scene_01.png",
    aspect_ratio="16:9"   # 1:1 | 4:3 | 16:9 | 9:16
)
```

**Цена:** $0.04/шт, 1500 бесплатных в месяц
**Fallback:** SDK → REST API → PIL placeholder (цветная заглушка)

---

## 🎥 GOOGLE VEO

```python
from utils.google_video import generate_video, estimate_cost

cost = estimate_cost(5, "720p")  # $1.21
path = generate_video(prompt, save_path, duration_seconds=5, resolution="720p")
```

**Асинхронный** — polling 10 сек, до 300 сек ожидания.

---

## 🧠 МЕТОДОЛОГИЯ КОНТЕНТА

### Writer-First структура сценария
1. **HOOK (0–3 сек)** — захват внимания
2. **FALSE UNDERSTANDING (3–15 сек)** — ложное понимание
3. **REVERSAL (15–30 сек)** — неожиданный поворот
4. **SYSTEM REVEAL (30–50 сек)** — раскрытие сути
5. **OPEN LOOP (50–60 сек)** — остаётся думать

### Стиль промтов (Stage 5)
```
3D Pixar animation style, {visual}, {mood} mood, vibrant colors,
cinematic lighting, 8k quality, professional
```

### Движения камеры (Stage 6, ротация)
```
slow zoom in → gentle pan left → slow pan right →
subtle camera movement → smooth dolly forward → gentle tilt up
```

### Character Lock (сериальный контент)
Описание персонажа **дословно** повторять в каждой сцене — иначе character drift.

---

## 🖥️ STREAMLIT UI (app.py)

Три вкладки:

### Вкладка 1 — Генератор контента
- Поле темы видео
- Загрузка фото-референса (добавляется к промтам)
- Кнопка генерации контента
- Кнопка генерации изображений под каждым промтом
- Копирование промтов, скачивание результатов

### Вкладка 2 — Генератор изображений
- Загрузка референса
- Ввод промта
- Быстрые стили: Pixar, Реализм, Аниме, Cinematic
- Генерация 1–4 изображений
- Галерея всех изображений со скачиванием

### Вкладка 3 — История
- Все предыдущие генерации
- Просмотр промтов и сценариев
- Скачивание JSON

---

## 💻 GIT И ДЕПЛОЙ

| Ветка | Назначение |
|-------|-----------|
| `main` | оригинальный код EMO (не трогать) |
| `claude/festive-davinci-ibp14q` | весь наш код |

**Команды для пуша:**
```bash
# В контейнере (с классическим ghp_ токеном):
git add -A
git commit -m "описание"
git push origin claude/festive-davinci-ibp14q

# На Windows (уже настроен remote с токеном):
git pull origin claude/festive-davinci-ibp14q
git push origin claude/festive-davinci-ibp14q
```

**Контейнер блокирует push через прокси 403.**
Пушить с Windows используя классический ghp_ токен (repo scope).

---

## ⚠️ ИЗВЕСТНЫЕ ПРОБЛЕМЫ

| Проблема | Причина | Решение |
|----------|---------|---------|
| `Host not in allowlist: api.groq.com` | Контейнер блокирует сеть | Запускать на Windows |
| `git push 403` | Прокси контейнера | Пушить с Windows или использовать ghp_ токен через remote set-url |
| `CommandNotFoundException: pip` | Python не установлен | `winget install Python.Python.3.11` |
| `CommandNotFoundException: git` | Git не установлен | `winget install Git.Git` |
| `.env.example не найден` | Файл не скопирован на Windows | `git pull origin claude/festive-davinci-ibp14q` |

---

## 🔄 ТИПИЧНЫЕ ЗАДАЧИ АГЕНТА

### "Запусти / заведи"
→ `streamlit run app.py` (на Windows) или `python main.py` (тест в контейнере)

### "Вставь ключи"
→ Обновить `.env`, не коммитить

### "Сделай интерфейс удобнее"
→ Редактировать `app.py`, коммитить, пушить

### "Добавь новый API"
1. Создать `utils/new_provider.py`
2. Обновить `main.py` (импорт)
3. Обновить `app.py` (UI)
4. Обновить `requirements.txt`
5. Обновить `.env.example`

### "Почему не работает"
→ Проверить `.env`, запустить `python main.py` и смотреть на `⚠️` строки

---

## 🚫 НИКОГДА

- Не коммитить `.env`
- Не пушить в `main`
- Не удалять fallback-логику
- Не задавать лишних вопросов если контекст понятен
- Не объяснять очевидное — просто делать

---

## 📞 КОНТЕКСТ

- **Репозиторий:** `taihrjan/EMO`
- **Ветка:** `claude/festive-davinci-ibp14q`
- **ОС пользователя:** Windows 11, PowerShell
- **Путь проекта:** `C:\Users\tahir\EMO`
- **Email:** superprofitabl@gmail.com
- **Обновлено:** 2026-06-23
