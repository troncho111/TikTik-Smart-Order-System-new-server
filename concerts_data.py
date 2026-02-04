"""
Concerts data module - Popular artists and concert venues
Based on TikTik inventory + major European venues
"""

ARTISTS = {
    "Metallica": {
        "name_en": "Metallica",
        "name_he": "מטאליקה",
        "genre": "Rock/Metal",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/68/Metallica_at_The_O2_Arena_London_2008.jpg/1200px-Metallica_at_The_O2_Arena_London_2008.jpg"
    },
    "Andrea Bocelli": {
        "name_en": "Andrea Bocelli",
        "name_he": "אנדראה בוצ'לי",
        "genre": "Classical/Opera",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Andrea_Bocelli_-_Festival_di_Sanremo_2019.jpg/440px-Andrea_Bocelli_-_Festival_di_Sanremo_2019.jpg"
    },
    "Rod Stewart": {
        "name_en": "Rod Stewart",
        "name_he": "רוד סטיוארט",
        "genre": "Rock/Pop",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1b/Rod_Stewart_2015.jpg/440px-Rod_Stewart_2015.jpg"
    },
    "Andre Rieu": {
        "name_en": "Andre Rieu",
        "name_he": "אנדרה ריו",
        "genre": "Classical/Waltz",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Andr%C3%A9_Rieu_2.jpg/440px-Andr%C3%A9_Rieu_2.jpg"
    },
    "Coldplay": {
        "name_en": "Coldplay",
        "name_he": "קולדפליי",
        "genre": "Rock/Pop",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/17/Coldplay_-_Sydney_2012.jpg/1200px-Coldplay_-_Sydney_2012.jpg"
    },
    "Ed Sheeran": {
        "name_en": "Ed Sheeran",
        "name_he": "אד שירן",
        "genre": "Pop",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Ed_Sheeran-6886_%28cropped%29.jpg/440px-Ed_Sheeran-6886_%28cropped%29.jpg"
    },
    "Bruno Mars": {
        "name_en": "Bruno Mars",
        "name_he": "ברונו מארס",
        "genre": "Pop/R&B",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/23/Bruno_Mars_24K_Magic_World_Tour.jpg/440px-Bruno_Mars_24K_Magic_World_Tour.jpg"
    },
    "Adele": {
        "name_en": "Adele",
        "name_he": "אדל",
        "genre": "Pop/Soul",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/7c/Adele_Live_2016_tour.jpeg/440px-Adele_Live_2016_tour.jpeg"
    },
    "The Weeknd": {
        "name_en": "The Weeknd",
        "name_he": "דה ויקנד",
        "genre": "R&B/Pop",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a0/The_Weeknd_with_hand_in_the_air_performing_live_in_Hong_Kong.jpg/440px-The_Weeknd_with_hand_in_the_air_performing_live_in_Hong_Kong.jpg"
    },
    "Taylor Swift": {
        "name_en": "Taylor Swift",
        "name_he": "טיילור סוויפט",
        "genre": "Pop/Country",
        "image": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d7/Taylor_Swift_at_the_2023_MTV_Video_Music_Awards_4.png/440px-Taylor_Swift_at_the_2023_MTV_Video_Music_Awards_4.png"
    }
}

