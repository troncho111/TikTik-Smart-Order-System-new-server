"""
Passport OCR using Google Gemini REST API
Extracts passenger details from passport images
"""

try:
    from pathlib import Path
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent / ".env")
except ImportError:
    pass

import os
import json
import base64
import requests


def is_gemini_key_configured() -> bool:
    """Check if Gemini API key is configured (מקור יחיד: .env)"""
    return bool(os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY", "").strip())


def extract_passport_data(image_bytes: bytes, max_retries: int = 2) -> dict:
    """
    Extract passport data from image using Gemini REST API
    Returns: dict with first_name, last_name, passport_number, birth_date, passport_expiry, success, error
    """
    if not is_gemini_key_configured():
        return {
            "first_name": "",
            "last_name": "",
            "passport_number": "",
            "birth_date": "",
            "passport_expiry": "",
            "success": False,
            "error": "נדרש מפתח API של Gemini"
        }
    
    api_key = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY", "").strip()
    api_keys = [api_key] if api_key else []
    
    prompt = """Extract passport information from this image and return ONLY a JSON object (no markdown, no explanation):
{
    "first_name": "given/first name",
    "last_name": "surname/family name",
    "passport_number": "passport number",
    "birth_date": "DD/MM/YYYY",
    "passport_expiry": "DD/MM/YYYY"
}
If you cannot find a field, use empty string. Return ONLY the JSON."""
    
    # Encode image to base64
    image_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    last_error = None
    # תמיד כתובת רשמית של Google. gemini-2.0-flash זמין ב-Free tier
    url_template = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={key}"

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
                                    "mime_type": "image/jpeg",
                                    "data": image_b64
                                }
                            }
                        ]
                    }]
                }
                
                response = requests.post(url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    result = response.json()
                    text = result.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
                    
                    # Remove markdown if present
                    text = text.strip()
                    if text.startswith("```"):
                        lines = text.split("\n")
                        text = "\n".join(lines[1:-1])
                    if text.startswith("json"):
                        text = text[4:].strip()
                    
                    data = json.loads(text)
                    
                    return {
                        "first_name": data.get("first_name", "").strip(),
                        "last_name": data.get("last_name", "").strip(),
                        "passport_number": data.get("passport_number", "").strip(),
                        "birth_date": data.get("birth_date", "").strip(),
                        "passport_expiry": data.get("passport_expiry", "").strip(),
                        "success": True,
                        "error": None
                    }
                else:
                    last_error = f"{response.status_code} {response.text[:200]}"
                    if response.status_code == 429:  # Rate limit
                        break  # Try next key
                    continue
                    
            except json.JSONDecodeError as e:
                last_error = f"Could not parse JSON: {str(e)}"
                continue
            except Exception as e:
                last_error = str(e)
                continue
    
    return {
        "first_name": "",
        "last_name": "",
        "passport_number": "",
        "birth_date": "",
        "passport_expiry": "",
        "success": False,
        "error": last_error or "Unknown error"
    }
