#!/usr/bin/env python3
"""
Конвертер текста в речь
Используется для добавления голоса в видео
"""

import os
import json
from datetime import datetime
from gtts import gTTS
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

def text_to_speech(text: str, language: str = "ru", slow: bool = False) -> bytes:
    """Конвертирует текст в речь"""

    tts = gTTS(text=text, lang=language, slow=slow)

    # Сохранить во временный файл
    from io import BytesIO
    fp = BytesIO()
    tts.write_to_fp(fp)
    fp.seek(0)

    return fp.read()

def process_prompts_for_audio(prompts_file: str, output_dir: str = "generated_output"):
    """Обрабатывает промпты и создаёт аудиофайлы"""

    # Загрузить промпты
    with open(prompts_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)

    results = []
    audio_output_dir = os.path.join(output_dir, "audio")
    os.makedirs(audio_output_dir, exist_ok=True)

    language = os.getenv('TEXT_TO_SPEECH_LANGUAGE', 'ru')

    print(f"🔊 Генерирую {len(prompts)} аудиофайлов...")

    for idx, prompt_obj in enumerate(prompts, 1):
        try:
            text = prompt_obj['prompt']
            category = prompt_obj.get('category', 'unknown')

            # Конвертировать текст в речь
            audio_data = text_to_speech(text, language=language)

            # Сохранить
            filename = f"{category}_{idx:04d}.mp3"
            filepath = os.path.join(audio_output_dir, filename)

            with open(filepath, 'wb') as f:
                f.write(audio_data)

            results.append({
                'id': idx,
                'category': category,
                'text': text,
                'audio_file': filepath,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            })

            print(f"✅ [{idx}/{len(prompts)}] {category}: {text[:40]}... → {filename}")

        except Exception as e:
            print(f"❌ [{idx}/{len(prompts)}] Ошибка: {e}")
            results.append({
                'id': idx,
                'category': prompt_obj.get('category', 'unknown'),
                'text': prompt_obj['prompt'],
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            continue

    return results

def main():
    """Основная функция"""

    print("=" * 60)
    print("🔊 КОНВЕРТЕР ТЕКСТА В РЕЧЬ")
    print("=" * 60)

    # Найти последний файл промптов
    prompts_dir = "generated_output"
    prompts_files = [f for f in os.listdir(prompts_dir) if f.startswith("prompts_") and f.endswith(".json")]

    if not prompts_files:
        print("❌ Файл с промптами не найден!")
        print("Сначала запустить: python scripts/generate_prompts.py")
        return

    # Использовать последний файл
    latest_prompts = sorted(prompts_files)[-1]
    prompts_file = os.path.join(prompts_dir, latest_prompts)

    print(f"📖 Использую промпты из: {latest_prompts}")

    # Генерировать аудио
    results = process_prompts_for_audio(prompts_file)

    # Сохранить результаты
    results_file = os.path.join(prompts_dir, f"audio_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Результаты сохранены в: {results_file}")

    # Статистика
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'error')

    print(f"\n📊 Статистика:")
    print(f"   - Успешно: {successful}")
    print(f"   - Ошибок: {failed}")
    print(f"   - Аудиофайлы сохранены в: generated_output/audio/")

if __name__ == "__main__":
    main()
