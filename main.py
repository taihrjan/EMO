#!/usr/bin/env python3
"""
AI Content Studio OS v2
Полный пайплайн: Идея → Скрипт → Инспекция → Сторибоард → Промпты → Медиа → Паковка

Текст: Groq (бесплатно, llama3-70b)
Изображения: Google Imagen 4 ($0.04/шт, 1500/мес бесплатно)
Видео: Google Veo ($0.2419/сек, дешевле fal.ai на 20%)
"""

import os
import json
import argparse
from datetime import datetime
from dotenv import load_dotenv

from utils.llm import call_llm, parse_json_response
from utils.google_image import generate_image
from utils.google_video import generate_video, estimate_cost

load_dotenv()

OUTPUT_DIR = "generated_output"
os.makedirs(f"{OUTPUT_DIR}/images", exist_ok=True)
os.makedirs(f"{OUTPUT_DIR}/videos", exist_ok=True)


def generate_idea(topic: str = None) -> dict:
    """STAGE 1: Генерация вирусной идеи для видео"""
    print("\n🎯 STAGE 1: Генерация идеи...")

    if not topic:
        topic = "удивительные факты о природе, технологиях или психологии"

    prompt = f"""Придумай вирусную идею для Shorts/Reels/TikTok на тему: {topic}

Требования:
- HOOK за первые 3 секунды
- Конфликт/интрига
- Неожиданный поворот
- Призыв к действию

Верни JSON:
{{
  "idea": "одна строка - суть",
  "hook": "первые 3 сек",
  "target_audience": "кому интересно",
  "viral_element": "почему вирусное"
}}"""

    try:
        raw = call_llm(prompt, system_prompt="Ты гений создания вирусного контента.")
        idea = parse_json_response(raw)
        if not idea:
            idea = {"idea": raw[:100], "hook": topic, "target_audience": "все", "viral_element": "интересно"}
        print(f"✅ Идея: {idea.get('idea', '')[:60]}...")
        return idea
    except Exception as e:
        print(f"⚠️  Ошибка: {e}, используется demo")
        return {
            "idea": f"5 шокирующих фактов о {topic}",
            "hook": "Вы не поверите, но это правда...",
            "target_audience": "люди 18-35",
            "viral_element": "неожиданные факты"
        }


def write_script(idea: dict) -> dict:
    """STAGE 2: Написание сценария (Writer-First метод)"""
    print("\n✍️  STAGE 2: Написание сценария...")

    prompt = f"""Напиши сценарий для видео (60-90 сек):
Идея: {idea.get('idea', '')}
Крючок: {idea.get('hook', '')}

Структура (Writer-First):
1. HOOK (0-3 сек) - зацепить
2. FALSE UNDERSTANDING (3-15 сек) - ложное понимание
3. REVERSAL (15-30 сек) - поворот
4. SYSTEM REVEAL (30-50 сек) - раскрытие
5. OPEN LOOP (50-60 сек) - запомнится

Верни JSON с полным сценарием:
{{
  "hook": "текст",
  "false_understanding": "текст",
  "reversal": "текст",
  "system_reveal": "текст",
  "open_loop": "текст",
  "full_script": "полный текст"
}}"""

    try:
        raw = call_llm(prompt)
        script = parse_json_response(raw)
        if not script or not script.get('full_script'):
            script = {"full_script": raw, "hook": idea.get('hook', '')}
        print(f"✅ Сценарий написан ({len(script.get('full_script', ''))} символов)")
        return script
    except Exception as e:
        print(f"⚠️  Demo сценарий")
        return {
            "hook": idea.get('hook', ''),
            "full_script": f"{idea.get('hook', '')} {idea.get('idea', '')} Подпишись чтобы узнать больше!",
        }


def inspect_script(script: dict) -> dict:
    """STAGE 3: Инспекция скрипта (оценка 0-100)"""
    print("\n🔍 STAGE 3: Инспекция скрипта...")

    text = script.get('full_script', str(script))[:400]
    prompt = f"""Оцени этот сценарий по 5 критериям (0-20 баллов каждый):

Сценарий: {text}

Критерии:
1. HOOK сила
2. Конфликт
3. Ценность
4. Эмоция
5. CTA

Верни JSON:
{{
  "hook_score": 0-20,
  "conflict_score": 0-20,
  "value_score": 0-20,
  "emotion_score": 0-20,
  "cta_score": 0-20,
  "total": 0-100,
  "passed": true/false
}}"""

    try:
        raw = call_llm(prompt)
        result = parse_json_response(raw)
        if result:
            total = result.get("total", 80)
            result["passed"] = total >= 80
            print(f"✅ Оценка: {total}/100 - {'ПРОШЁЛ ✅' if result['passed'] else 'ДОРАБОТАТЬ ⚠️'}")
            return result
    except:
        pass

    print(f"⚠️  Demo оценка")
    return {"total": 85, "passed": True}


