# ⚙️ ПОДРОБНАЯ НАСТРОЙКА СИСТЕМЫ ГЕНЕРАЦИИ ФОТО И ВИДЕО

## 📋 ТРЕБОВАНИЯ

- Python 3.8+
- Git (для GitHub Actions)
- FFmpeg (для видео)
- Интернет (для облачных API)
- 5 минут свободного времени

---

## 🔑 ШАГ 1: ПОЛУЧИТЬ БЕСПЛАТНЫЕ API КЛЮЧИ

### 1.1 Groq API (Генерация промптов)

```
1. Открыть: https://console.groq.com
2. Кликнуть: "Sign Up"
3. Заполнить форму
4. Подтвердить почту
5. Перейти: API Keys
6. Кликнуть: "Create New API Key"
7. Копировать ключ (начинается с "gsk_")
8. Сохранить в .env файл как: GROQ_API_KEY=gsk_...
```

**Лимиты Groq:**
- 10,000 запросов в день (БЕСПЛАТНО)
- Быстрая работа (1-2 секунды на запрос)
- Модель: mixtral-8x7b-32768

### 1.2 Hugging Face (Stable Diffusion)

```
1. Открыть: https://huggingface.co
2. Кликнуть: "Sign Up"
3. Заполнить форму
4. Подтвердить почту
5. Перейти: Settings → Access Tokens
6. Кликнуть: "New token"
7. Выбрать: "Read" (только для чтения)
8. Копировать токен
9. Сохранить в .env файл как: HF_TOKEN=hf_...
```

**Лимиты Hugging Face:**
- 100 фото в день (БЕСПЛАТНО)
- Обработка: 10-30 секунд на фото
- Модель: stabilityai/stable-diffusion-3

### 1.3 Google Sheets (Хранение данных)

```
1. Открыть: https://console.cloud.google.com
2. Кликнуть: "Создать проект"
3. Введённое название: "Photo Video Generator"
4. Открыть проект
5. Включить: Google Sheets API
   (Search → Google Sheets API → Enable)
6. Включить: Google Drive API
   (Search → Google Drive API → Enable)
7. Перейти: Credentials
8. Кликнуть: "Create Credentials" → "Service Account"
9. Заполнить форму:
   - Service account name: "photo-generator"
   - Email будет создан автоматически
10. Кликнуть: "Create and Continue"
11. Пропустить: "Grant this service account access" (можно пропустить)
12. Кликнуть: "Done"
13. В списке найти созданный Service Account
14. Перейти: Keys tab
15. Кликнуть: "Add Key" → "Create new key" → "JSON"
16. Скачается JSON файл
17. Переименовать в: google_sheets_key.json
18. Сохранить в папке проекта
```

**После этого:**
```
1. Открыть JSON файл в текстовом редакторе
2. Копировать поле "client_email"
3. Создать Google Sheet
4. Поделиться с этим email адресом (Editor доступ)
```

---

## 🐍 ШАГ 2: УСТАНОВИТЬ PYTHON ЗАВИСИМОСТИ

### 2.1 Установить Python 3.8+ (если нет)

**Windows:**
```
Скачать: https://www.python.org/downloads/
Установить (не забыть галку "Add Python to PATH")
```

**Linux/Mac:**
```bash
# Проверить версию
python3 --version

# Если нет, установить
sudo apt install python3.9 python3-pip  # Linux
brew install python3  # Mac
```

### 2.2 Установить FFmpeg (для видео)

**Windows:**
```
1. Скачать: https://ffmpeg.org/download.html
2. Распаковать в папку
3. Добавить в PATH (это может быть сложно, лучше скачать готовую версию)
ИЛИ через chocolatey:
choco install ffmpeg
```

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Mac:**
```bash
brew install ffmpeg
```

**Проверить установку:**
```bash
ffmpeg -version
```

### 2.3 Установить Python пакеты

```bash
# Перейти в папку проекта
cd /path/to/project

# Установить из requirements.txt
pip install -r requirements.txt
```

**Что будет установлено:**
- `groq` - для Groq API
- `requests` - для HTTP запросов
- `python-dotenv` - для переменных окружения
- `google-auth-oauthlib` - для Google Sheets
- `google-api-python-client` - для Google Sheets API
- `google-auth-httplib2` - для Google аутентификации
- `gtts` - для Text-to-Speech
- `Pillow` - для работы с изображениями
- `ffmpeg-python` - для работы с видео

---

## 📝 ШАГ 3: СОЗДАТЬ .env ФАЙЛ

### 3.1 Копировать .env.example

```bash
cp .env.example .env
```

### 3.2 Заполнить .env

```env
# Groq API
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Hugging Face
HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Google Sheets
GOOGLE_SHEETS_KEY_PATH=./google_sheets_key.json
GOOGLE_SHEET_ID=xxxxxxxxxxxxxxxxxxxxxxxx

# Настройки генерации
DAILY_PHOTO_COUNT=160
DAILY_VIDEO_COUNT=30
IMAGE_STYLE=realistic
VIDEO_DURATION=30

# Уведомления (опционально)
TELEGRAM_TOKEN=optional
TELEGRAM_CHAT_ID=optional
```

### 3.3 Получить ID Google Sheet

```
1. Открыть Google Sheet
2. В URL найти часть после /spreadsheets/d/
3. Это ID (копировать всё между /d/ и /edit)
4. Вставить в .env как GOOGLE_SHEET_ID
```

