"""Генерация видео через Google Veo (Vertex AI / Gemini API)."""

import os
import time
import requests
from typing import Optional


def generate_video(prompt: str, save_path: str, duration_seconds: int = 5,
                   resolution: str = "720p") -> Optional[str]:
    """
    Генерирует видео через Google Veo.

    Пробует сначала через Gemini API (AI Studio), потом Vertex AI.

    Args:
        prompt: Текстовый промпт для видео
        save_path: Путь для сохранения .mp4
        duration_seconds: Длительность (5 или 8 секунд)
        resolution: "720p" или "1080p"

    Returns:
        Путь к сохраненному файлу или None при ошибке
    """
    api_key = os.getenv("GEMINI_API_KEY")
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")

    if not api_key and not project_id:
        print("⚠️  GEMINI_API_KEY и GOOGLE_CLOUD_PROJECT не найдены")
        return None

    # Пробуем Gemini API (AI Studio) — проще
    if api_key:
        result = _generate_via_gemini_api(prompt, save_path, duration_seconds, api_key)
        if result:
            return result

    # Fallback на Vertex AI (требует google-cloud-aiplatform)
    if project_id:
        return _generate_via_vertex(prompt, save_path, duration_seconds, project_id)

    return None


def _generate_via_gemini_api(prompt: str, save_path: str, duration_seconds: int,
                              api_key: str) -> Optional[str]:
    """Генерация через Gemini API (veo-3.0-generate-preview)."""
    model = os.getenv("VEO_MODEL", "veo-3.0-generate-preview")

    try:
        # Запуск генерации (асинхронная операция)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateVideo"
        headers = {"Content-Type": "application/json"}
        params = {"key": api_key}
        payload = {
            "prompt": {"text": prompt},
            "videoGenerationConfig": {
                "durationSeconds": duration_seconds,
                "resolution": _map_resolution(resolution_label=os.getenv("VEO_RESOLUTION", "720p")),
            }
        }

        print(f"   📡 Google Veo ({model}) — запуск...")
        resp = requests.post(url, json=payload, headers=headers, params=params, timeout=30)

        if resp.status_code != 200:
            print(f"   ⚠️  Veo ошибка запуска {resp.status_code}: {resp.text[:100]}")
            return None

        # Асинхронный результат — нужно polling
        operation = resp.json()
        op_name = operation.get("name", "")
        if not op_name:
            print("   ⚠️  Veo: не получено имя операции")
            return None

        return _poll_operation(op_name, save_path, api_key)

    except Exception as e:
        print(f"   ⚠️  Veo Gemini API ошибка: {e}")
        return None


def _poll_operation(op_name: str, save_path: str, api_key: str,
                    max_wait_sec: int = 300) -> Optional[str]:
    """Ожидание завершения асинхронной операции Veo."""
    poll_url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}"
    params = {"key": api_key}

    print(f"   ⏳ Ожидание генерации видео (до {max_wait_sec} сек)...")

    for attempt in range(max_wait_sec // 10):
        time.sleep(10)
        try:
            resp = requests.get(poll_url, params=params, timeout=30)
            if resp.status_code != 200:
                print(f"   ⚠️  Polling ошибка {resp.status_code}")
                continue

            data = resp.json()

            if data.get("done"):
                # Извлечь URL видео
                response_data = data.get("response", {})
                videos = response_data.get("videos", [])

                if videos:
                    video_url = videos[0].get("video", {}).get("uri") or videos[0].get("uri")
                    if video_url:
                        return _download_video(video_url, save_path)

                print("   ⚠️  Veo: операция завершена, но нет видео")
                return None

            elapsed = (attempt + 1) * 10
            print(f"   ⏳ Генерация... ({elapsed}/{max_wait_sec} сек)")

        except Exception as e:
            print(f"   ⚠️  Polling ошибка: {e}")
            continue

    print(f"   ⚠️  Veo: таймаут {max_wait_sec} сек")
    return None


def _download_video(url: str, save_path: str) -> Optional[str]:
    """Скачивает готовое видео."""
    try:
        resp = requests.get(url, timeout=120, stream=True)
        if resp.status_code == 200:
            os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"   ✅ Veo видео сохранено: {save_path}")
            return save_path
        print(f"   ⚠️  Ошибка скачивания видео: {resp.status_code}")
        return None
    except Exception as e:
        print(f"   ⚠️  Ошибка скачивания: {e}")
        return None


def _generate_via_vertex(prompt: str, save_path: str, duration_seconds: int,
                         project_id: str) -> Optional[str]:
    """Генерация через Vertex AI (google-cloud-aiplatform)."""
    try:
        import google.cloud.aiplatform as aiplatform
    except ImportError:
        print("   ⚠️  Установите: pip install google-cloud-aiplatform")
        return None

    try:
        location = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
        model_id = os.getenv("VEO_MODEL", "veo-3.0-generate-preview")

        aiplatform.init(project=project_id, location=location)

        # Vertex AI Video Generation
        endpoint = f"projects/{project_id}/locations/{location}/publishers/google/models/{model_id}"

        client = aiplatform.gapic.PredictionServiceClient(
            client_options={"api_endpoint": f"{location}-aiplatform.googleapis.com"}
        )

        instances = [{"prompt": prompt, "duration_seconds": duration_seconds}]
        parameters = {"resolution": "720p"}

        response = client.predict(endpoint=endpoint, instances=instances, parameters=parameters)

        predictions = response.predictions
        if predictions:
            import base64
            video_bytes = base64.b64decode(predictions[0].get("bytesBase64Encoded", ""))
            if video_bytes:
                os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
                with open(save_path, 'wb') as f:
                    f.write(video_bytes)
                print(f"   ✅ Veo (Vertex) видео сохранено: {save_path}")
                return save_path

    except Exception as e:
        print(f"   ⚠️  Vertex AI ошибка: {e}")

    return None


def _map_resolution(resolution_label: str) -> str:
    """Конвертация метки разрешения в формат API."""
    mapping = {
        "720p": "RESOLUTION_720P",
        "1080p": "RESOLUTION_1080P",
        "480p": "RESOLUTION_480P",
    }
    return mapping.get(resolution_label, "RESOLUTION_720P")


def estimate_cost(duration_seconds: int = 5, resolution: str = "720p") -> float:
    """Подсчёт стоимости генерации видео Veo (Google)."""
    # Цены Google Veo (720p): $0.2419/сек
    price_per_second = {
        "480p": 0.12,
        "720p": 0.2419,
        "1080p": 0.35,
    }
    rate = price_per_second.get(resolution, 0.2419)
    cost = duration_seconds * rate
    print(f"   💰 Стоимость {duration_seconds} сек {resolution}: ${cost:.4f}")
    return cost
