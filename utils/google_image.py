"""Генерация изображений через Google Imagen 4 (REST API)."""

import os
import base64
import requests
from typing import Optional
from PIL import Image, ImageDraw
from io import BytesIO


def generate_image(prompt: str, save_path: str, model: Optional[str] = None,
                   aspect_ratio: str = "16:9") -> Optional[str]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("⚠️  GEMINI_API_KEY не найден")
        return _create_placeholder_image(save_path, prompt[:50])

    model = model or os.getenv("IMAGEN_MODEL", "imagen-4.0-generate-001")

    # Сначала пробуем новый SDK (google-genai)
    result = _try_sdk(prompt, save_path, model, aspect_ratio, api_key)
    if result:
        return result

    # Fallback: REST API
    result = _try_rest(prompt, save_path, model, aspect_ratio, api_key)
    if result:
        return result

    print("   ⚠️  Все методы не сработали, placeholder")
    return _create_placeholder_image(save_path, prompt[:50])


def _try_sdk(prompt, save_path, model, aspect_ratio, api_key):
    """Новый SDK: pip install google-genai"""
    try:
        from google import genai
        from google.genai import types as gtypes

        client = genai.Client(api_key=api_key)
        response = client.models.generate_images(
            model=model,
            prompt=prompt,
            config=gtypes.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio=aspect_ratio,
            )
        )
        for img_obj in response.generated_images:
            img = Image.open(BytesIO(img_obj.image.image_bytes))
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
            img.save(save_path)
            print(f"   ✅ Imagen SDK сохранено: {save_path}")
            return save_path
    except ImportError:
        pass
    except Exception as e:
        print(f"   ⚠️  SDK ошибка: {e}")
    return None


def _try_rest(prompt, save_path, model, aspect_ratio, api_key):
    """REST API через requests."""
    # Маппинг aspect_ratio в формат API
    ar_map = {
        "1:1":  "ASPECT_RATIO_1_1",
        "4:3":  "ASPECT_RATIO_4_3",
        "16:9": "ASPECT_RATIO_16_9",
        "9:16": "ASPECT_RATIO_9_16",
    }
    ar_val = ar_map.get(aspect_ratio, "ASPECT_RATIO_16_9")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:predict"
    headers = {"Content-Type": "application/json", "x-goog-api-key": api_key}
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": ar_val,
        }
    }

    try:
        print(f"   📡 Imagen REST ({model})...")
        resp = requests.post(url, json=payload, headers=headers, timeout=120)

        if resp.status_code == 200:
            data = resp.json()
            preds = data.get("predictions", [])
            if preds:
                b64 = preds[0].get("bytesBase64Encoded", "")
                if b64:
                    img_bytes = base64.b64decode(b64)
                    img = Image.open(BytesIO(img_bytes))
                    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
                    img.save(save_path)
                    print(f"   ✅ Imagen REST сохранено: {save_path}")
                    return save_path
        print(f"   ⚠️  REST {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"   ⚠️  REST ошибка: {e}")
    return None


def _create_placeholder_image(save_path: str, text: str = "") -> str:
    colors = [(52, 152, 219), (46, 204, 113), (231, 76, 60),
              (155, 89, 182), (241, 196, 15), (26, 188, 156)]
    color = colors[hash(text) % len(colors)]
    img = Image.new('RGB', (1280, 720), color=color)
    draw = ImageDraw.Draw(img)
    draw.text((640, 350), "Google Imagen 4", fill='white', anchor='mm')
    draw.text((640, 390), text[:50], fill='white', anchor='mm')
    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
    img.save(save_path)
    print(f"   🖼️  Placeholder: {save_path}")
    return save_path
