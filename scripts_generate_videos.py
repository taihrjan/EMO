#!/usr/bin/env python3
"""
Генератор видео из фото и аудио
Использует FFmpeg для сборки видео
"""

import os
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv

# Загрузить переменные окружения
load_dotenv()

def create_video_from_image_and_audio(image_path: str, audio_path: str, output_path: str, duration: int = 30):
    """Создаёт видео из фото и аудио используя FFmpeg"""

    # FFmpeg команда
    cmd = [
        'ffmpeg',
        '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-shortest',
        '-y',  # Перезаписать файл
        output_path
    ]

    try:
        # Запустить FFmpeg
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0:
            return True, "Видео создано успешно"
        else:
            return False, f"FFmpeg ошибка: {result.stderr}"

    except FileNotFoundError:
        return False, "FFmpeg не установлен. Установить: sudo apt install ffmpeg"
    except subprocess.TimeoutExpired:
        return False, "Таймаут при создании видео"
    except Exception as e:
        return False, str(e)

def generate_videos_from_images_and_audio(images_dir: str = "generated_output/images",
                                         audio_dir: str = "generated_output/audio",
                                         output_dir: str = "generated_output/videos"):
    """Создаёт видео из всех пар фото и аудио"""

    os.makedirs(output_dir, exist_ok=True)

    # Получить список файлов
    image_files = sorted([f for f in os.listdir(images_dir) if f.endswith(('.png', '.jpg', '.jpeg'))])
    audio_files = sorted([f for f in os.listdir(audio_dir) if f.endswith('.mp3')])

    # Взять минимум фото и аудио
    count = min(len(image_files), len(audio_files))
    count = min(count, int(os.getenv('DAILY_VIDEO_COUNT', 30)))

    print(f"🎬 Создаю {count} видео...")

    results = []
    video_fps = int(os.getenv('VIDEO_FPS', 24))
    video_duration = int(os.getenv('VIDEO_DURATION_SECONDS', 30))

    for idx in range(count):
        try:
            image_file = image_files[idx]
            audio_file = audio_files[idx]

            image_path = os.path.join(images_dir, image_file)
            audio_path = os.path.join(audio_dir, audio_file)

            # Получить имя без расширения
            base_name = os.path.splitext(image_file)[0]
            video_file = f"{base_name}.mp4"
            video_path = os.path.join(output_dir, video_file)

            # Создать видео
            success, message = create_video_from_image_and_audio(
                image_path,
                audio_path,
                video_path,
                duration=video_duration
            )

            if success:
                results.append({
                    'id': idx + 1,
                    'image': image_file,
                    'audio': audio_file,
                    'video': video_file,
                    'status': 'success',
                    'message': message,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"✅ [{idx+1}/{count}] {video_file}")
            else:
                results.append({
                    'id': idx + 1,
                    'image': image_file,
                    'audio': audio_file,
                    'status': 'error',
                    'error': message,
                    'timestamp': datetime.now().isoformat()
                })
                print(f"❌ [{idx+1}/{count}] Ошибка: {message}")

        except Exception as e:
            print(f"❌ [{idx+1}/{count}] Ошибка: {e}")
            results.append({
                'id': idx + 1,
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            })
            continue

    return results

def main():
    """Основная функция"""

    print("=" * 60)
    print("🎬 ГЕНЕРАТОР ВИДЕО (FFmpeg)")
    print("=" * 60)

    # Проверить что фото и аудио существуют
    images_dir = "generated_output/images"
    audio_dir = "generated_output/audio"

    if not os.path.exists(images_dir):
        print("❌ Папка с фото не найдена!")
        print("Сначала запустить: python scripts/generate_images.py")
        return

    if not os.path.exists(audio_dir):
        print("❌ Папка с аудио не найдена!")
        print("Сначала запустить: python scripts/text_to_speech.py")
        return

    # Генерировать видео
    results = generate_videos_from_images_and_audio(images_dir, audio_dir)

    # Сохранить результаты
    output_dir = "generated_output"
    results_file = os.path.join(output_dir, f"videos_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n💾 Результаты сохранены в: {results_file}")

    # Статистика
    successful = sum(1 for r in results if r['status'] == 'success')
    failed = sum(1 for r in results if r['status'] == 'error')

    print(f"\n📊 Статистика:")
    print(f"   - Успешно: {successful}")
    print(f"   - Ошибок: {failed}")
    print(f"   - Видео сохранены в: generated_output/videos/")

if __name__ == "__main__":
    main()