def create_storyboard(script: dict, num_scenes: int = 5) -> list:
    """STAGE 4: Создание сторибоарда (разбор на сцены)"""
    print(f"\n🎬 STAGE 4: Сторибоард ({num_scenes} сцен)...")

    text = script.get('full_script', '')[:400]
    prompt = f"""Разбей сценарий на {num_scenes} визуальных сцен:

Сценарий: {text}

Верни JSON массив сцен:
[
  {{
    "scene_number": 1,
    "duration_seconds": 12,
    "narration": "текст диктора",
    "visual_description": "что показать на экране",
    "mood": "атмосфера"
  }}
]"""

    try:
        raw = call_llm(prompt)
        start = raw.find('[')
        end = raw.rfind(']') + 1
        if start >= 0 and end > start:
            scenes = json.loads(raw[start:end])
            if scenes:
                print(f"✅ Сторибоард: {len(scenes)} сцен")
                return scenes
    except:
        pass

    print(f"⚠️  Demo сторибоард")
    return [
        {
            "scene_number": i+1,
            "duration_seconds": 12,
            "narration": f"Часть {i+1}",
            "visual_description": f"Визуальная сцена {i+1}",
            "mood": "динамичный"
        }
        for i in range(num_scenes)
    ]


def generate_photo_prompts(scenes: list) -> list:
    """STAGE 5: Генерация фото-промтов (3D Pixar стиль)"""
    print("\n🖼️  STAGE 5: Генерация фото-промтов...")
    prompts = []

    for scene in scenes:
        visual = scene.get('visual_description', 'beautiful scene')
        mood = scene.get('mood', 'dynamic')

        prompt_text = f"3D Pixar animation style, {visual}, {mood} mood, vibrant colors, cinematic lighting, 8k quality, professional"

        prompts.append({
            "scene_number": scene["scene_number"],
            "prompt": prompt_text,
            "narration": scene.get("narration", "")
        })

    print(f"✅ Фото-промты: {len(prompts)} созданы")
    return prompts


def generate_video_prompts(photo_prompts: list) -> list:
    """STAGE 6: Добавление движения камеры к фото-промтам"""
    print("\n🎥 STAGE 6: Генерация видео-промтов...")

    camera_motions = [
        "slow zoom in",
        "gentle pan left",
        "slow pan right",
        "subtle camera movement",
        "smooth dolly forward",
        "gentle tilt up"
    ]

    video_prompts = []
    for i, item in enumerate(photo_prompts):
        motion = camera_motions[i % len(camera_motions)]
        video_prompt = f"{item['prompt']}, {motion}, smooth motion, cinematic video"
        video_prompts.append({
            "scene_number": item["scene_number"],
            "prompt": video_prompt,
            "narration": item.get("narration", "")
        })

    print(f"✅ Видео-промты: {len(video_prompts)} созданы")
    return video_prompts


def generate_packaging(idea: dict, script: dict) -> dict:
    """STAGE 7: Генерация заголовков и текстов для соцсетей"""
    print("\n📦 STAGE 7: Создание паковки...")

    prompt = f"""Создай упаковку для вирусного видео.

Идея: {idea.get('idea', '')}

Верни JSON:
{{
  "titles": [
    "Заголовок 1",
    "Заголовок 2",
    "Заголовок 3"
  ],
  "thumbnail_texts": [
    "Текст 1",
    "Текст 2"
  ],
  "hashtags": ["#tag1", "#tag2", "#tag3", "#tag4", "#tag5"]
}}"""

    try:
        raw = call_llm(prompt)
        packaging = parse_json_response(raw)
        if packaging:
            print(f"✅ Паковка: {len(packaging.get('titles', []))} заголовков")
            return packaging
    except:
        pass

    print(f"⚠️  Demo паковка")
    idea_text = idea.get('idea', 'видео')
    return {
        "titles": [
            f"🔥 {idea_text}",
            f"Вы не знали: {idea_text}",
            f"Это изменит всё"
        ],
        "thumbnail_texts": ["ШОКИРУЮЩЕЕ", "СМОТРИ ДО КОНЦА"],
        "hashtags": ["#viral", "#facts", "#shorts", "#trending", "#amazing"]
    }


