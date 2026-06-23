"""Универсальный интерфейс для работы с LLM (Groq, Gemini, OpenAI)."""

import os
from typing import Optional
import json

def call_llm(prompt: str, system_prompt: str = "", provider: Optional[str] = None, json_mode: bool = False) -> str:
    """
    Универсальный вызов LLM.

    Args:
        prompt: Основной запрос
        system_prompt: Системный промпт
        provider: Провайдер ("groq", "gemini", "openai"). По умолчанию из .env
        json_mode: Ожидать JSON в ответе

    Returns:
        Текст ответа от LLM
    """
    provider = provider or os.getenv("LLM_PROVIDER", "groq").lower()

    # Порядок попыток: основной → запасной
    order = []
    if provider == "groq":
        order = ["groq", "gemini"]
    elif provider == "gemini":
        order = ["gemini", "groq"]
    else:
        order = [provider]

    last_err = None
    for p in order:
        try:
            if p == "groq" and os.getenv("GROQ_API_KEY"):
                print(f"   🤖 Groq...")
                return _call_groq(prompt, system_prompt, json_mode)
            elif p == "gemini" and os.getenv("GEMINI_API_KEY"):
                print(f"   🤖 Gemini...")
                return _call_gemini(prompt, system_prompt, json_mode)
        except Exception as e:
            print(f"   ⚠️  {p} ошибка: {str(e)[:120]}")
            last_err = e
            continue

    raise RuntimeError(f"Все LLM недоступны. Последняя ошибка: {last_err}\n\nПроверь .env:\nGROQ_API_KEY=gsk_...\nGEMINI_API_KEY=AIzaSy...")


def _call_groq(prompt: str, system_prompt: str = "", json_mode: bool = False) -> str:
    """Вызов Groq API через requests."""
    import requests

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY не найден в .env")

    model = os.getenv("GROQ_MODEL", "llama3-70b-8192")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        json={"model": model, "messages": messages, "max_tokens": 4096, "temperature": 0.7},
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _call_gemini(prompt: str, system_prompt: str = "", json_mode: bool = False) -> str:
    """Вызов Google Gemini API через requests (без SDK)."""
    import requests

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY не найден в .env")

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent"

    parts = []
    if system_prompt:
        parts.append({"text": system_prompt + "\n\n"})
    parts.append({"text": prompt})

    payload = {"contents": [{"parts": parts}]}
    resp = requests.post(url, json=payload, params={"key": api_key}, timeout=30)
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]


def _call_openai(prompt: str, system_prompt: str = "", json_mode: bool = False) -> str:
    """Вызов OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("Установите: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY не найден в .env")

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.7,
        max_tokens=4096,
    )

    return response.choices[0].message.content


def parse_json_response(response: str) -> dict:
    """Парсить JSON из ответа LLM."""
    try:
        start = response.find('{')
        end = response.rfind('}') + 1
        if start >= 0 and end > start:
            return json.loads(response[start:end])
    except:
        pass
    return {}
