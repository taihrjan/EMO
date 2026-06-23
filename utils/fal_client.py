"""Интеграция с fal.ai для генерации изображений и видео."""

import os
import requests
from typing import Optional
from PIL import Image, ImageDraw
import io


def generate_image(prompt: str, save_path: str, model: Optional[str] = None) -> Optional[str]:
    """
    Генерирует изображение через fal.ai и сохраняет по пути.

    Args:
        prompt: Текстовый промпт для генерации
        save_path: Путь для сохранения изображения
        model: Модель fal.ai (по умолчанию из .env)

    Returns:
        Путь к сохраненному файлу или None при ошибке
    """
    api_key = os.getenv("FAL_API_KEY")
    if not api_key:
        print("⚠️  FAL_API_KEY не найден, используется placeholder")
        return _create_placeholder_image(save_path, prompt[:50])

    model = model or os.getenv("FAL_IMAGE_MODEL", "fal-ai/flux-pro")

    try:
        url = f"https://fal.run/{model}"
        headers = {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": prompt,
            "image_size": "landscape_16_9",
            "num_images": 1,
            "safety_checker": False,
        }

        print(f"   📡 Запрос к fal.ai ({model})...")
        response = requests.post(url, json=payload, headers=headers, timeout=120)

        if response.status_code == 200:
            data = response.json()
            if "images" in data and len(data["images"]) > 0:
                image_url = data["images"][0].get("url")
                if image_url:
                    print(f"   ⬇️  Загрузка изображения...")
                    img_data = requests.get(image_url, timeout=30).content
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(img_data)
                    print(f"   ✅ Сохранено: {save_path}")
                    return save_path
        else:
            print(f"   ⚠️  fal.ai ошибка {response.status_code}: {response.text[:100]}")
            return _create_placeholder_image(save_path, prompt[:50])

    except Exception as e:
        print(f"   ⚠️  Ошибка при генерации: {e}")
        return _create_placeholder_image(save_path, prompt[:50])

    return None


def generate_video(prompt: str, save_path: str, model: Optional[str] = None, duration: int = 5) -> Optional[str]:
    """
    Генерирует видео через fal.ai.

    Args:
        prompt: Текстовый промпт для генерации видео
        save_path: Путь для сохранения видео
        model: Модель fal.ai (по умолчанию из .env)
        duration: Длительность видео в секундах

    Returns:
        Путь к сохраненному файлу или None при ошибке
    """
    api_key = os.getenv("FAL_API_KEY")
    if not api_key:
        print("⚠️  FAL_API_KEY не найден")
        return None

    model = model or os.getenv("FAL_VIDEO_MODEL", "fal-ai/kling-video-v1")

    try:
        url = f"https://fal.run/{model}"
        headers = {
            "Authorization": f"Key {api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "prompt": prompt,
            "duration": duration,
            "fps": 24,
        }

        print(f"   📡 Запрос видео к fal.ai ({model})...")
        response = requests.post(url, json=payload, headers=headers, timeout=300)

        if response.status_code == 200:
            data = response.json()
            if "video" in data:
                video_url = data["video"].get("url")
                if video_url:
                    print(f"   ⬇️  Загрузка видео...")
                    video_data = requests.get(video_url, timeout=60).content
                    os.makedirs(os.path.dirname(save_path), exist_ok=True)
                    with open(save_path, "wb") as f:
                        f.write(video_data)
                    print(f"   ✅ Видео сохранено: {save_path}")
                    return save_path
        else:
            print(f"   ⚠️  Ошибка видео {response.status_code}")

    except Exception as e:
        print(f"   ⚠️  Ошибка при генерации видео: {e}")

    return None


def _create_placeholder_image(save_path: str, text: str = "") -> str:
    """Создает placeholder изображение с PIL."""
    try:
        colors = [(52, 152, 219), (46, 204, 113), (231, 76, 60),
                  (155, 89, 182), (241, 196, 15), (26, 188, 156)]
        color = colors[hash(text) % len(colors)]

        img = Image.new('RGB', (1280, 720), color=color)
        draw = ImageDraw.Draw(img)

        draw.text((640, 360), text[:40], fill='white', anchor='mm')

        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        img.save(save_path)
        print(f"   🖼️  Placeholder: {save_path}")
        return save_path
    except Exception as e:
        print(f"   ⚠️  Placeholder ошибка: {e}")
        return None
