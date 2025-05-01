import requests
import os
from dotenv import load_dotenv
import json
import httpx

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError("API-ключ для OpenRouter не найден. Проверьте переменные окружения.")

url = "https://openrouter.ai/api/v1/chat/completions"

async def ask_openrouter(message:str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://t.me/@botik_11111Bot",
        "X-Title": "telegram_ai_bot"
    }

    data = {
        "model": "google/gemini-2.5-flash-preview",
        "messages": [
            {
                "role": "user",
                "content": message  # Просто передаем текст, без дополнительных вложенных объектов
            }
        ],
        "max_tokens": 2000 
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=data)
    

            # Выводим тело ответа для диагностики
            print(f"Response status code: {response.status_code}")
            print(f"Response body: {response.text}")

            if response.status_code == 200:
                try:
                    response_data = response.json()
                    if "choices" in response_data and len(response_data["choices"]) > 0:
                        return response_data["choices"][0]["message"]["content"]
                    else:
                        return "Ошибка: нет данных в ответе от API."
                except ValueError as e:
                    return f"Ошибка при разборе ответа JSON: {e}"
            else:
                return f"Ошибка: неверный статус ответа от API. Код: {response.status_code}, Сообщение: {response.text}"
        
    except Exception as e:
        print(f"Ошибка при обращении к OpenRouter API: {e}")
        return f"Ошибка при обращении к DeepSeek API: {e}"