#!/usr/bin/env python3
"""
Генератор промптов для фото
Использует Groq API для создания интересных описаний фото
"""

import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

# Инициализировать Groq клиент
client = Groq(api_key=os.getenv('GROQ_API_KEY'))

# Категории для разнообразия
CATEGORIES = [
    "пейзаж",
    "портрет",
    "натюрморт",
    "животные",
    "архитектура",
    "природа",
    "город",
    "абстракция",
    "еда",
    "мода",
]

def generate_prompt(category: str) -> str:
    """Генерирует один промпт для фото"""

    system_prompt = f"""Ты профессиональный фотограф и художник.
Создай подробное описание для генерации фото категории: {category}

Требования:
- Описание на русском языке
- 2-3 предложения
- Детальное описание сцены, объектов, освещения, цветов
- Стиль: реалистичный или артистичный
- Формат: просто описание, без кавычек

Примеры:
- "Закат на берегу моря, оранжевое небо, отражение солнца в воде, волны с пеной"
- "Портрет красивой девушки с голубыми глазами, длинные волосы, нежный макияж, студийное освещение"
- "Букет тюльпанов в стеклянной вазе, деревянный стол, окно с естественным светом"
"""

    message = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        max_tokens=200,
        messages=[
            {"role": "user", "content": system_prompt}
        ]
    )

    return message.choices[0].message.content.strip()

def generate_batch_prompts(count: int = 160) -> list:
    """Генерирует batch промптов для всех категорий"""

    prompts = []
    prompts_per_category = count // len(CATEGORIES)

    print(f"🎨 Генерирую {count} промптов ({prompts_per_category} на категорию)...")

    for category in CATEGORIES:
        for i in range(prompts_per_category):
            try:
                prompt = generate_prompt(category)
                prompts.append({
                    'id': len(prompts) + 1,
                    'category': category,
                    'prompt': prompt,
                    'timestamp': datetime.now().isoformat(),
                    'status': 'pending'
                })
                print(f"✅ [{category}] Промпт {i+1}/{prompts_per_category}: {prompt[:50]}...")
            except Exception as e:
                print(f"❌ Ошибка при генерации промпта: {e}")
                continue

    return prompts

def save_prompts(prompts: list, output_dir: str = "generated_output"):
    """Сохраняет промпты в JSON"""

    os.makedirs(output_dir, exist_ok=True)

    # Сохранить как JSON
    json_file = os.path.join(output_dir, f"prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(prompts, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Промпты сохранены в: {json_file}")
    print(f"📊 Всего промптов: {len(prompts)}")

    # Также сохранить как текст
    txt_file = os.path.join(output_dir, f"prompts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(txt_file, 'w', encoding='utf-8') as f:
        for p in prompts:
            f.write(f"[{p['category'].upper()}]\n{p['prompt']}\n\n")

    print(f"📝 Текстовый вариант: {txt_file}")

def main():
    """Основная функция"""

    print("=" * 60)
    print("🎨 ГЕНЕРАТОР ПРОМПТОВ ДЛЯ ФОТО")
    print("=" * 60)

    # Получить количество промптов
    count = int(os.getenv('DAILY_PHOTO_COUNT', 160))

    # Генерировать промпты
    prompts = generate_batch_prompts(count)

    # Сохранить результаты
    save_prompts(prompts)

    print("\n✅ Готово! Промпты готовы для генерации фото")
    print(f"📊 Статистика:")
    print(f"   - Всего промптов: {len(prompts)}")
    for cat in CATEGORIES:
        cat_count = sum(1 for p in prompts if p['category'] == cat)
        print(f"   - {cat}: {cat_count}")

if __name__ == "__main__":
    main()
