"""
Flight OCR using Gemini AI
Extracts flight details from screenshots/images
"""

import os
import json
import time
from google import genai
from google.genai import types

AI_INTEGRATIONS_GEMINI_API_KEY = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY")
AI_INTEGRATIONS_GEMINI_BASE_URL = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")

def get_client():
    """Create a new client instance to avoid stale connections"""
    return genai.Client(
        api_key=AI_INTEGRATIONS_GEMINI_API_KEY,
        http_options={
            'api_version': '',
            'base_url': AI_INTEGRATIONS_GEMINI_BASE_URL   
        }
    )

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

    last_error = None
    for attempt in range(max_retries):
        try:
            client = get_client()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    prompt,
                    types.Part(
                        inline_data=types.Blob(
                            mime_type="image/jpeg",
                            data=image_bytes
                        )
                    )
                ]
            )
            
            result_text = response.text.strip()
            
            if result_text.startswith("```"):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1])
            
            data = json.loads(result_text)
            
            return {
                "flights": data.get("flights", []),
                "success": True,
                "error": None
            }
            
        except json.JSONDecodeError as e:
            return {
                "flights": [],
                "success": False,
                "error": f"Could not parse response: {str(e)}"
            }
        except Exception as e:
            last_error = str(e)
            if "Connection refused" in last_error or "111" in last_error:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            return {
                "flights": [],
                "success": False,
                "error": last_error
            }
    
    return {
        "flights": [],
        "success": False,
        "error": f"Failed after {max_retries} attempts: {last_error}"
    }
