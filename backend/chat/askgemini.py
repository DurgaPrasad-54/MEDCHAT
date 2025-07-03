import os
import httpx
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise EnvironmentError("GEMINI_API_KEY not found in environment")

BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

async def ask_gemini(prompt: str) -> str:
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
    }
    payload = {
        "prompt": {
            "text": prompt
        },
        "temperature": 0.7,
        "candidateCount": 1
    }

    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        try:
            candidates = data.get("candidates", [])
            if candidates:
                return candidates[0].get("output", "No output found")
            else:
                return "No candidates found in response"
        except Exception:
            return "Failed to parse Gemini API response"