CONCERT_VENUES = {
    "O2 Arena London": {
        "name_en": "The O2 Arena",
        "name_he": "O2 ארנה לונדון",
        "city_en": "London",
        "city_he": "לונדון",
        "country": "UK",
        "capacity": 20000,
        "categories": ["Floor", "Lower Tier", "Upper Tier", "VIP Box"]
    },
    "Wembley Stadium": {
        "name_en": "Wembley Stadium",
        "name_he": "אצטדיון וומבלי",
        "city_en": "London",
        "city_he": "לונדון",
        "country": "UK",
        "capacity": 90000,
        "categories": ["Pitch Standing", "Lower Tier", "Club Wembley", "Upper Tier"]
    },
    "Accor Arena Paris": {
        "name_en": "Accor Arena",
        "name_he": "אקור ארנה פריז",
        "city_en": "Paris",
        "city_he": "פריז",
        "country": "France",
        "capacity": 20300,
        "categories": ["Floor", "Tribune", "Balcony", "VIP"]
    },
    "Stade de France": {
        "name_en": "Stade de France",
        "name_he": "סטאד דה פראנס",
        "city_en": "Paris",
        "city_he": "פריז",
        "country": "France",
        "capacity": 80000,
        "categories": ["Pelouse", "Tribune Basse", "Tribune Haute", "Loge"]
    },
    "Mercedes-Benz Arena Berlin": {
        "name_en": "Mercedes-Benz Arena",
        "name_he": "מרצדס-בנץ ארנה ברלין",
        "city_en": "Berlin",
        "city_he": "ברלין",
        "country": "Germany",
        "capacity": 17000,
        "categories": ["Innenraum", "Unterrang", "Oberrang", "Loge"]
    },
    "Olympiastadion Berlin": {
        "name_en": "Olympiastadion",
        "name_he": "אולימפיאשטדיון ברלין",
        "city_en": "Berlin",
        "city_he": "ברלין",
        "country": "Germany",
        "capacity": 74475,
        "categories": ["Innenraum", "Unterrang", "Oberrang", "VIP"]
    },
    "Ziggo Dome Amsterdam": {
        "name_en": "Ziggo Dome",
        "name_he": "זיגו דום אמסטרדם",
        "city_en": "Amsterdam",
        "city_he": "אמסטרדם",
        "country": "Netherlands",
        "capacity": 17000,
        "categories": ["Floor", "Lower Ring", "Upper Ring", "Skybox"]
    },
    "Johan Cruijff Arena": {
        "name_en": "Johan Cruijff ArenA",
        "name_he": "יוהאן קרויף ארנה",
        "city_en": "Amsterdam",
        "city_he": "אמסטרדם",
        "country": "Netherlands",
        "capacity": 55500,
        "categories": ["Pitch", "Ring 1", "Ring 2", "Skybox"]
    },
    "Palau Sant Jordi Barcelona": {
        "name_en": "Palau Sant Jordi",
        "name_he": "פאלאו סנט ג'ורדי ברצלונה",
        "city_en": "Barcelona",
        "city_he": "ברצלונה",
        "country": "Spain",
        "capacity": 18000,
        "categories": ["Pista", "Grada Baja", "Grada Alta", "Palco"]
    },
    "WiZink Center Madrid": {
        "name_en": "WiZink Center",
        "name_he": "וויזינק סנטר מדריד",
        "city_en": "Madrid",
        "city_he": "מדריד",
        "country": "Spain",
        "capacity": 17453,
        "categories": ["Pista", "Tribuna Baja", "Tribuna Alta", "Palco VIP"]
    },
    "San Siro Milan": {
        "name_en": "San Siro Stadium",
        "name_he": "סן סירו מילאן",
        "city_en": "Milan",
        "city_he": "מילאן",
        "country": "Italy",
        "capacity": 80018,
        "categories": ["Prato", "Primo Anello", "Secondo Anello", "Terzo Anello"]
    },
    "Mediolanum Forum Milan": {
        "name_en": "Mediolanum Forum",
        "name_he": "מדיולנום פורום מילאן",
        "city_en": "Milan",
        "city_he": "מילאן",
        "country": "Italy",
        "capacity": 12700,
        "categories": ["Parterre", "Tribuna", "Gradinata", "VIP"]
    },
    "Puskas Arena Budapest": {
        "name_en": "Puskas Arena",
        "name_he": "פושקאש ארנה בודפשט",
        "city_en": "Budapest",
        "city_he": "בודפשט",
        "country": "Hungary",
        "capacity": 67215,
        "categories": ["Pitch", "Lower Tier", "Middle Tier", "Upper Tier"]
    },
    "O2 Arena Prague": {
        "name_en": "O2 Arena Prague",
        "name_he": "O2 ארנה פראג",
        "city_en": "Prague",
        "city_he": "פראג",
        "country": "Czech Republic",
        "capacity": 18000,
        "categories": ["Floor", "Lower Bowl", "Upper Bowl", "Skybox"]
    },
    "OAKA Athens": {
        "name_en": "Olympic Stadium Athens (OAKA)",
        "name_he": "האצטדיון האולימפי אתונה",
        "city_en": "Athens",
        "city_he": "אתונה",
        "country": "Greece",
        "capacity": 69618,
        "categories": ["Pitch", "Lower Tier", "Upper Tier", "VIP"]
    },
    "Krakow Arena": {
        "name_en": "Tauron Arena Krakow",
        "name_he": "טאורון ארנה קרקוב",
        "city_en": "Krakow",
        "city_he": "קרקוב",
        "country": "Poland",
        "capacity": 22000,
        "categories": ["Floor", "Lower Level", "Upper Level", "VIP Box"]
    }
}

