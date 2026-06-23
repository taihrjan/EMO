"""Пакетная генерация фото и видео для всех сцен."""

import os
import time
import requests
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed


# ─── ПАКЕТНАЯ ГЕНЕРАЦИЯ ФОТО ────────────────────────────────────────────────

def batch_generate_images(prompts: list[dict], aspect_ratio: str = "16:9",
                          progress_cb=None) -> list[dict]:
    """
    Генерирует изображения для всех сцен параллельно.

    Args:
        prompts: [{"scene_number": 1, "prompt": "..."}, ...]
        aspect_ratio: "16:9" | "9:16" | "1:1" | "4:3"
        progress_cb: callback(scene_num, status, path) — вызывается по мере готовности

    Returns:
        [{"scene_number": 1, "prompt": "...", "image_path": "...", "status": "ok"|"error"}, ...]
    """
    from utils.google_image import generate_image

    os.makedirs("generated_output/images", exist_ok=True)
    results = []

    def _gen_one(item):
        n = item["scene_number"]
        p = item["prompt"]
        path = f"generated_output/images/scene_{n:02d}.png"
        try:
            out = generate_image(p, path, aspect_ratio=aspect_ratio)
            status = "ok" if out and os.path.exists(out) else "error"
        except Exception as e:
            print(f"   ⚠️  Сцена {n}: {e}")
            out = None
            status = "error"
        if progress_cb:
            progress_cb(n, status, out)
        return {"scene_number": n, "prompt": p, "image_path": out, "status": status}

    # Параллельно — до 3 потоков (Imagen rate limit)
    with ThreadPoolExecutor(max_workers=3) as ex:
        futures = {ex.submit(_gen_one, item): item for item in prompts}
        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda x: x["scene_number"])
    return results


# ─── ПАКЕТНАЯ ГЕНЕРАЦИЯ ВИДЕО ───────────────────────────────────────────────

def batch_generate_videos(prompts: list[dict], duration_seconds: int = 5,
                          resolution: str = "720p",
                          progress_cb=None) -> list[dict]:
    """
    Запускает все Veo-операции параллельно, потом поллит их одновременно.

    Args:
        prompts: [{"scene_number": 1, "prompt": "..."}, ...]
        duration_seconds: 5 или 8
        resolution: "720p" | "1080p"
        progress_cb: callback(scene_num, status, path)

    Returns:
        [{"scene_number": 1, "prompt": "...", "video_path": "...", "status": "...", "cost": 0.0}, ...]
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return [{"scene_number": p["scene_number"], "prompt": p["prompt"],
                 "video_path": None, "status": "no_api_key", "cost": 0.0} for p in prompts]

    model = os.getenv("VEO_MODEL", "veo-3.0-generate-preview")
    os.makedirs("generated_output/videos", exist_ok=True)

    # Шаг 1: запустить все операции
    operations = []
    for item in prompts:
        n = item["scene_number"]
        op_name = _start_veo_operation(item["prompt"], duration_seconds, resolution, api_key, model)
        save_path = f"generated_output/videos/scene_{n:02d}.mp4"
        operations.append({
            "scene_number": n,
            "prompt": item["prompt"],
            "op_name": op_name,
            "save_path": save_path,
            "status": "pending" if op_name else "launch_error",
            "video_path": None,
            "cost": estimate_video_cost(duration_seconds, resolution),
        })
        print(f"   🚀 Veo запущен для сцены {n}: {op_name or 'ОШИБКА'}")

    # Шаг 2: поллить все операции одновременно
    pending = [op for op in operations if op["status"] == "pending"]
    max_wait = 300
    interval = 10
    elapsed = 0

    while pending and elapsed < max_wait:
        time.sleep(interval)
        elapsed += interval
        still_pending = []

        for op in pending:
            result = _check_veo_operation(op["op_name"], op["save_path"], api_key)
            if result == "done":
                op["status"] = "ok"
                op["video_path"] = op["save_path"]
                print(f"   ✅ Сцена {op['scene_number']} готова")
                if progress_cb:
                    progress_cb(op["scene_number"], "ok", op["save_path"])
            elif result == "error":
                op["status"] = "error"
                print(f"   ⚠️  Сцена {op['scene_number']} — ошибка")
                if progress_cb:
                    progress_cb(op["scene_number"], "error", None)
            else:
                still_pending.append(op)

        pending = still_pending
        if pending:
            print(f"   ⏳ Ждём {len(pending)} видео... ({elapsed}/{max_wait} сек)")

    for op in pending:
        op["status"] = "timeout"
        if progress_cb:
            progress_cb(op["scene_number"], "timeout", None)

    return operations


# ─── HELPERS ────────────────────────────────────────────────────────────────

def _start_veo_operation(prompt: str, duration_seconds: int, resolution: str,
                         api_key: str, model: str) -> Optional[str]:
    """Запускает одну Veo-операцию, возвращает op_name."""
    res_map = {"720p": "RESOLUTION_720P", "1080p": "RESOLUTION_1080P", "480p": "RESOLUTION_480P"}
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateVideo"
    payload = {
        "prompt": {"text": prompt},
        "videoGenerationConfig": {
            "durationSeconds": duration_seconds,
            "resolution": res_map.get(resolution, "RESOLUTION_720P"),
        }
    }
    try:
        resp = requests.post(url, json=payload,
                             headers={"Content-Type": "application/json"},
                             params={"key": api_key}, timeout=30)
        if resp.status_code == 200:
            return resp.json().get("name")
        print(f"   ⚠️  Veo запуск {resp.status_code}: {resp.text[:100]}")
    except Exception as e:
        print(f"   ⚠️  Veo запуск ошибка: {e}")
    return None


def _check_veo_operation(op_name: str, save_path: str, api_key: str) -> str:
    """Проверяет статус операции. Возвращает 'done'|'error'|'pending'."""
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/{op_name}"
        resp = requests.get(url, params={"key": api_key}, timeout=30)
        if resp.status_code != 200:
            return "error"
        data = resp.json()
        if not data.get("done"):
            return "pending"
        # Готово — скачиваем
        videos = data.get("response", {}).get("videos", [])
        if videos:
            video_url = videos[0].get("video", {}).get("uri") or videos[0].get("uri")
            if video_url:
                r = requests.get(video_url, timeout=120, stream=True)
                if r.status_code == 200:
                    os.makedirs(os.path.dirname(save_path) or ".", exist_ok=True)
                    with open(save_path, "wb") as f:
                        for chunk in r.iter_content(8192):
                            f.write(chunk)
                    return "done"
        return "error"
    except Exception as e:
        print(f"   ⚠️  Check op ошибка: {e}")
        return "error"


def estimate_video_cost(duration_seconds: int = 5, resolution: str = "720p") -> float:
    rates = {"480p": 0.12, "720p": 0.2419, "1080p": 0.35}
    return round(duration_seconds * rates.get(resolution, 0.2419), 4)


def estimate_batch_cost(n_scenes: int, duration_seconds: int = 5,
                        resolution: str = "720p") -> dict:
    img_cost = n_scenes * 0.04  # Imagen: $0.04/шт
    video_cost = n_scenes * estimate_video_cost(duration_seconds, resolution)
    return {
        "images": round(img_cost, 2),
        "videos": round(video_cost, 2),
        "total": round(img_cost + video_cost, 2),
        "n_scenes": n_scenes,
        "duration": duration_seconds,
        "resolution": resolution,
    }
