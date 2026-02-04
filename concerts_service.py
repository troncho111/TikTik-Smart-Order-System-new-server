"""
Ticketmaster Discovery API + RapidAPI Real-Time Events integration for live concert data.
Fetches real-time concert/event information from multiple sources for comprehensive coverage.
Uses database caching to share results across all users and reduce API calls.
"""

import os
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import json
import re
from bs4 import BeautifulSoup

TICKETMASTER_API_KEY = os.environ.get('TICKETMASTER_API_KEY', '')
RAPIDAPI_KEY = os.environ.get('RAPIDAPI_KEY', '')
BASE_URL = "https://app.ticketmaster.com/discovery/v2"
RAPIDAPI_HOST = "real-time-events-search.p.rapidapi.com"

_cache = {}
CACHE_DURATION_HOURS = 24


def _get_db_cache(cache_key: str) -> Optional[Dict]:
    """Get cached concert results from database"""
    try:
        from models import get_db, ConcertCache
        db = get_db()
        if not db:
            return None
        
        cached = db.query(ConcertCache).filter(
            ConcertCache.cache_key == cache_key,
            ConcertCache.expires_at > datetime.utcnow()
        ).first()
        
        if cached:
            result = {
                'concerts': json.loads(cached.concerts_json) if cached.concerts_json else [],
                'total': cached.total_results,
                'artist_id': cached.artist_id,
                'artist_name': cached.artist_name,
                'source': cached.source,
                'from_cache': True,
                'error': None
            }
            db.close()
            return result
        
        db.close()
        return None
    except Exception as e:
        print(f"DB cache read error: {e}")
        return None


def _set_db_cache(cache_key: str, data: Dict, artist_id: str = '', artist_name: str = '', source: str = 'combined'):
    """Save concert results to database cache"""
    try:
        from models import get_db, ConcertCache
        db = get_db()
        if not db:
            return
        
        existing = db.query(ConcertCache).filter(ConcertCache.cache_key == cache_key).first()
        
        concerts_json = json.dumps(data.get('concerts', []), ensure_ascii=False)
        expires_at = datetime.utcnow() + timedelta(hours=CACHE_DURATION_HOURS)
        
        if existing:
            existing.concerts_json = concerts_json
            existing.total_results = data.get('total', 0)
            existing.artist_id = artist_id
            existing.artist_name = artist_name
            existing.source = source
            existing.created_at = datetime.utcnow()
            existing.expires_at = expires_at
        else:
            new_cache = ConcertCache(
                cache_key=cache_key,
                artist_id=artist_id,
                artist_name=artist_name,
                concerts_json=concerts_json,
                total_results=data.get('total', 0),
                source=source,
                expires_at=expires_at
            )
            db.add(new_cache)
        
        db.commit()
        db.close()
    except Exception as e:
        print(f"DB cache write error: {e}")
        try:
            db.rollback()
            db.close()
        except:
            pass

EUROPEAN_COUNTRIES = {
    'AT', 'BE', 'BG', 'HR', 'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'DE', 'GR', 'HU', 
    'IE', 'IT', 'LV', 'LT', 'LU', 'MT', 'NL', 'PL', 'PT', 'RO', 'SK', 'SI', 'ES', 
    'SE', 'CH', 'GB', 'NO', 'IS', 'TR', 'UA', 'RU'
}

POPULAR_ARTISTS = [
    {"id": "K8vZ9171izV", "name_en": "Coldplay", "name_he": "קולדפליי", "genre": "Rock/Pop"},
    {"id": "K8vZ917CAQV", "name_en": "Ed Sheeran", "name_he": "אד שירן", "genre": "Pop"},
    {"id": "K8vZ917GJc7", "name_en": "Bruno Mars", "name_he": "ברונו מארס", "genre": "Pop/R&B"},
    {"id": "K8vZ9175Tr0", "name_en": "Taylor Swift", "name_he": "טיילור סוויפט", "genre": "Pop"},
    {"id": "K8vZ9171G9V", "name_en": "Metallica", "name_he": "מטאליקה", "genre": "Rock/Metal"},
    {"id": "K8vZ9171bQ0", "name_en": "Andrea Bocelli", "name_he": "אנדראה בוצ'לי", "genre": "Classical/Opera"},
    {"id": "K8vZ9172Ln7", "name_en": "The Weeknd", "name_he": "דה ויקנד", "genre": "R&B/Pop"},
    {"id": "K8vZ917hv-f", "name_en": "Adele", "name_he": "אדל", "genre": "Pop/Soul"},
    {"id": "K8vZ917135f", "name_en": "Rod Stewart", "name_he": "רוד סטיוארט", "genre": "Rock/Pop"},
    {"id": "K8vZ9171bjf", "name_en": "Andre Rieu", "name_he": "אנדרה ריו", "genre": "Classical/Waltz"},
]