**Пример:**
```
URL: https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMKUVn5OuSGR-XjTfqR8/edit

ID: 1BxiMVs0XRA5nFMKUVn5OuSGR-XjTfqR8
```

---

## ✅ ШАГ 4: ПРОВЕРИТЬ НАСТРОЙКУ

### 4.1 Запустить тест

```bash
python scripts/test_setup.py
```

**Должно вывести:**
```
✅ Python версия: 3.9.x
✅ Groq API: подключено
✅ Hugging Face: подключено
✅ Google Sheets: подключено
✅ FFmpeg: установлено
✅ Все зависимости: установлены

Готово к использованию! 🚀
```

### 4.2 Если ошибка

**Ошибка: "ModuleNotFoundError"**
```bash
# Переустановить зависимости
pip install --upgrade -r requirements.txt
```

**Ошибка: "GROQ_API_KEY not found"**
```
- Проверить что .env создан в правильной папке
- Проверить что ключ скопирован правильно
- Перезагрузить терминал
```

**Ошибка: "FFmpeg not found"**
```bash
# Проверить установку
ffmpeg -version

# Если не установлен, установить:
# Windows: choco install ffmpeg
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg
```

---

## 🎬 ШАГ 5: ЗАПУСТИТЬ ПЕРВЫЙ РАЗ

### 5.1 Запустить генерацию промптов

```bash
python scripts/generate_prompts.py
```

**Результат:**
- Папка: `generated_output/prompts/`
- 160+ текстовых файлов с промптами

### 5.2 Запустить генерацию фото

```bash
python scripts/generate_images.py
```

**Результат:**
- Папка: `generated_output/images/`
- 160+ PNG файлов с фото
- Каждое изображение: 512x512 пикселей

### 5.3 Запустить генерацию голоса

```bash
python scripts/text_to_speech.py
```

**Результат:**
- Папка: `generated_output/audio/`
- 160+ MP3 файлов с голосом

### 5.4 Запустить создание видео

```bash
python scripts/generate_videos.py
```

**Результат:**
- Папка: `generated_output/videos/`
- 30+ MP4 видео (каждое 15-30 секунд)

### 5.5 Запустить загрузку в Google Sheets

```bash
python scripts/update_sheets.py
```

**Результат:**
- Google Sheet заполнена результатами
- Столбцы: дата, промпт, статус, оценка

---

## ⚙️ ШАГ 6: НАСТРОИТЬ GITHUB ACTIONS

### 6.1 Запушить код в GitHub

```bash
# Инициализировать git
git init
git add .
git commit -m "Initial: Photo Video Generator System"

# Запушить на GitHub
git remote add origin https://github.com/YOUR_USERNAME/photo-video-generator.git
git push -u origin main
```

### 6.2 Добавить Secrets в GitHub

```
1. Открыть: GitHub repo → Settings → Secrets and variables → Actions
2. Кликнуть: "New repository secret"
3. Добавить 3 секрета:

   Name: GROQ_API_KEY
   Value: gsk_... (скопировать из .env)
   
   Name: HF_TOKEN
   Value: hf_... (скопировать из .env)
   
   Name: GOOGLE_SHEETS_KEY_JSON
   Value: (содержимое google_sheets_key.json - весь JSON как одну строку)
   
   Name: GOOGLE_SHEET_ID
   Value: (ID из Google Sheet)
```

### 6.3 Включить GitHub Actions

```
1. Открыть: GitHub repo → Actions
2. Кликнуть: "I understand..." (если нужно)
3. Проверить что workflow файл есть: .github/workflows/generate.yml
4. Workflow должен запускаться автоматически каждый день в 22:00 UTC
```

---

## 🎯 ПОЛНЫЙ ПРОЦЕСС УСТАНОВКИ (КРАТКАЯ ВЕРСИЯ)

```bash
# 1. Скачать код
git clone https://github.com/username/photo-video-generator.git
cd photo-video-generator

# 2. Получить API ключи (вручную через веб)
# - Groq: https://console.groq.com
# - Hugging Face: https://huggingface.co
# - Google: https://console.cloud.google.com

# 3. Создать .env
cp .env.example .env
# Отредактировать .env и добавить ключи

# 4. Установить зависимости
pip install -r requirements.txt

# 5. Установить FFmpeg
# Windows: choco install ffmpeg
# Linux: sudo apt install ffmpeg
# Mac: brew install ffmpeg

# 6. Тестировать
python scripts/test_setup.py

# 7. Запустить
python scripts/generate_prompts.py
python scripts/generate_images.py
python scripts/text_to_speech.py
python scripts/generate_videos.py
python scripts/update_sheets.py

# 8. Результаты в generated_output/
```

---

## ✅ ЧЕКЛИСТ ГОТОВНОСТИ

- [ ] Python 3.8+ установлен
- [ ] FFmpeg установлен
- [ ] Groq API ключ получен
- [ ] Hugging Face токен получен
- [ ] Google Service Account создан
- [ ] google_sheets_key.json скачан
- [ ] Google Sheet создан и поделен
- [ ] .env файл заполнен
- [ ] requirements.txt установлен
- [ ] test_setup.py проходит без ошибок
- [ ] Первая генерация работает
- [ ] GitHub Actions настроен (опционально)

---

## 🚀 ГОТОВО!

После выполнения всех шагов система готова генерировать фото и видео! 

**Следующее:** Прочитать PROMPTS_GUIDE.md чтобы улучшить качество генерации.