def run_pipeline(topic: str = "", generate_media: bool = False):
    """Запустить полный пайплайн"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    print("=" * 60)
    print("🎬 AI CONTENT STUDIO OS v2")
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # STAGE 1: Идея
    idea = generate_idea(topic if topic else None)

    # STAGE 2: Сценарий
    script = write_script(idea)

    # STAGE 3: Инспекция
    inspection = inspect_script(script)
    if not inspection.get("passed"):
        print("⚠️  Сценарий требует доработки, продолжаем...")

    # STAGE 4: Сторибоард
    scenes = create_storyboard(script, num_scenes=5)

    # STAGE 5: Фото-промты
    photo_prompts = generate_photo_prompts(scenes)

    # STAGE 6: Видео-промты
    video_prompts = generate_video_prompts(photo_prompts)

    # Опциональная генерация медиа через Google Imagen + Veo
    if generate_media:
        imagen_model = os.getenv("IMAGEN_MODEL", "imagen-4.0-generate-001")
        veo_resolution = os.getenv("VEO_RESOLUTION", "720p")
        video_duration = int(os.getenv("VEO_DURATION_SECONDS", "5"))

        print(f"\n🖼️  Генерация изображений через Google Imagen ({imagen_model})...")
        for prompt_item in photo_prompts:
            scene_num = prompt_item["scene_number"]
            img_path = f"{OUTPUT_DIR}/images/scene_{scene_num:02d}.png"
            generate_image(prompt_item["prompt"], img_path, model=imagen_model)

        print(f"\n🎥 Генерация видео через Google Veo ({veo_resolution})...")
        total_cost = 0.0
        for prompt_item in video_prompts:
            scene_num = prompt_item["scene_number"]
            vid_path = f"{OUTPUT_DIR}/videos/scene_{scene_num:02d}.mp4"
            cost = estimate_cost(video_duration, veo_resolution)
            total_cost += cost
            generate_video(prompt_item["prompt"], vid_path, duration_seconds=video_duration)
        print(f"   💰 Итого за видео: ${total_cost:.4f}")

    # STAGE 7: Паковка
    packaging = generate_packaging(idea, script)

    # Сохранить результаты
    result = {
        "timestamp": timestamp,
        "idea": idea,
        "script": script,
        "inspection": inspection,
        "scenes": scenes,
        "photo_prompts": photo_prompts,
        "video_prompts": video_prompts,
        "packaging": packaging
    }

    # JSON результаты
    result_file = f"{OUTPUT_DIR}/result_{timestamp}.json"
    with open(result_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    # Текстовый отчёт
    report_file = f"{OUTPUT_DIR}/report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("AI CONTENT STUDIO OS - ОТЧЁТ\n")
        f.write(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 60 + "\n\n")

        f.write("💡 ИДЕЯ\n")
        f.write(f"{idea.get('idea', '')}\n\n")

        f.write("📝 СЦЕНАРИЙ\n")
        f.write(f"{script.get('full_script', '')}\n\n")

        f.write(f"🔍 ОЦЕНКА: {inspection.get('total', '?')}/100\n\n")

        f.write("📦 ЗАГОЛОВКИ\n")
        for title in packaging.get('titles', []):
            f.write(f"- {title}\n")

        f.write("\n🏷️ ХЭШТЕГИ\n")
        f.write(" ".join(packaging.get('hashtags', [])) + "\n\n")

        f.write("🎬 СЦЕНЫ И ПРОМТЫ\n")
        for scene in scenes:
            f.write(f"\nСцена {scene['scene_number']}:\n")
            f.write(f"  Визуал: {scene.get('visual_description', '')}\n")
            photo_prompt = next((p for p in photo_prompts if p['scene_number'] == scene['scene_number']), None)
            if photo_prompt:
                f.write(f"  Фото: {photo_prompt['prompt'][:80]}...\n")

    print("\n" + "=" * 60)
    print("✅ ПАЙПЛАЙН ЗАВЕРШЁН!")
    print(f"📁 Результаты в: {OUTPUT_DIR}/")
    print(f"   📄 JSON: {result_file}")
    print(f"   📝 Отчёт: {report_file}")
    if generate_media:
        print(f"   🖼️  Изображения: {OUTPUT_DIR}/images/")
        print(f"   🎥 Видео: {OUTPUT_DIR}/videos/")
    print("\n📦 ЛУЧШИЙ ЗАГОЛОВОК:")
    titles = packaging.get('titles', [])
    if titles:
        print(f"   {titles[0]}")
    print("=" * 60)

    return result


def main():
    parser = argparse.ArgumentParser(description="AI Content Studio OS v2")
    parser.add_argument("--topic", type=str, default="", help="Тема для видео")
    parser.add_argument("--generate-media", action="store_true", help="Генерировать изображения и видео через fal.ai")
    args = parser.parse_args()

    run_pipeline(args.topic, args.generate_media)


if __name__ == "__main__":
    main()
