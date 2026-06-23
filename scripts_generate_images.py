#!/usr/bin/env python3
"""
Генератор фото из промптов
Использует fal.ai API для создания изображений
Поддерживает: Stable Diffusion, FLUX и другие модели
"""

import os
import json
import requests
from datetime import datetime
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

# fal.ai API
FAL_API_KEY = os.getenv('FAL_API_KEY')
FAL_API_URL = "https://api.fal.ai/v1/image/generate"

def generate_image_from_prompt(prompt: str, model: str = "flux") -> bytes:
    """Генерирует одно фото из текстового промпта используя fal.ai"""

    headers = {
        "Authorization": f"Key {FAL_API_KEY}",
        "Content-Type": "application/json"
    }

    # fal.ai поддерживает разные модели
    # Варианты: "flux", "flux-pro", "flux-realism", "stable-diffusion-3", и др.

    payload = {
        "prompt": prompt,
        "model_name": model,
        "image_size": {
            "width": int(os.getenv('IMAGE_WIDTH', 512)),
            "height": int(os.getenv('IMAGE_HEIGHT', 512))
        },
        "num_inference_steps": 50,
        "guidance_scale": 7.5,
    }

    try:
        response = requests.post(FAL_API_URL, headers=headers, json=payload, timeout=120)

        if response.status_code == 200:
            data = response.json()
            # fal.ai возвращает URL изображения
            if 'images' in data and len(data['images']) > 0:
                image_url = data['images'][0]['url']
                # Загрузить изображение
                img_response = requests.get(image_url, timeout=30)
                if img_response.status_code == 200:
                    return img_response.content
                else:
                    raise Exception(f"Ошибка загрузки изображения: {img_response.status_code}")
            else:
                raise Exception("Нет изображений в ответе")
        else:
            raise Exception(f"fal.ai API ошибка: {response.status_code} - {response.text}")

    except Exception as e:
        raise Exception(f"Ошибка при генерации: {str(e)}")

def save_image(image_data: bytes, filename: str, output_dir: str = "generated_output/images"):
    """Сохраняет фото в файл"""

    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, filename)
    with open(filepath, 'wb') as f:
        f.write(image_data)

    return filepath

def process_prompts_file(prompts_file: str, output_dir: str = "generated_output", model: str = "flux"):
    """Обрабатывает файл с промптами и генерирует фото"""

    # Загрузить промпты
    with open(prompts_file, 'r', encoding='utf-8') as f:
        prompts = json.load(f)

    results = []
    image_output_dir = os.path.join(output_dir, "images")
    os.makedirs(image_output_dir, exist_ok=True)

    print(f"🖼️  Генерирую {len(prompts)} фото используя fal.ai ({model})...")

    for idx, prompt_obj in enumerate(prompts, 1):
        try:
            prompt = prompt_obj['prompt']
            category = prompt_obj.get('category', 'unknown')

            # Генерировать фото
            image_data = generate_image_from_prompt(prompt, model=model)

            # Сохранить
            filename = f"{category}_{idx:04d}.png"
            filepath = save_image(image_data, filename, image_output_dir)

            results.append({
                'id': idx,
                'category': category,
                'prompt': prompt,
                'image_file': filepath,
                'model': model,
                'status': 'success',
                'timestamp': datetime.now().isoformat()
            })

            print(f"✅ [{idx}/{len(prompts)}] {category}: {prompt[:40]}... → {filename}")

        except Exception as e:
            print(f"❌ [{idx}/{len(prompts)}] Ошибка: {e}")
            results.append({
                'id': idx,
                'category': prompt_obj.get('category', 'unknown'),
                'prompt': prompt_obj['prompt'],
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            continue

    return results

def main():
    """Основная функция"""

    print("=" * 60)
    print("🖼️  ГЕНЕРАТОР ФОТО (fal.ai)")
    print("=" * 60)

    # Проверить API ключ
    if not FAL_API_KEY:
        print("❌ Ошибка: FAL_API_KEY не найден в .env файле!")
        print("1. Зайти на: https://fal.ai")
        print("2. Получить API ключ")
        print("3. Добавить в .env: FAL_API_KEY=ваш_ключ")
        return

    # Найти последний файл промптов
    prompts_dir = "generated_output"
    os.makedirs(prompts_dir, exist_ok=True)

    prompts_files = [f for f in os.listdir(prompts_dir) if f.startswith("prompts_") and f.endswith(".json")]

    if not prompts_files:
        print("❌ Файл с промптами не найден!")
        print("Сначала запустить: python scripts_generate_prompts.py")
        return

    # Использовать последний файл
    latest_prompts = sorted(prompts_files)[-1]
    prompts_file = os.path.join(prompts_dir, latest_prompts)

    print(f"📖 Использую промпты из: {latest_prompts}")

    # Выбор модели (по умолчанию flux)
    model = os.getenv('FAL_MODEL', 'flux')
    print(f"🎨 Модель: {model}")

    # Генерировать фото
    results = process_prompts_file(prompts_file, model=model)

    # Сохранить результаты
    results_file = os.path.join(prompts_dir, f"images_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Результаты сохранены в: {results_file}")

    # Статистика
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'error')

    print(f"\n📊 Статистика:")
    print(f"   - Успешно: {successful}")
    print(f"   - Ошибок: {failed}")
    print(f"   - Фото сохранены в: generated_output/images/")

if __name__ == "__main__":
    main()
