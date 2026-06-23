"""Генерация изображений через Google Imagen (Gemini API)."""

import os
from typing import Optional
from PIL import Image, ImageDraw
from io import BytesIO


def generate_image(prompt: str, save_path: str, model: Optional[str] = None,
                   aspect_ratio: str = "16:9") -> Optional[str]:
    """
    Генерирует изображение через Google Imagen и сохраняет по пути.

    Args:
        prompt: Текстовый промпт для генерации
        save_path: Путь для сохранения изображения
        model: Модель Imagen (по умолчанию из .env)
        aspect_ratio: "1:1", "4:3", "16:9", "9:16"

    Returns:
        Путь к сохраненному файлу или None при ошибке
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GEMINI_API_KEY не найден, используется placeholder")
        return _create_placeholder_image(save_path, prompt[:50])

    model = model or os.getenv("IMAGEN_MODEL", "imagen-4.0-generate-001")

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        print(f"   📡 Google Imagen ({model})...")

        # Новый API через genai.Client
        client = genai.Client()
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=genai.types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio,
            )
        )

        for generated_image in response.generated_images:
            img = Image.open(BytesIO(generated_image.image.image_bytes))
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
            img.save(save_path)
            print(f"   ✅ Imagen сохранено: {save_path}")
            return save_path

        print("   ⚠️  Imagen: пустой ответ")
        return _create_placeholder_image(save_path, prompt[:50])

    except ImportError:
        print("   ⚠️  Установите: pip install google-generativeai>=0.8.0")
        return _create_placeholder_image(save_path, prompt[:50])

    except Exception as e:
        print(f"   ⚠️  Imagen ошибка: {e}")
        return _create_placeholder_image(save_path, prompt[:50])


def generate_image_fallback(prompt: str, save_path: str) -> Optional[str]:
    """Попытка через requests напрямую (если SDK недоступен)."""
    import requests

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return _create_placeholder_image(save_path, prompt[:50])

    model = os.getenv("IMAGEN_MODEL", "imagen-4.0-generate-001")

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateImages"
        headers = {"Content-Type": "application/json"}
        params = {"key": api_key}
        payload = {
            "prompt": {"text": prompt},
            "numberOfImages": 1,
            "aspectRatio": "ASPECT_RATIO_LANDSCAPE",
        }

        resp = requests.post(url, json=payload, headers=headers, params=params, timeout=120)

        if resp.status_code == 200:
            data = resp.json()
            images = data.get("images", [])
            if images:
                import base64
                img_bytes = base64.b64decode(images[0].get("bytesBase64Encoded", ""))
                img = Image.open(BytesIO(img_bytes))
                os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
                img.save(save_path)
                print(f"   ✅ Imagen (REST) сохранено: {save_path}")
                return save_path

        print(f"   ⚠️  Imagen REST {resp.status_code}: {resp.text[:100]}")
        return _create_placeholder_image(save_path, prompt[:50])

    except Exception as e:
        print(f"   ⚠️  Imagen REST ошибка: {e}")
        return _create_placeholder_image(save_path, prompt[:50])


def _create_placeholder_image(save_path: str, text: str = "") -> str:
    """Создает цветной placeholder с PIL при недоступности API."""
    colors = [(52, 152, 219), (46, 204, 113), (231, 76, 60),
              (155, 89, 182), (241, 196, 15), (26, 188, 156)]
    color = colors[hash(text) % len(colors)]

    img = Image.new('RGB', (1280, 720), color=color)
    draw = ImageDraw.Draw(img)
    draw.text((640, 350), "Google Imagen", fill='white', anchor='mm')
    draw.text((640, 390), text[:50], fill='white', anchor='mm')

    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    img.save(save_path)
    print(f"   🖼️  Placeholder: {save_path}")
    return save_path
