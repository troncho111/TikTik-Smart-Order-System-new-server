"""
Hotel Resolver using Google Places API
Fetches hotel details and photos, saves images locally for PDF generation
With database caching to avoid repeated API calls
"""

import os
import requests
import uuid
from pathlib import Path


GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', '')
HOTELS_DIR = Path('attached_assets/hotels')
REQUEST_TIMEOUT = 10


def get_cached_hotel(query: str):
    """Check if hotel is in cache. Returns None if images are missing (to trigger re-download)."""
    try:
        from models import get_db, HotelCache
        db = get_db()
        if db:
            normalized_query = query.strip().lower()
            cached = db.query(HotelCache).filter(
                HotelCache.search_query == normalized_query
            ).first()
            
            if cached:
                has_image_1 = cached.hotel_image_path and os.path.exists(cached.hotel_image_path)
                
                if not has_image_1:
                    db.delete(cached)
                    db.commit()
                    db.close()
                    return None
                
                result = cached.to_dict()
                result['hotel_image_path'] = cached.hotel_image_path
                if cached.hotel_image_path_2 and os.path.exists(cached.hotel_image_path_2):
                    result['hotel_image_path_2'] = cached.hotel_image_path_2
                result['from_cache'] = True
                db.close()
                return result
            db.close()
    except Exception as e:
        print(f"Cache lookup error: {e}")
    return None


def save_to_cache(query: str, result: dict, place_id: str = None):
    """Save hotel result to cache"""
    try:
        from models import get_db, HotelCache
        db = get_db()
        if db:
            normalized_query = query.strip().lower()
            existing = db.query(HotelCache).filter(
                HotelCache.search_query == normalized_query
            ).first()
            
            if not existing:
                cache_entry = HotelCache(
                    search_query=normalized_query,
                    hotel_name=result.get('hotel_name'),
                    hotel_address=result.get('hotel_address'),
                    hotel_website=result.get('hotel_website'),
                    hotel_rating=result.get('hotel_rating'),
                    hotel_image_path=result.get('hotel_image_path'),
                    hotel_image_path_2=result.get('hotel_image_path_2'),
                    place_id=place_id
                )
                db.add(cache_entry)
                db.commit()
            db.close()
    except Exception as e:
        print(f"Cache save error: {e}")


def ensure_hotels_dir():
    """Create hotels directory if it doesn't exist"""
    HOTELS_DIR.mkdir(parents=True, exist_ok=True)


def find_place_id(query: str) -> str | None:
    """
    Find Place From Text API - returns place_id for the first result
    """
    if not GOOGLE_PLACES_API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY not configured")
    
    url = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    params = {
        'input': query,
        'inputtype': 'textquery',
        'fields': 'place_id',
        'key': GOOGLE_PLACES_API_KEY
    }
    
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    
    if data.get('status') != 'OK' or not data.get('candidates'):
        return None
    
    return data['candidates'][0].get('place_id')


def get_place_details(place_id: str) -> dict | None:
    """
    Place Details API - returns hotel info and photo references
    """
    if not GOOGLE_PLACES_API_KEY:
        raise ValueError("GOOGLE_PLACES_API_KEY not configured")
    
    url = "https://maps.googleapis.com/maps/api/place/details/json"
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,website,rating,photos',
        'key': GOOGLE_PLACES_API_KEY
    }
    
    response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()
    data = response.json()
    
    if data.get('status') != 'OK' or not data.get('result'):
        return None
    
    result = data['result']
    return {
        'hotel_name': result.get('name', ''),
        'hotel_address': result.get('formatted_address', ''),
        'hotel_website': result.get('website', ''),
        'hotel_rating': result.get('rating'),
        'photos': result.get('photos', [])[:2]  # Take first 2 photos
    }


def download_place_photo(photo_reference: str, save_path: Path) -> bool:
    """
    Download a photo from Google Places Photo API and save locally
    """
    if not GOOGLE_PLACES_API_KEY:
        return False
    
    url = "https://maps.googleapis.com/maps/api/place/photo"
    params = {
        'maxwidth': 1600,
        'photo_reference': photo_reference,
        'key': GOOGLE_PLACES_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        response.raise_for_status()
        
        # Save the image bytes
        with open(save_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"Error downloading photo: {e}")
        return False


def resolve_hotel(query: str, order_id: str = None) -> dict:
    """
    Main function to resolve hotel info and download images
    
    Args:
        query: Hotel name + city (e.g., "Hilton Madrid, Madrid")
        order_id: Optional order ID for naming saved images
    
    Returns:
        dict with hotel info and local image paths
    """
    # Check cache first
    cached = get_cached_hotel(query)
    if cached:
        return cached
    
    ensure_hotels_dir()
    
    # Generate unique ID if not provided
    if not order_id:
        order_id = uuid.uuid4().hex[:8]
    
    # Step 1: Find place_id
    place_id = find_place_id(query)
    if not place_id:
        return {'error': 'מלון לא נמצא', 'status': 404}
    
    # Step 2: Get place details
    details = get_place_details(place_id)
    if not details:
        return {'error': 'לא ניתן לקבל פרטי מלון', 'status': 500}
    
    result = {
        'hotel_name': details['hotel_name'],
        'hotel_address': details['hotel_address'],
        'hotel_website': details['hotel_website'],
        'hotel_rating': details['hotel_rating'],
        'hotel_image_path': None,
        'hotel_image_path_2': None
    }
    
    # Step 3: Download photos (up to 2)
    photos = details.get('photos', [])
    
    for i, photo in enumerate(photos[:2]):
        photo_ref = photo.get('photo_reference')
        if not photo_ref:
            continue
        
        # Save path
        save_path = HOTELS_DIR / f"{order_id}_{i+1}.jpg"
        
        if download_place_photo(photo_ref, save_path):
            if i == 0:
                result['hotel_image_path'] = str(save_path)
            else:
                result['hotel_image_path_2'] = str(save_path)
    
    # Save to cache for future lookups
    save_to_cache(query, result, place_id)
    
    return result


def resolve_hotel_safe(query: str, order_id: str = None) -> dict:
    """
    Safe wrapper with error handling
    """
    try:
        return resolve_hotel(query, order_id)
    except ValueError as e:
        return {'error': str(e), 'status': 400}
    except requests.exceptions.Timeout:
        return {'error': 'תם הזמן לחיבור ל-Google Places', 'status': 504}
    except requests.exceptions.RequestException as e:
        return {'error': f'שגיאת רשת: {str(e)}', 'status': 500}
    except Exception as e:
        return {'error': f'שגיאה לא צפויה: {str(e)}', 'status': 500}