SAMPLE_CONCERTS = [
    {"artist": "Metallica", "venue": "Puskas Arena Budapest", "date": "2026-06-11", "time": "20:00"},
    {"artist": "Metallica", "venue": "Puskas Arena Budapest", "date": "2026-06-13", "time": "20:00"},
    {"artist": "Metallica", "venue": "OAKA Athens", "date": "2026-05-09", "time": "20:00"},
    {"artist": "Metallica", "venue": "Olympiastadion Berlin", "date": "2026-05-30", "time": "20:00"},
    {"artist": "Andrea Bocelli", "venue": "O2 Arena Prague", "date": "2026-01-23", "time": "20:00"},
    {"artist": "Andrea Bocelli", "venue": "Ziggo Dome Amsterdam", "date": "2026-03-27", "time": "20:00"},
    {"artist": "Rod Stewart", "venue": "OAKA Athens", "date": "2025-12-13", "time": "21:00"},
    {"artist": "Andre Rieu", "venue": "Krakow Arena", "date": "2026-05-09", "time": "19:30"},
    {"artist": "Coldplay", "venue": "Wembley Stadium", "date": "2025-08-22", "time": "19:00"},
    {"artist": "Ed Sheeran", "venue": "San Siro Milan", "date": "2025-06-15", "time": "20:30"},
]

def get_all_artists():
    """Get list of all artists for dropdown"""
    return [{"name_en": k, "name_he": v["name_he"], "genre": v["genre"]} for k, v in ARTISTS.items()]

def get_artist_info(name_en):
    """Get artist details by English name"""
    return ARTISTS.get(name_en, {})

def get_artist_hebrew(name_en):
    """Get Hebrew name for artist"""
    artist = ARTISTS.get(name_en, {})
    return artist.get("name_he", name_en)

def get_all_venues():
    """Get list of all venues"""
    return [{"id": k, **v} for k, v in CONCERT_VENUES.items()]

def get_venue_info(venue_id):
    """Get venue details by ID"""
    return CONCERT_VENUES.get(venue_id, {})

def get_venues_by_city(city_en):
    """Get venues in a specific city"""
    return [{"id": k, **v} for k, v in CONCERT_VENUES.items() if v["city_en"] == city_en]

def get_concerts_by_artist(artist_name):
    """Get sample concerts for an artist"""
    return [c for c in SAMPLE_CONCERTS if c["artist"] == artist_name]

def get_venue_categories(venue_id):
    """Get seating categories for a venue"""
    venue = CONCERT_VENUES.get(venue_id, {})
    return venue.get("categories", ["General Admission"])

CITIES = {
    "London": "לונדון",
    "Paris": "פריז",
    "Berlin": "ברלין",
    "Amsterdam": "אמסטרדם",
    "Barcelona": "ברצלונה",
    "Madrid": "מדריד",
    "Milan": "מילאן",
    "Budapest": "בודפשט",
    "Prague": "פראג",
    "Athens": "אתונה",
    "Krakow": "קרקוב"
}

def get_city_hebrew(city_en):
    """Get Hebrew name for city"""
    return CITIES.get(city_en, city_en)

def get_all_cities():
    """Get all cities with concerts"""
    cities = set()
    for venue in CONCERT_VENUES.values():
        cities.add(venue["city_en"])
    return sorted(list(cities))

import os

CONCERT_VENUE_MAPS_DIR = os.path.join(os.path.dirname(__file__), 'attached_assets', 'concert_venue_maps')
CONCERT_DEFAULT_BG = os.path.join(os.path.dirname(__file__), 'assets', 'concert_bg.jpg')

def get_venue_map_path(venue_id, use_fallback=True):
    """
    Returns the path to the venue seating map image if available.
    Falls back to generic concert background if no specific map exists.
    
    Args:
        venue_id: The venue identifier (key from CONCERT_VENUES)
        use_fallback: If True, returns generic concert bg when no specific map exists
    
    Returns:
        str: Path to venue map image, generic background, or None
    """
    if not venue_id or venue_id not in CONCERT_VENUES:
        if use_fallback and os.path.exists(CONCERT_DEFAULT_BG):
            return CONCERT_DEFAULT_BG
        return None
    
    venue_filename = venue_id.replace(' ', '_').replace('-', '_') + '.png'
    specific_path = os.path.join(CONCERT_VENUE_MAPS_DIR, venue_filename)
    
    if os.path.exists(specific_path):
        return specific_path
    
    jpg_path = specific_path.replace('.png', '.jpg')
    if os.path.exists(jpg_path):
        return jpg_path
    
    if use_fallback and os.path.exists(CONCERT_DEFAULT_BG):
        return CONCERT_DEFAULT_BG
    
    return None

def get_concert_default_bg():
    """Returns path to default concert background if it exists"""
    if os.path.exists(CONCERT_DEFAULT_BG):
        return CONCERT_DEFAULT_BG
    return None
