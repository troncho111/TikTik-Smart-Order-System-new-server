"""
Flight OCR using Google Gemini REST API
Extracts flight details from screenshots/images
משתמש ב-REST API כמו passport_ocr לסטביליות
"""

try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env", override=True)
except ImportError:
    pass

import os
import json
import base64
import time
import requests


def _is_gemini_key_configured() -> bool:
    """Check if Gemini API key is configured (מקור יחיד: .env)"""
    return bool(os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY", "").strip())


def _detect_mime_type(image_bytes: bytes) -> str:
    """Detect image mime type from bytes"""
    if image_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "image/png"
    if image_bytes[:2] == b'\xff\xd8':
        return "image/jpeg"
    if image_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return "image/gif"
    if image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':
        return "image/webp"
    return "image/jpeg"


def extract_flight_data(image_bytes: bytes, max_retries: int = 3) -> dict:
    """
    Extract flight information from a screenshot/image using Gemini Vision.
    
    Args:
        image_bytes: The flight screenshot as bytes
        max_retries: Number of retry attempts for network errors
        
    Returns:
        Dictionary with extracted flights array:
        - flights: array of flight objects with from, to, date, time, flight_no
    """
    if not _is_gemini_key_configured():
        return {
            "flights": [],
            "success": False,
            "error": "נדרש מפתח API של Gemini (AI_INTEGRATIONS_GEMINI_API_KEY)"
        }

    prompt = """Analyze this flight booking/search screenshot and extract ALL flight information.
Return ONLY a valid JSON object with this structure (no markdown, no explanation):
{
    "flights": [
        {
            "direction": "outbound" or "return",
            "from": "3-letter airport code (e.g. TLV)",
            "to": "3-letter airport code (e.g. MAD)",
            "date": "date in DD/MM format",
            "time": "departure time in HH:MM format",
            "arrival_time": "arrival time in HH:MM format if visible",
            "flight_no": "flight number (e.g. UX1302) if visible",
            "duration": "flight duration if visible"
        }
    ]
}

Rules:
- Extract ALL flights shown (outbound and return)
- First flight(s) are usually outbound, last flight(s) are return
- Use standard 3-letter IATA codes for airports
- If a date shows only day/month like "18/12", use DD/MM format
- If year is shown, include it as DD/MM/YY
- Leave fields empty string "" if not visible
- Return ONLY the JSON object, nothing else."""

    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    mime_type = _detect_mime_type(image_bytes)

    api_key = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY", "").strip()
    api_keys = [api_key] if api_key else []

    # תמיד קוראים לכתובת הרשמית של Google. gemini-2.0-flash זמין ב-Free tier
    url_template = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"
    last_error = None

    for api_key in api_keys:
        for attempt in range(max_retries):
            try:
                url = url_template.format(key=api_key)

                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": mime_type,
                                    "data": image_b64
                                }
                            }
                        ]
                    }]
                }

                response = requests.post(url, json=payload, timeout=60)

                if response.status_code == 200:
                    result = response.json()
                    candidates = result.get("candidates", [])
                    if not candidates:
                        last_error = "No response from model"
                        continue

                    parts = candidates[0].get("content", {}).get("parts", [])
                    if not parts:
                        last_error = "Empty response"
                        continue

                    result_text = parts[0].get("text", "").strip()

                    if result_text.startswith("```"):
                        lines = result_text.split("\n")
                        result_text = "\n".join(lines[1:-1])
                    if result_text.startswith("json"):
                        result_text = result_text[4:].strip()

                    data = json.loads(result_text)
                    flights = data.get("flights", [])

                    if flights:
                        return {
                            "flights": flights,
                            "success": True,
                            "error": None
                        }
                    last_error = "לא זוהו טיסות בתמונה"
                    continue

                # HTTP error
                err_body = response.text[:300] if response.text else ""
                last_error = f"HTTP {response.status_code}: {err_body}"
                if response.status_code == 429:
                    time.sleep(2 ** attempt)
                continue

            except json.JSONDecodeError as e:
                last_error = f"Could not parse response: {str(e)}"
                continue
            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

    return {
        "flights": [],
        "success": False,
        "error": last_error or "Unknown error"
    }