def get_popular_artists():
    """Get list of popular artists with Hebrew names and Ticketmaster IDs"""
    return POPULAR_ARTISTS


def _get_cache_key(prefix: str, key: str) -> str:
    """Generate cache key"""
    return f"{prefix}_{key.lower()}"


def _is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid"""
    if cache_key not in _cache:
        return False
    cached_time = _cache[cache_key].get('timestamp')
    if not cached_time:
        return False
    return datetime.now() - cached_time < timedelta(hours=CACHE_DURATION_HOURS)


def search_artists(query: str, size: int = 10) -> Dict:
    """
    Search for artists/attractions on Ticketmaster.
    Returns list of artists with their unique IDs for accurate event lookup.
    
    Args:
        query: Artist name to search for
        size: Max number of results
    
    Returns:
        Dict with 'artists' list containing id, name, genre, image_url
    """
    if not TICKETMASTER_API_KEY:
        return {'error': 'API key not configured', 'artists': []}
    
    if not query or len(query.strip()) < 2:
        return {'error': 'Query too short', 'artists': []}
    
    cache_key = _get_cache_key('artists', query)
    if _is_cache_valid(cache_key):
        cached = _cache[cache_key]['data']
        if not cached.get('error'):
            return cached
    
    try:
        params = {
            'apikey': TICKETMASTER_API_KEY,
            'keyword': query.strip(),
            'classificationName': 'music',
            'size': min(size, 50),
            'sort': 'relevance,desc'
        }
        
        response = requests.get(
            f"{BASE_URL}/attractions.json",
            params=params,
            timeout=10
        )
        
        if response.status_code == 429:
            return {'error': 'Rate limit exceeded', 'artists': []}
        
        response.raise_for_status()
        data = response.json()
        
        artists = []
        embedded = data.get('_embedded', {})
        attractions = embedded.get('attractions', [])
        
        for attraction in attractions:
            artist = _parse_attraction(attraction)
            if artist:
                artists.append(artist)
        
        result = {
            'artists': artists,
            'total': len(artists),
            'error': None
        }
        
        _cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
        
        return result
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout', 'artists': []}
    except requests.exceptions.RequestException as e:
        return {'error': f'API error: {str(e)}', 'artists': []}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}', 'artists': []}


def _parse_attraction(attraction: dict) -> Optional[Dict]:
    """Parse Ticketmaster attraction into artist format"""
    try:
        artist_id = attraction.get('id', '')
        name = attraction.get('name', '')
        
        if not artist_id or not name:
            return None
        
        genre = ''
        classifications = attraction.get('classifications', [])
        if classifications:
            cls = classifications[0]
            genre_info = cls.get('genre', {})
            genre = genre_info.get('name', '')
            if not genre:
                segment = cls.get('segment', {})
                genre = segment.get('name', '')
        
        image_url = ''
        images = attraction.get('images', [])
        if images:
            for img in images:
                if img.get('width', 0) >= 300:
                    image_url = img.get('url', '')
                    break
            if not image_url and images:
                image_url = images[0].get('url', '')
        
        upcoming_events = attraction.get('upcomingEvents', {})
        event_count = upcoming_events.get('_total', 0)
        
        return {
            'id': artist_id,
            'name': name,
            'genre': genre,
            'image_url': image_url,
            'upcoming_events': event_count
        }
        
    except Exception:
        return None


def get_events_by_attraction_id(attraction_id: str, artist_name: str = '', size: int = 50, europe_only: bool = True) -> Dict:
    """
    Fetch events for a specific artist using their Ticketmaster Attraction ID.
    This ensures 100% accuracy - only events featuring this exact artist.
    
    Args:
        attraction_id: Ticketmaster attraction ID
        artist_name: Artist name for display
        size: Max number of results
        europe_only: Filter for European venues only
    
    Returns:
        Dict with 'concerts' list and 'total' count
    """
    if not TICKETMASTER_API_KEY:
        return {'error': 'API key not configured', 'concerts': [], 'total': 0}
    
    if not attraction_id:
        return {'error': 'Attraction ID required', 'concerts': [], 'total': 0}
    
    cache_key = _get_cache_key('events', f"{attraction_id}_{europe_only}")
    if _is_cache_valid(cache_key):
        cached = _cache[cache_key]['data']
        if not cached.get('error'):
            return cached
    
    try:
        params = {
            'apikey': TICKETMASTER_API_KEY,
            'attractionId': attraction_id,
            'classificationName': 'music',
            'size': min(size * 2 if europe_only else size, 200),
            'sort': 'date,asc'
        }
        
        response = requests.get(
            f"{BASE_URL}/events.json",
            params=params,
            timeout=15
        )
        
        if response.status_code == 429:
            return {'error': 'Rate limit exceeded', 'concerts': [], 'total': 0}
        
        response.raise_for_status()
        data = response.json()
        
        concerts = []
        embedded = data.get('_embedded', {})
        events = embedded.get('events', [])
        
        for event in events:
            concert = _parse_event(event, artist_name)
            if concert:
                if europe_only:
                    country = concert.get('country', '').upper()
                    if country in EUROPEAN_COUNTRIES:
                        concerts.append(concert)
                else:
                    concerts.append(concert)
        
        concerts = concerts[:size]
        
        result = {
            'concerts': concerts,
            'total': len(concerts),
            'artist_id': attraction_id,
            'artist_name': artist_name,
            'error': None
        }
        
        _cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
        
        return result
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout', 'concerts': [], 'total': 0}
    except requests.exceptions.RequestException as e:
        return {'error': f'API error: {str(e)}', 'concerts': [], 'total': 0}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}', 'concerts': [], 'total': 0}


def _parse_event(event: dict, artist_name: str) -> Optional[Dict]:
    """Parse Ticketmaster event into our concert format"""
    try:
        name = event.get('name', '')
        event_id = event.get('id', '')
        
        dates = event.get('dates', {})
        start = dates.get('start', {})
        local_date = start.get('localDate', '')
        local_time = start.get('localTime', '')
        if local_time:
            local_time = local_time[:5]
        
        venue_name = ''
        venue_city = ''
        venue_country = ''
        venue_address = ''
        venue_id = ''
        venue_url = ''
        venue_phone = ''
        venue_postal_code = ''
        venue_capacity = None
        
        embedded = event.get('_embedded', {})
        venues = embedded.get('venues', [])
        if venues:
            venue = venues[0]
            venue_id = venue.get('id', '')
            venue_name = venue.get('name', '')
            venue_url = venue.get('url', '')
            venue_phone = venue.get('phoneNumberDetail', '')
            city_info = venue.get('city', {})
            venue_city = city_info.get('name', '')
            country_info = venue.get('country', {})
            venue_country = country_info.get('countryCode', '')
            address_info = venue.get('address', {})
            venue_address = address_info.get('line1', '')
            postal_info = venue.get('postalCode', '')
            venue_postal_code = postal_info if postal_info else ''
            venue_capacity = venue.get('capacity')
        
        price_min = None
        price_max = None
        currency = 'EUR'
        price_ranges = event.get('priceRanges', [])
        if price_ranges:
            price_min = price_ranges[0].get('min')
            price_max = price_ranges[0].get('max')
            currency = price_ranges[0].get('currency', 'EUR')
        
        url = event.get('url', '')
        
        images = event.get('images', [])
        image_url = ''
        if images:
            for img in images:
                if img.get('width', 0) >= 500:
                    image_url = img.get('url', '')
                    break
            if not image_url and images:
                image_url = images[0].get('url', '')
        
        return {
            'id': event_id,
            'name': name,
            'artist': artist_name,
            'date': local_date,
            'time': local_time,
            'venue': venue_name,
            'venue_id': venue_id,
            'venue_url': venue_url,
            'venue_phone': venue_phone,
            'city': venue_city,
            'country': venue_country,
            'address': venue_address,
            'postal_code': venue_postal_code,
            'capacity': venue_capacity,
            'price_min': price_min,
            'price_max': price_max,
            'currency': currency,
            'url': url,
            'image_url': image_url
        }
        
    except Exception:
        return None


def get_popular_artists_with_events(size: int = 20) -> Dict:
    """
    Get popular music artists that have upcoming events.
    Fetches from Ticketmaster's trending/popular attractions.
    
    Returns:
        Dict with 'artists' list
    """
    if not TICKETMASTER_API_KEY:
        return {'error': 'API key not configured', 'artists': []}
    
    cache_key = 'popular_artists'
    if _is_cache_valid(cache_key):
        cached = _cache[cache_key]['data']
        if not cached.get('error'):
            return cached
    
    try:
        params = {
            'apikey': TICKETMASTER_API_KEY,
            'classificationName': 'music',
            'size': size,
            'sort': 'relevance,desc'
        }
        
        response = requests.get(
            f"{BASE_URL}/attractions.json",
            params=params,
            timeout=10
        )
        
        if response.status_code == 429:
            return {'error': 'Rate limit exceeded', 'artists': []}
        
        response.raise_for_status()
        data = response.json()
        
        artists = []
        embedded = data.get('_embedded', {})
        attractions = embedded.get('attractions', [])
        
        for attraction in attractions:
            artist = _parse_attraction(attraction)
            if artist and artist.get('upcoming_events', 0) > 0:
                artists.append(artist)
        
        result = {
            'artists': artists[:size],
            'total': len(artists),
            'error': None
        }
        
        _cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
        
        return result
        
    except Exception as e:
        return {'error': str(e), 'artists': []}


def format_concert_for_display(concert: dict) -> str:
    """Format concert info for Hebrew display"""
    date_str = concert.get('date', '')
    if date_str:
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            date_str = date_obj.strftime('%d/%m/%Y')
        except:
            pass
    
    time_str = concert.get('time', '')
    venue = concert.get('venue', '')
    city = concert.get('city', '')
    country = concert.get('country', '')
    
    location = f"{venue}, {city}" if venue and city else venue or city
    if country:
        location += f" ({country})"
    
    return f"{date_str} {time_str} - {location}"


def clear_cache():
    """Clear all cached data"""
    global _cache
    _cache = {}


def fetch_venue_map_from_ticketmaster(event_url: str, venue_id: str) -> Optional[str]:
    """
    Extract venue map image from Ticketmaster event page.
    Saves the image to attached_assets/concert_venue_maps/{venue_id}.ext
    
    Note: Ticketmaster uses bot protection, so this has limited success.
    Manual upload is the more reliable method.
    """
    if not event_url or not venue_id:
        return None
    
    try:
        os.makedirs('attached_assets/concert_venue_maps', exist_ok=True)
        
        for ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
            existing_path = f'attached_assets/concert_venue_maps/{venue_id}.{ext}'
            if os.path.exists(existing_path):
                return existing_path
        
        output_path = f'attached_assets/concert_venue_maps/{venue_id}.png'
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(event_url, headers=headers, timeout=20)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        map_img_url = None
        
        for tag in soup.find_all(['img', 'div', 'a', 'source']):
            for attr in ['src', 'data-src', 'href', 'srcset', 'data-lazy-src', 'data-original']:
                attr_val = tag.get(attr, '')
                if attr_val and 'tmimages' in str(attr_val).lower() and ('venue' in str(attr_val).lower() or 'map' in str(attr_val).lower()):
                    map_img_url = str(attr_val).split(' ')[0]
                    break
            if map_img_url:
                break
        
        if not map_img_url:
            for img in soup.find_all('img'):
                alt = str(img.get('alt', '')).lower()
                if any(kw in alt for kw in ['venue map', 'seating', 'seat map', 'floor plan', 'seatmap']):
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy-src')
                    if src:
                        map_img_url = str(src)
                        break
        
        if not map_img_url:
            page_text = response.text
            patterns = [
                r'https?://[^"\'\s<>]+tmimages[^"\'\s<>]+maps?[^"\'\s<>]+\.(gif|png|jpg|jpeg)',
                r'https?://[^"\'\s<>]+seatmap[^"\'\s<>]+\.(gif|png|jpg|jpeg)',
            ]
            for pattern in patterns:
                full_match = re.search(pattern, page_text, re.IGNORECASE)
                if full_match:
                    map_img_url = full_match.group(0)
                    break
        
        if map_img_url:
            if not map_img_url.startswith('http'):
                if map_img_url.startswith('//'):
                    map_img_url = 'https:' + map_img_url
                else:
                    from urllib.parse import urljoin
                    map_img_url = urljoin(event_url, map_img_url)
            
            img_response = requests.get(map_img_url, headers=headers, timeout=15)
            if img_response.status_code == 200:
                ext = 'png'
                if '.gif' in map_img_url.lower():
                    ext = 'gif'
                elif '.jpg' in map_img_url.lower() or '.jpeg' in map_img_url.lower():
                    ext = 'jpg'
                content_type = img_response.headers.get('content-type', '')
                if 'gif' in content_type:
                    ext = 'gif'
                elif 'jpeg' in content_type or 'jpg' in content_type:
                    ext = 'jpg'
                
                save_path = f'attached_assets/concert_venue_maps/{venue_id}.{ext}'
                with open(save_path, 'wb') as f:
                    f.write(img_response.content)
                return save_path
        
        return None
    
    except Exception as e:
        print(f"Error fetching venue map: {e}")
        return None


def is_ticketmaster_url(url: str) -> bool:
    """Check if URL is a Ticketmaster event page"""
    if not url:
        return False
    tm_domains = ['ticketmaster.com', 'ticketmaster.co.uk', 'ticketmaster.de', 
                  'ticketmaster.nl', 'ticketmaster.es', 'ticketmaster.fr',
                  'ticketmaster.it', 'ticketmaster.at', 'ticketmaster.be',
                  'ticketmaster.cz', 'ticketmaster.pl', 'ticketmaster.ie',
                  'ticketmaster.se', 'ticketmaster.no', 'ticketmaster.dk',
                  'ticketmaster.fi', 'ticketmaster.ch', 'ticketmaster.pt']
    return any(domain in url.lower() for domain in tm_domains)


def search_events_rapidapi(query: str, size: int = 20) -> Dict:
    """
    Search for concerts/events using RapidAPI Real-Time Events Search.
    This API aggregates from multiple sources including regional Ticketmaster sites,
    Spotify, Tixel, TicketSwap, and more.
    
    Args:
        query: Search query (artist name, location, etc.)
        size: Max number of results
    
    Returns:
        Dict with 'concerts' list and metadata
    """
    if not RAPIDAPI_KEY:
        return {'error': 'RapidAPI key not configured', 'concerts': [], 'total': 0}
    
    if not query or len(query.strip()) < 2:
        return {'error': 'Query too short', 'concerts': [], 'total': 0}
    
    cache_key = _get_cache_key('rapidapi_events', query)
    if _is_cache_valid(cache_key):
        cached = _cache[cache_key]['data']
        if not cached.get('error'):
            return cached
    
    try:
        headers = {
            'X-RapidAPI-Key': RAPIDAPI_KEY,
            'X-RapidAPI-Host': RAPIDAPI_HOST
        }
        
        response = requests.get(
            f'https://{RAPIDAPI_HOST}/search-events',
            params={'query': query.strip(), 'start': '0'},
            headers=headers,
            timeout=15
        )
        
        if response.status_code == 429:
            return {'error': 'Rate limit exceeded', 'concerts': [], 'total': 0}
        
        if response.status_code == 403:
            return {'error': 'API subscription required', 'concerts': [], 'total': 0}
        
        response.raise_for_status()
        data = response.json()
        
        concerts = []
        events = data.get('data', [])
        
        for event in events[:size]:
            concert = _parse_rapidapi_event(event, query)
            if concert:
                if concert.get('country', '').upper() in EUROPEAN_COUNTRIES:
                    concerts.append(concert)
        
        result = {
            'concerts': concerts,
            'total': len(concerts),
            'source': 'rapidapi',
            'error': None
        }
        
        _cache[cache_key] = {
            'data': result,
            'timestamp': datetime.now()
        }
        
        return result
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout', 'concerts': [], 'total': 0}
    except requests.exceptions.RequestException as e:
        return {'error': f'API error: {str(e)}', 'concerts': [], 'total': 0}
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}', 'concerts': [], 'total': 0}


def _parse_rapidapi_event(event: dict, search_query: str) -> Optional[Dict]:
    """Parse RapidAPI event into our standard concert format"""
    try:
        name = event.get('name', '')
        description = event.get('description', '')
        event_id = event.get('event_id', '')
        
        start_time = event.get('start_time', '')
        local_date = ''
        local_time = ''
        if start_time:
            try:
                dt = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
                local_date = dt.strftime('%Y-%m-%d')
                local_time = dt.strftime('%H:%M')
            except:
                parts = start_time.split(' ')
                if parts:
                    local_date = parts[0]
                    if len(parts) > 1:
                        local_time = parts[1][:5]
        
        venue_info = event.get('venue', {})
        venue_name = venue_info.get('name', '')
        venue_city = venue_info.get('city', '')
        venue_country = venue_info.get('country', '')
        venue_address = venue_info.get('full_address', '')
        venue_phone = venue_info.get('phone_number', '')
        venue_website = venue_info.get('website', '')
        venue_rating = venue_info.get('rating')
        venue_zipcode = venue_info.get('zipcode', '')
        
        ticket_links = event.get('ticket_links', [])
        primary_url = event.get('link', '')
        ticketmaster_url = ''
        for link in ticket_links:
            source = link.get('source', '').lower()
            if 'ticketmaster' in source:
                ticketmaster_url = link.get('link', '')
                break
        
        url = ticketmaster_url or primary_url
        
        image_url = event.get('thumbnail', '')
        
        artist_name = search_query.split()[0] if search_query else name
        for ticket_link in ticket_links:
            link_url = ticket_link.get('link', '').lower()
            if 'metallica' in link_url:
                artist_name = 'Metallica'
                break
            elif 'iron-maiden' in link_url or 'ironmaiden' in link_url:
                artist_name = 'Iron Maiden'
                break
            elif 'coldplay' in link_url:
                artist_name = 'Coldplay'
                break
        
        return {
            'id': event_id,
            'name': name,
            'description': description,
            'artist': artist_name,
            'date': local_date,
            'time': local_time,
            'venue': venue_name,
            'venue_id': venue_info.get('google_id', ''),
            'venue_url': venue_website or url,
            'venue_phone': venue_phone,
            'city': venue_city,
            'country': venue_country,
            'address': venue_address,
            'postal_code': venue_zipcode,
            'capacity': None,
            'price_min': None,
            'price_max': None,
            'currency': 'EUR',
            'url': url,
            'image_url': image_url,
            'ticket_links': ticket_links,
            'source': 'rapidapi'
        }
        
    except Exception:
        return None


def search_events_combined(artist_name: str, attraction_id: str = '', size: int = 30) -> Dict:
    """
    Search for events using both Ticketmaster and RapidAPI, combining results.
    This provides the most comprehensive coverage.
    Uses database caching to share results across all users.
    
    Args:
        artist_name: Artist name to search for
        attraction_id: Ticketmaster attraction ID (optional, for more accurate TM results)
        size: Max total results
    
    Returns:
        Dict with combined 'concerts' list from both sources
    """
    cache_key = f"combined_{artist_name.lower()}_{attraction_id}"
    
    cached_result = _get_db_cache(cache_key)
    if cached_result:
        print(f"Using cached results for {artist_name}")
        return cached_result
    
    all_concerts = []
    seen_events = set()
    errors = []
    
    if attraction_id and TICKETMASTER_API_KEY:
        tm_result = get_events_by_attraction_id(attraction_id, artist_name, size=size//2)
        if tm_result.get('error'):
            errors.append(f"Ticketmaster: {tm_result['error']}")
        for concert in tm_result.get('concerts', []):
            event_key = f"{concert.get('date')}_{concert.get('venue', '')[:20]}"
            if event_key not in seen_events:
                concert['source'] = 'ticketmaster'
                all_concerts.append(concert)
                seen_events.add(event_key)
    
    if RAPIDAPI_KEY:
        search_queries = [
            f"{artist_name} concert 2025 2026",
            f"{artist_name} tour Europe",
            f"{artist_name} live 2026"
        ]
        
        artist_lower = artist_name.lower()
        
        for query in search_queries:
            rapid_result = search_events_rapidapi(query, size=size//2)
            if rapid_result.get('error'):
                if rapid_result['error'] not in [e for e in errors]:
                    errors.append(f"RapidAPI: {rapid_result['error']}")
            
            for concert in rapid_result.get('concerts', []):
                event_key = f"{concert.get('date')}_{concert.get('venue', '')[:20]}"
                if event_key not in seen_events:
                    concert_artist = concert.get('artist', '').lower()
                    concert_name = concert.get('name', '').lower()
                    
                    if artist_lower in concert_artist or artist_lower in concert_name:
                        all_concerts.append(concert)
                        seen_events.add(event_key)
                    else:
                        for tl in concert.get('ticket_links', []):
                            if artist_lower in tl.get('link', '').lower():
                                all_concerts.append(concert)
                                seen_events.add(event_key)
                                break
    
    all_concerts.sort(key=lambda x: x.get('date', ''))
    
    result = {
        'concerts': all_concerts[:size],
        'total': len(all_concerts),
        'sources': ['ticketmaster', 'rapidapi'],
        'errors': errors if errors else None,
        'error': None
    }
    
    if all_concerts:
        _set_db_cache(cache_key, result, artist_id=attraction_id, artist_name=artist_name, source='combined')
    
    return result


def search_concerts_by_location(location: str, artist_name: str = '', size: int = 20) -> Dict:
    """
    Search for concerts in a specific location using RapidAPI.
    Great for finding events that aren't in Ticketmaster's main API.
    
    Args:
        location: Location name (city, country, venue)
        artist_name: Optional artist name to filter
        size: Max results
    
    Returns:
        Dict with 'concerts' list
    """
    if not RAPIDAPI_KEY:
        return {'error': 'RapidAPI key not configured', 'concerts': [], 'total': 0}
    
    query = f"{artist_name} {location} concert 2026" if artist_name else f"concerts {location} 2026"
    return search_events_rapidapi(query, size)


def extract_concert_from_url(url: str) -> Dict:
    """
    Extract concert details from any event URL.
    Supports multiple ticket platforms: Ticketmaster, Eventim, See Tickets, Viagogo, StubHub, etc.
    
    Args:
        url: Event page URL
    
    Returns:
        Dict with extracted concert details or error
    """
    if not url or not url.startswith('http'):
        return {'error': 'Invalid URL', 'concert': None}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
        }
        
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code != 200:
            return {'error': f'Could not fetch page (status {response.status_code})', 'concert': None}
        
        soup = BeautifulSoup(response.text, 'lxml')
        
        concert = {
            'name': '',
            'artist': '',
            'date': '',
            'time': '',
            'venue': '',
            'city': '',
            'country': '',
            'address': '',
            'url': url,
            'source': _get_url_source(url)
        }
        
        og_title = soup.find('meta', property='og:title')
        if og_title:
            concert['name'] = og_title.get('content', '')
        
        if not concert['name']:
            title_tag = soup.find('title')
            if title_tag:
                concert['name'] = title_tag.get_text().strip()
        
        for tag in soup.find_all(['script']):
            if tag.get('type') == 'application/ld+json':
                try:
                    ld_data = json.loads(tag.string)
                    if isinstance(ld_data, list):
                        ld_data = ld_data[0]
                    
                    if ld_data.get('@type') in ['Event', 'MusicEvent', 'Festival']:
                        concert['name'] = ld_data.get('name', concert['name'])
                        
                        start_date = ld_data.get('startDate', '')
                        if start_date:
                            if 'T' in start_date:
                                parts = start_date.split('T')
                                concert['date'] = parts[0]
                                if len(parts) > 1:
                                    time_part = parts[1].split('+')[0].split('-')[0][:5]
                                    concert['time'] = time_part
                            else:
                                concert['date'] = start_date[:10]
                        
                        location = ld_data.get('location', {})
                        if isinstance(location, dict):
                            concert['venue'] = location.get('name', '')
                            address = location.get('address', {})
                            if isinstance(address, dict):
                                concert['city'] = address.get('addressLocality', '')
                                concert['country'] = address.get('addressCountry', '')
                                concert['address'] = address.get('streetAddress', '')
                            elif isinstance(address, str):
                                concert['address'] = address
                        
                        performers = ld_data.get('performer', [])
                        if performers:
                            if isinstance(performers, list) and len(performers) > 0:
                                concert['artist'] = performers[0].get('name', '')
                            elif isinstance(performers, dict):
                                concert['artist'] = performers.get('name', '')
                        
                        break
                except:
                    continue
        
        if not concert['venue']:
            venue_patterns = [
                soup.find(class_=re.compile(r'venue', re.I)),
                soup.find(attrs={'data-venue': True}),
                soup.find('span', class_=re.compile(r'location', re.I)),
            ]
            for v in venue_patterns:
                if v:
                    text = v.get_text().strip()
                    if text and len(text) < 200:
                        concert['venue'] = text
                        break
        
        if not concert['date']:
            date_patterns = [
                soup.find(class_=re.compile(r'date', re.I)),
                soup.find('time'),
                soup.find(attrs={'datetime': True}),
            ]
            for d in date_patterns:
                if d:
                    dt = d.get('datetime', '')
                    if dt:
                        concert['date'] = dt[:10]
                        break
                    text = d.get_text().strip()
                    date_match = re.search(r'(\d{1,2})[/.-](\d{1,2})[/.-](\d{2,4})', text)
                    if date_match:
                        day, month, year = date_match.groups()
                        if len(year) == 2:
                            year = '20' + year
                        concert['date'] = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                        break
        
        # Try to parse details from title for LiveNation and similar sites
        if concert['name'] and not concert['artist']:
            title = concert['name']
            
            # LiveNation format: "Artist Name, City, Date, Venue - site"
            # Example: "Lenny Kravitz Live 2026, Budapest, 2026. augusztus 2., , Tickets"
            title_clean = re.sub(r'\s*[-–|]\s*(www\.|Tickets).*$', '', title, flags=re.I)
            title_clean = re.sub(r',\s*Tickets.*$', '', title_clean, flags=re.I)
            
            # Hungarian month names
            hu_months = {
                'január': '01', 'február': '02', 'március': '03', 'április': '04',
                'május': '05', 'június': '06', 'július': '07', 'augusztus': '08',
                'szeptember': '09', 'október': '10', 'november': '11', 'december': '12'
            }
            
            # Try to extract date from Hungarian format: "2026. augusztus 2."
            hu_date_match = re.search(r'(\d{4})\.\s*([a-záéíóöőúüű]+)\s*(\d{1,2})\.?', title_clean, re.I)
            if hu_date_match:
                year, month_hu, day = hu_date_match.groups()
                month_num = hu_months.get(month_hu.lower(), '')
                if month_num:
                    concert['date'] = f"{year}-{month_num}-{day.zfill(2)}"
            
            # Split by comma and try to extract artist and city
            parts = [p.strip() for p in title_clean.split(',') if p.strip()]
            if parts:
                # First part is usually artist/event name
                artist_part = parts[0]
                # Remove "Live 2026" or similar suffixes
                artist_clean = re.sub(r'\s*(Live|Tour|Concert)\s*\d{4}.*$', '', artist_part, flags=re.I)
                if artist_clean:
                    concert['artist'] = artist_clean.strip()
                
                # Look for city (usually after artist, before date)
                for part in parts[1:]:
                    # Skip if it looks like a date
                    if re.search(r'\d{4}', part):
                        continue
                    # Skip empty or very short
                    if len(part) < 3:
                        continue
                    # This is likely the city
                    if not concert['city']:
                        concert['city'] = part.strip()
                        break
            
            # For LiveNation Hungary, set country
            if 'livenation.hu' in url.lower() and not concert['country']:
                concert['country'] = 'Hungary'
        
        if concert['name'] or concert['venue']:
            return {'concert': concert, 'error': None}
        else:
            return {'error': 'Could not extract event details from page', 'concert': None}
        
    except requests.exceptions.Timeout:
        return {'error': 'Request timeout', 'concert': None}
    except requests.exceptions.RequestException as e:
        return {'error': f'Network error: {str(e)}', 'concert': None}
    except Exception as e:
        return {'error': f'Extraction error: {str(e)}', 'concert': None}


def _get_url_source(url: str) -> str:
    """Identify the source platform from URL"""
    url_lower = url.lower()
    
    if 'ticketmaster' in url_lower:
        return 'Ticketmaster'
    elif 'eventim' in url_lower:
        return 'Eventim'
    elif 'seetickets' in url_lower:
        return 'See Tickets'
    elif 'viagogo' in url_lower:
        return 'Viagogo'
    elif 'stubhub' in url_lower:
        return 'StubHub'
    elif 'livenation' in url_lower:
        return 'Live Nation'
    elif 'bandsintown' in url_lower:
        return 'Bandsintown'
    elif 'songkick' in url_lower:
        return 'Songkick'
    elif 'axs.com' in url_lower:
        return 'AXS'
    elif 'dice.fm' in url_lower:
        return 'DICE'
    elif 'tixel' in url_lower:
        return 'Tixel'
    elif 'ticketswap' in url_lower:
        return 'TicketSwap'
    else:
        return 'Other'
