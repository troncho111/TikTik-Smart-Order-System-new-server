"""
Passport OCR using Gemini AI
Extracts passenger details from passport images
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

def extract_passport_data(image_bytes: bytes, max_retries: int = 3) -> dict:
    """
    Extract passport information from an image using Gemini Vision.
    
    Args:
        image_bytes: The passport image as bytes
        max_retries: Number of retry attempts for network errors
        
    Returns:
        Dictionary with extracted fields:
        - first_name: First/given name
        - last_name: Surname/family name
        - passport_number: Passport number
        - birth_date: Date of birth (DD/MM/YYYY)
        - passport_expiry: Passport expiry date (DD/MM/YYYY)
    """
    prompt = """Analyze this passport image carefully and extract ALL the following information.

IMPORTANT: Look for these fields on the passport:
- SURNAME / FAMILY NAME (שם משפחה) - usually at the top
- GIVEN NAMES / FIRST NAME (שם פרטי) - usually below surname
- PASSPORT NUMBER - the document number
- DATE OF BIRTH - birth date
- DATE OF EXPIRY - expiry date

Also check the MRZ (Machine Readable Zone) at the bottom - the two lines of text with << symbols.
The MRZ format is: SURNAME<<FIRSTNAME<<

Return ONLY a valid JSON object with these exact keys (no markdown, no explanation):
{
    "first_name": "the given/first name EXACTLY as written on the passport",
    "last_name": "the surname/family name EXACTLY as written on the passport", 
    "passport_number": "the passport/document number",
    "birth_date": "date of birth in DD/MM/YYYY format",
    "passport_expiry": "passport expiry date in DD/MM/YYYY format"
}

CRITICAL: You MUST extract the first_name and last_name. These are always on the passport.
If any field cannot be found, use an empty string for that field.
Return ONLY the JSON object, nothing else."""

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
            print(f"[Passport OCR] Raw AI response: {result_text}")
            
            if result_text.startswith("```"):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1])
            
            data = json.loads(result_text)
            print(f"[Passport OCR] Parsed data: {data}")
            print(f"[Passport OCR] first_name='{data.get('first_name', '')}', last_name='{data.get('last_name', '')}'")
            
            return {
                "first_name": data.get("first_name", ""),
                "last_name": data.get("last_name", ""),
                "passport_number": data.get("passport_number", ""),
                "birth_date": data.get("birth_date", ""),
                "passport_expiry": data.get("passport_expiry", ""),
                "success": True,
                "error": None
            }
            
        except json.JSONDecodeError as e:
            return {
                "first_name": "",
                "last_name": "",
                "passport_number": "",
                "birth_date": "",
                "passport_expiry": "",
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
                "first_name": "",
                "last_name": "",
                "passport_number": "",
                "birth_date": "",
                "passport_expiry": "",
                "success": False,
                "error": last_error
            }
    
    return {
        "first_name": "",
        "last_name": "",
        "passport_number": "",
        "birth_date": "",
        "passport_expiry": "",
        "success": False,
        "error": f"Failed after {max_retries} attempts: {last_error}"
    }
