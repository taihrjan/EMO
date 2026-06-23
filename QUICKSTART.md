# ⚡ QUICKSTART - Начните за 5 минут!

## 🚀 Минимальная настройка (3 шага)

### ШАГ 1: Установить зависимости (1 минута)
```bash
pip install -r requirements.txt
```

### ШАГ 2: Получить API ключ Groq (2 минуты)
```
1. Открыть: https://console.groq.com
2. Sign Up → подтвердить почту
3. API Keys → Create New API Key
4. Скопировать ключ (начинается с "gsk_")
```

### ШАГ 3: Заполнить .env (1 минута)
```bash
# Скопировать шаблон
cp .env.example .env

# Открыть .env и добавить ключ Groq:
# GROQ_API_KEY=gsk_YOUR_KEY_HERE
```

## ▶️ Запустить!

### 🌐 Веб-интерфейс (красиво)
```bash
streamlit run app.py
```
Откройте браузер: **http://localhost:8501**

### 💻 Консоль (быстро)
```bash
python main.py --topic "5 фактов о природе"
```

### 🎬 С генерацией медиа (реальные фото/видео)
```bash
# Сначала получите fal.ai ключ: https://fal.ai
# Добавьте в .env: FAL_API_KEY=...

python main.py --topic "как заработать на YouTube" --generate-media
```

---

## 📊 Что вы получите?

**Полный пакет контента за 10-30 секунд:**

```
✅ Вирусную идею для видео
✅ Структурированный сценарий (Writer-First)
✅ Оценку сценария (0-100 баллов)
✅ Разбивку на 5 визуальных сцен
✅ 5 фото-промтов (3D Pixar стиль)
✅ 5 видео-промтов (с движением камеры)
✅ 3-5 заголовков для соцсетей
✅ Тексты для превью
✅ 5 оптимальных хэштегов
```

**Результаты сохраняются в:** `generated_output/result_*.json`

---

## 🎯 Примеры команд

```bash
# Генерация по теме
python main.py --topic "как заработать на интернете"

# Генерация с фото/видео
python main.py --topic "5 способов похудеть" --generate-media

# Случайная тема (demo)
python main.py

# Веб-интерфейс
streamlit run app.py
```

---

## 🤯 Как это работает? (7 стадий)

```
1️⃣  ИДЕЯ      Система придумывает вирусную идею
2️⃣  СЦЕНАРИЙ  Пишет сценарий по Writer-First методу
3️⃣  ОЦЕНКА    Проверяет качество (0-100 баллов)
4️⃣  СЦЕНЫ     Разбивает на 5 визуальных сцен
5️⃣  ФОТО      Создаёт промты для AI изображений
6️⃣  ВИДЕО     Добавляет движение камеры
7️⃣  ПАКОВКА   Генерирует заголовки и хэштеги

Каждая стадия занимает 1-5 секунд ⚡
```

---

## 💰 Цена: $0

```
Groq API:       ✅ БЕСПЛАТНО (10k запросов/день)
fal.ai:         ✅ БЕСПЛАТНО (100 изображений/день)
GitHub Actions: ✅ БЕСПЛАТНО (2000 минут/месяц)
ИТОГО:          💰 АБСОЛЮТНО БЕСПЛАТНО!
```

---

## 📁 Ваши файлы

После запуска посмотрите:
- **JSON результаты:** `generated_output/result_*.json`
- **Текстовый отчёт:** `generated_output/report_*.txt`
- **Изображения:** `generated_output/images/`
- **Видео:** `generated_output/videos/`

---

## ⚠️ Если что-то не работает

```bash
# Проверьте что .env заполнен правильно
cat .env

# Переустановите зависимости
pip install -r requirements.txt --upgrade

# Запустите с дебагом
python main.py --topic "test" 2>&1 | head -50
```

---

## 🎁 Бонус: GitHub Actions

Хотите автоматическую генерацию контента каждый день?

1. Создайте `.github/workflows/studio.yml`:
```yaml
name: AI Content Studio
on:
  schedule:
    - cron: '0 22 * * *'
jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: pip install -r requirements.txt
      - env:
          GROQ_API_KEY: ${{ secrets.GROQ_API_KEY }}
        run: python main.py --topic "daily content"
      - run: |
          git config user.name "GitHub Actions"
          git add generated_output/
          git commit -m "🎬 Daily content" || true
          git push
```

2. Добавьте secrets в GitHub Settings

**Готово! Каждый день в 22:00 будет генерироваться новый контент! 🤖**

---

## 🚀 Дальше

Прочитайте `README_STUDIO_OS.md` для полного руководства.

---

**Поехали!** 🎬🚀

```bash
streamlit run app.py
```

Вам нужно ~5 минут установки + открыть браузер = готово! ✨
