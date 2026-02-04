"""
Concert OCR using Gemini AI
Extracts concert/event details from screenshots or web page images
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

def extract_concert_data(image_bytes: bytes, max_retries: int = 3) -> dict:
    """
    Extract concert/event information from a screenshot/image using Gemini Vision.
    
    Args:
        image_bytes: The event page screenshot as bytes
        max_retries: Number of retry attempts for network errors
        
    Returns:
        Dictionary with extracted concert data:
        - artist_name: Artist/performer name
        - event_name: Full event/tour name
        - event_date: Date of the event
        - event_time: Start time
        - venue_name: Venue name
        - venue_city: City
        - venue_country: Country
        - categories: List of ticket categories with prices
        - notes: Additional info
    """
    prompt = """Analyze this concert/event page screenshot and extract ALL event information.
Return ONLY a valid JSON object with this structure (no markdown, no explanation):
{
    "artist_name": "Main artist/performer name",
    "event_name": "Full event/tour name (e.g. 'STING 3.0 WORLD TOUR')",
    "event_date": "Date in DD/MM/YYYY format",
    "event_time": "Show start time in HH:MM format",
    "doors_open": "Doors open time if visible",
    "venue_name": "Venue/stadium name",
    "venue_city": "City name",
    "venue_country": "Country name",
    "categories": [
        {
            "name": "Category name (e.g. 'Golden Circle', 'VIP', 'Standing')",
            "price": "Price in euros if visible (number only)",
            "description": "Category description if available"
        }
    ],
    "min_price": "Minimum ticket price if visible",
    "currency": "Currency (EUR, USD, etc.)",
    "notes": "Any additional important info (age restrictions, special notes, etc.)"
}

Rules:
- Extract ALL ticket categories/sections visible
- Convert dates to DD/MM/YYYY format
- Use 24-hour format for times (e.g. 20:30)
- If price shows "from €49", extract 49 as min_price
- Leave fields as empty string "" if not visible
- For categories array, include all visible ticket types
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
                "success": True,
                "error": None,
                "artist_name": data.get("artist_name", ""),
                "event_name": data.get("event_name", ""),
                "event_date": data.get("event_date", ""),
                "event_time": data.get("event_time", ""),
                "doors_open": data.get("doors_open", ""),
                "venue_name": data.get("venue_name", ""),
                "venue_city": data.get("venue_city", ""),
                "venue_country": data.get("venue_country", ""),
                "categories": data.get("categories", []),
                "min_price": data.get("min_price", ""),
                "currency": data.get("currency", "EUR"),
                "notes": data.get("notes", "")
            }
            
        except json.JSONDecodeError as e:
            return {
                "success": False,
                "error": f"Could not parse response: {str(e)}",
                "artist_name": "",
                "event_name": "",
                "event_date": "",
                "event_time": "",
                "doors_open": "",
                "venue_name": "",
                "venue_city": "",
                "venue_country": "",
                "categories": [],
                "min_price": "",
                "currency": "EUR",
                "notes": ""
            }
        except Exception as e:
            last_error = str(e)
            if "Connection refused" in last_error or "111" in last_error:
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                    continue
            return {
                "success": False,
                "error": last_error,
                "artist_name": "",
                "event_name": "",
                "event_date": "",
                "event_time": "",
                "doors_open": "",
                "venue_name": "",
                "venue_city": "",
                "venue_country": "",
                "categories": [],
                "min_price": "",
                "currency": "EUR",
                "notes": ""
            }
    
    return {
        "success": False,
        "error": f"Failed after {max_retries} attempts: {last_error}",
        "artist_name": "",
        "event_name": "",
        "event_date": "",
        "event_time": "",
        "doors_open": "",
        "venue_name": "",
        "venue_city": "",
        "venue_country": "",
        "categories": [],
        "min_price": "",
        "currency": "EUR",
        "notes": ""
    }
