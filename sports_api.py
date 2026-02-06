"""
Sports API Module
Fetches football team data from TheSportsDB
"""

import requests
import json
import os
from functools import lru_cache

LEAGUES = {
    "מונדיאל 2026": "FIFA World Cup 2026",
    "ליגת האלופות": "UEFA Champions League",
    "ליגה ספרדית": "Spanish La Liga",
    "פרמיירליג": "English Premier League",
    "סריה A": "Italian Serie A",
    "בונדסליגה": "German Bundesliga",
    "ליג 1": "French Ligue 1"
}

# Normalize league name: Hebrew or any variant -> English (used for API lookups)
def _normalize_league_name(league_name: str) -> str:
    if not league_name or not isinstance(league_name, str):
        return ""
    key = league_name.strip()
    if not key:
        return ""
    # Already English (value in LEAGUES)
    if key in LEAGUES.values():
        return key
    # Hebrew or display name (key in LEAGUES)
    if key in LEAGUES:
        return LEAGUES[key]
    # Case-insensitive match for English names
    key_lower = key.lower()
    for eng in LEAGUES.values():
        if eng.lower() == key_lower:
            return eng
    return key

LEAGUE_IDS = {
    "Spanish La Liga": 4335,
    "English Premier League": 4328,
    "Italian Serie A": 4332,
    "German Bundesliga": 4331,
    "French Ligue 1": 4334,
    "UEFA Champions League": 4480
}

# Fallback teams for Champions League (2024-25 season)
CHAMPIONS_LEAGUE_TEAMS = [
    {"name": "Real Madrid", "stadium": "Santiago Bernabeu", "stadium_location": "Madrid, Spain", "capacity": "81044"},
    {"name": "Barcelona", "stadium": "Estadi Olimpic Lluis Companys", "stadium_location": "Barcelona, Spain", "capacity": "55926"},
    {"name": "Manchester City", "stadium": "Etihad Stadium", "stadium_location": "Manchester, England", "capacity": "55017"},
    {"name": "Bayern Munich", "stadium": "Allianz Arena", "stadium_location": "Munich, Germany", "capacity": "75000"},
    {"name": "Paris Saint-Germain", "stadium": "Parc des Princes", "stadium_location": "Paris, France", "capacity": "47929"},
    {"name": "Liverpool", "stadium": "Anfield", "stadium_location": "Liverpool, England", "capacity": "61276"},
    {"name": "Inter Milan", "stadium": "San Siro", "stadium_location": "Milan, Italy", "capacity": "75923"},
    {"name": "AC Milan", "stadium": "San Siro", "stadium_location": "Milan, Italy", "capacity": "75923"},
    {"name": "Borussia Dortmund", "stadium": "Signal Iduna Park", "stadium_location": "Dortmund, Germany", "capacity": "81365"},
    {"name": "Juventus", "stadium": "Allianz Stadium", "stadium_location": "Turin, Italy", "capacity": "41507"},
    {"name": "Atletico Madrid", "stadium": "Civitas Metropolitano", "stadium_location": "Madrid, Spain", "capacity": "70460"},
    {"name": "Arsenal", "stadium": "Emirates Stadium", "stadium_location": "London, England", "capacity": "60704"},
    {"name": "Chelsea", "stadium": "Stamford Bridge", "stadium_location": "London, England", "capacity": "40834"},
    {"name": "Manchester United", "stadium": "Old Trafford", "stadium_location": "Manchester, England", "capacity": "74310"},
    {"name": "Napoli", "stadium": "Stadio Diego Armando Maradona", "stadium_location": "Naples, Italy", "capacity": "54726"},
    {"name": "Benfica", "stadium": "Estadio da Luz", "stadium_location": "Lisbon, Portugal", "capacity": "64642"},
    {"name": "Porto", "stadium": "Estadio do Dragao", "stadium_location": "Porto, Portugal", "capacity": "50033"},
    {"name": "Sporting CP", "stadium": "Estadio Jose Alvalade", "stadium_location": "Lisbon, Portugal", "capacity": "50095"},
    {"name": "Ajax", "stadium": "Johan Cruyff Arena", "stadium_location": "Amsterdam, Netherlands", "capacity": "55500"},
    {"name": "PSV Eindhoven", "stadium": "Philips Stadion", "stadium_location": "Eindhoven, Netherlands", "capacity": "35000"},
    {"name": "Feyenoord", "stadium": "De Kuip", "stadium_location": "Rotterdam, Netherlands", "capacity": "51117"},
    {"name": "RB Leipzig", "stadium": "Red Bull Arena", "stadium_location": "Leipzig, Germany", "capacity": "47069"},
    {"name": "Bayer Leverkusen", "stadium": "BayArena", "stadium_location": "Leverkusen, Germany", "capacity": "30210"},
    {"name": "Atalanta", "stadium": "Gewiss Stadium", "stadium_location": "Bergamo, Italy", "capacity": "24642"},
    {"name": "Monaco", "stadium": "Stade Louis II", "stadium_location": "Monaco", "capacity": "18523"},
    {"name": "Lille", "stadium": "Stade Pierre-Mauroy", "stadium_location": "Lille, France", "capacity": "50157"},
    {"name": "Celtic", "stadium": "Celtic Park", "stadium_location": "Glasgow, Scotland", "capacity": "60411"},
    {"name": "Rangers", "stadium": "Ibrox Stadium", "stadium_location": "Glasgow, Scotland", "capacity": "50817"},
    {"name": "Club Brugge", "stadium": "Jan Breydelstadion", "stadium_location": "Bruges, Belgium", "capacity": "29042"},
    {"name": "Shakhtar Donetsk", "stadium": "Arena Lviv", "stadium_location": "Lviv, Ukraine", "capacity": "34915"},
    {"name": "Dinamo Zagreb", "stadium": "Stadion Maksimir", "stadium_location": "Zagreb, Croatia", "capacity": "35123"},
    {"name": "Red Star Belgrade", "stadium": "Rajko Mitic Stadium", "stadium_location": "Belgrade, Serbia", "capacity": "55538"},
    {"name": "Salzburg", "stadium": "Red Bull Arena Salzburg", "stadium_location": "Salzburg, Austria", "capacity": "30188"},
    {"name": "Young Boys", "stadium": "Stade de Suisse", "stadium_location": "Bern, Switzerland", "capacity": "31983"},
    {"name": "Copenhagen", "stadium": "Parken Stadium", "stadium_location": "Copenhagen, Denmark", "capacity": "38065"},
    {"name": "Bologna", "stadium": "Stadio Renato Dall'Ara", "stadium_location": "Bologna, Italy", "capacity": "38279"},
    {"name": "Girona", "stadium": "Estadi Montilivi", "stadium_location": "Girona, Spain", "capacity": "14286"},
    {"name": "Aston Villa", "stadium": "Villa Park", "stadium_location": "Birmingham, England", "capacity": "42640"},
    {"name": "Brest", "stadium": "Stade Francis-Le Ble", "stadium_location": "Brest, France", "capacity": "15220"},
    {"name": "Stuttgart", "stadium": "MHPArena", "stadium_location": "Stuttgart, Germany", "capacity": "60449"},
    {"name": "Sparta Prague", "stadium": "Letna Stadium", "stadium_location": "Prague, Czech Republic", "capacity": "19370"},
    {"name": "Slovan Bratislava", "stadium": "Tehelne pole", "stadium_location": "Bratislava, Slovakia", "capacity": "22500"},
    {"name": "Sturm Graz", "stadium": "Merkur Arena", "stadium_location": "Graz, Austria", "capacity": "16364"},
]

OPENFOOTBALL_URLS = {
    "Spanish La Liga": "https://raw.githubusercontent.com/openfootball/football.json/master/2025-26/es.1.json",
    "English Premier League": "https://raw.githubusercontent.com/openfootball/football.json/master/2025-26/en.1.json",
    "Italian Serie A": "https://raw.githubusercontent.com/openfootball/football.json/master/2025-26/it.1.json",
    "German Bundesliga": "https://raw.githubusercontent.com/openfootball/football.json/master/2025-26/de.1.json",
    "French Ligue 1": "https://raw.githubusercontent.com/openfootball/football.json/master/2025-26/fr.1.json"
}

# Champions League 2026 fixtures
CHAMPIONS_LEAGUE_FIXTURES = [
    {"date": "2026-02-17", "time": "20:45", "home_team": "Galatasaray", "away_team": "Juventus", "round": "Champions League", "venue": "Rams Park", "city": "Istanbul", "country": "Turkey"},
    {"date": "2026-02-17", "time": "21:00", "home_team": "Benfica", "away_team": "Real Madrid", "round": "Champions League", "venue": "Estadio da Luz", "city": "Lisbon", "country": "Portugal"},
    {"date": "2026-02-17", "time": "21:00", "home_team": "AS Monaco", "away_team": "Paris Saint-Germain", "round": "Champions League", "venue": "Louis II Stadium", "city": "Fontvieille", "country": "Monaco"},
    {"date": "2026-02-17", "time": "21:00", "home_team": "Borussia Dortmund", "away_team": "Atalanta", "round": "Champions League", "venue": "Signal Iduna Park", "city": "Dortmund", "country": "Germany"},
    {"date": "2026-02-18", "time": "22:00", "home_team": "Olympiacos", "away_team": "Bayer Leverkusen", "round": "Champions League", "venue": "Georgios Karaiskakis", "city": "Piraeus", "country": "Greece"},
    {"date": "2026-02-24", "time": "18:45", "home_team": "Atletico Madrid", "away_team": "Club Brugge", "round": "Champions League", "venue": "Estadio Metropolitano", "city": "Madrid", "country": "Spain"},
    {"date": "2026-02-24", "time": "20:00", "home_team": "Newcastle United", "away_team": "Qarabag FK", "round": "Champions League", "venue": "St James Park", "city": "Newcastle Upon Tyne", "country": "United Kingdom"},
    {"date": "2026-02-24", "time": "21:00", "home_team": "Inter Milan", "away_team": "Bodo/Glimt", "round": "Champions League", "venue": "San Siro", "city": "Milan", "country": "Italy"},
    {"date": "2026-02-24", "time": "21:00", "home_team": "Bayer Leverkusen", "away_team": "Olympiacos", "round": "Champions League", "venue": "BayArena", "city": "Leverkusen", "country": "Germany"},
    {"date": "2026-02-25", "time": "18:45", "home_team": "Atalanta", "away_team": "Borussia Dortmund", "round": "Champions League", "venue": "Atleti Azzurri d Italia", "city": "Bergamo", "country": "Italy"},
    {"date": "2026-02-25", "time": "21:00", "home_team": "Real Madrid", "away_team": "Benfica", "round": "Champions League", "venue": "Santiago Bernabeu", "city": "Madrid", "country": "Spain"},
    {"date": "2026-02-25", "time": "21:00", "home_team": "Juventus", "away_team": "Galatasaray", "round": "Champions League", "venue": "Juventus Arena", "city": "Torino", "country": "Italy"},
    {"date": "2026-02-25", "time": "21:00", "home_team": "Paris Saint-Germain", "away_team": "AS Monaco", "round": "Champions League", "venue": "Parc des Princes", "city": "Paris", "country": "France"},
]

TEAM_HEBREW_NAMES = {
    # La Liga (Spain) - including OpenFootball full names
    "ברצלונה": "Barcelona",
    "ריאל מדריד": "Real Madrid",
    "אתלטיקו מדריד": "Atletico Madrid",
    "סביליה": "Sevilla",
    "ולנסיה": "Valencia",
    "ריאל בטיס": "Real Betis",
    "ריאל סוסיאדד": "Real Sociedad",
    "אתלטיק בילבאו": "Athletic Bilbao",
    "אתלטיק קלאב": "Athletic Club",
    "ויאריאל": "Villarreal",
    "אוסאסונה": "Osasuna",
    "לגאנס": "Leganes",
    "אלאבס": "Alaves",
    "חטאפה": "Getafe",
    "ג'ירונה": "Girona",
    "סלטה ויגו": "Celta Vigo",
    "אספניול": "Espanyol",
    "מיורקה": "Mallorca",
    "ראיו ואייקאנו": "Rayo Vallecano",
    "ויאדוליד": "Valladolid",
    "לאס פלמאס": "Las Palmas",
    "לבנטה": "Levante",
    "אוביידו": "Oviedo",
    "אלצ'ה": "Elche",
    
    # Premier League (England)
    "מנצ'סטר יונייטד": "Manchester United",
    "מנצ'סטר סיטי": "Manchester City",
    "ליברפול": "Liverpool",
    "צ'לסי": "Chelsea",
    "ארסנל": "Arsenal",
    "טוטנהאם": "Tottenham",
    "ניוקאסל": "Newcastle",
    "אסטון וילה": "Aston Villa",
    "בורנמות'": "Bournemouth",
    "ברנטפורד": "Brentford",
    "ברייטון": "Brighton",
    "קריסטל פאלאס": "Crystal Palace",
    "אברטון": "Everton",
    "פולהאם": "Fulham",
    "איפסוויץ'": "Ipswich",
    "לסטר": "Leicester",
    "נוטינגהאם פורסט": "Nottingham Forest",
    "סאות'המפטון": "Southampton",
    "ווסטהאם": "West Ham",
    "וולבס": "Wolves",
    
    # Serie A (Italy)
    "יובנטוס": "Juventus",
    "מילאן": "AC Milan",
    "אינטר מילאן": "Inter Milan",
    "אינטר": "Inter",
    "נאפולי": "Napoli",
    "רומא": "Roma",
    "לאציו": "Lazio",
    "אטאלנטה": "Atalanta",
    "פיורנטינה": "Fiorentina",
    "מונזה": "Monza",
    "בולוניה": "Bologna",
    "קליארי": "Cagliari",
    "קומו": "Como",
    "אמפולי": "Empoli",
    "ג'נואה": "Genoa",
    "ורונה": "Verona",
    "פארמה": "Parma",
    "טורינו": "Torino",
    "לצ'ה": "Lecce",
    "אודינזה": "Udinese",
    "ונציה": "Venezia",
    
    # Bundesliga (Germany)
    "באיירן מינכן": "Bayern Munich",
    "באיירן": "Bayern",
    "דורטמונד": "Borussia Dortmund",
    "לייפציג": "RB Leipzig",
    "לברקוזן": "Bayer Leverkusen",
    "היידנהיים": "Heidenheim",
    "אוניון ברלין": "Union Berlin",
    "מיינץ": "Mainz",
    "גלאדבאך": "Gladbach",
    "פרנקפורט": "Frankfurt",
    "אוגסבורג": "Augsburg",
    "סנט פאולי": "St Pauli",
    "הולשטיין קיל": "Holstein Kiel",
    "פרייבורג": "Freiburg",
    "ורדר ברמן": "Werder Bremen",
    "הופנהיים": "Hoffenheim",
    "שטוטגרט": "Stuttgart",
    "בוכום": "Bochum",
    "וולפסבורג": "Wolfsburg",
    
    # Ligue 1 (France)
    "פריז סן ז'רמן": "Paris Saint Germain",
    "פ.ס.ז'": "PSG",
    "מרסיי": "Marseille",
    "ליון": "Lyon",
    "מונקו": "Monaco",
    "אוקסר": "Auxerre",
    "סנט אטיין": "Saint-Etienne",
    "אנז'ה": "Angers",
    "נאנט": "Nantes",
    "לה האבר": "Le Havre",
    "ליל": "Lille",
    "מונפלייה": "Montpellier",
    "ניס": "Nice",
    "סטרסבורג": "Strasbourg",
    "לאנס": "Lens",
    "ברסט": "Brest",
    "רן": "Rennes",
    "ריימס": "Reims",
    "טולוז": "Toulouse",
    
    # World Cup 2026 National Teams
    "מקסיקו": "Mexico",
    "ארה\"ב": "USA",
    "קנדה": "Canada",
    "ברזיל": "Brazil",
    "ארגנטינה": "Argentina",
    "גרמניה": "Germany",
    "צרפת": "France",
    "ספרד": "Spain",
    "אנגליה": "England",
    "פורטוגל": "Portugal",
    "הולנד": "Netherlands",
    "בלגיה": "Belgium",
    "קרואטיה": "Croatia",
    "מרוקו": "Morocco",
    "יפן": "Japan",
    "קוריאה": "Korea Republic",
    "דרום קוריאה": "Korea Republic",
    "אוסטרליה": "Australia",
    "סעודיה": "Saudi Arabia",
    "ערב הסעודית": "Saudi Arabia",
    "קטאר": "Qatar",
    "איראן": "Iran",
    "מצרים": "Egypt",
    "אלג'יריה": "Algeria",
    "סנגל": "Senegal",
    "גאנה": "Ghana",
    "חוף השנהב": "Cote d'Ivoire",
    "קולומביה": "Colombia",
    "אורוגוואי": "Uruguay",
    "אקוודור": "Ecuador",
    "פרגוואי": "Paraguay",
    "שוויץ": "Switzerland",
    "אוסטריה": "Austria",
    "נורבגיה": "Norway",
    "סקוטלנד": "Scotland",
    "פנמה": "Panama",
    "האיטי": "Haiti",
    "דרום אפריקה": "South Africa",
    "טוניסיה": "Tunisia",
    "ניו זילנד": "New Zealand",
    "ירדן": "Jordan",
    "אוזבקיסטן": "Uzbekistan",
    "קאבו ורדה": "Cabo Verde",
    "קוראסאו": "Curacao",
}

def get_hebrew_name(english_name: str) -> str:
    """Get Hebrew name for a team (with smart matching for OpenFootball names like 'FC Barcelona')"""
    if not english_name:
        return english_name
    
    # Exact match first
    for heb, eng in TEAM_HEBREW_NAMES.items():
        if eng.lower() == english_name.lower():
            return heb
    
    # Normalize: remove common prefixes/suffixes for matching
    normalized = english_name.lower().strip()
    for prefix in ['fc ', 'cf ', 'afc ', 'rcd ', 'ac ', 'as ', 'real ', 'cd ', 'ud ', 'rc ']:
        if normalized.startswith(prefix):
            normalized = normalized[len(prefix):].strip()
    for suffix in [' fc', ' cf', ' afc', ' sc', ' ac', ' fk', ' de madrid', ' balompié', ' de fútbol']:
        if normalized.endswith(suffix):
            normalized = normalized[:-len(suffix)].strip()
    
    # Try matching normalized name
    for heb, eng in TEAM_HEBREW_NAMES.items():
        eng_normalized = eng.lower().strip()
        for prefix in ['fc ', 'cf ', 'afc ', 'rcd ', 'ac ', 'as ', 'real ', 'cd ', 'ud ', 'rc ']:
            if eng_normalized.startswith(prefix):
                eng_normalized = eng_normalized[len(prefix):].strip()
        for suffix in [' fc', ' cf', ' afc', ' sc', ' ac', ' fk']:
            if eng_normalized.endswith(suffix):
                eng_normalized = eng_normalized[:-len(suffix)].strip()
        if eng_normalized == normalized or normalized in eng_normalized or eng_normalized in normalized:
            return heb
    
    return english_name

def get_english_name(hebrew_name: str) -> str:
    """Get English name for a Hebrew team name"""
    return TEAM_HEBREW_NAMES.get(hebrew_name, hebrew_name)

def get_teams_by_league(league_name: str) -> list:
    """Get all teams in a league (Champions League uses hardcoded list). Accepts Hebrew or English league name."""
    league_name = _normalize_league_name(league_name)
    if not league_name:
        return []
    return _get_teams_by_league_cached(league_name)


@lru_cache(maxsize=20)
def _get_teams_by_league_cached(league_name: str) -> list:
    """Internal: get teams by English league name (cached)."""
    # Use hardcoded Champions League teams for reliability (return copy to avoid mutation)
    if league_name == "UEFA Champions League":
        return list(CHAMPIONS_LEAGUE_TEAMS)
    
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/3/search_all_teams.php?l={league_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        teams = data.get('teams', []) or []
        return [{
            'name': t.get('strTeam', ''),
            'stadium': t.get('strStadium', ''),
            'stadium_location': t.get('strStadiumLocation', ''),
            'badge': t.get('strTeamBadge', ''),
            'capacity': t.get('intStadiumCapacity', '')
        } for t in teams if t.get('strTeam')]
    except Exception as e:
        print(f"Error fetching teams: {e}")
        return []


def search_team(team_name: str) -> dict:
    """Search for a team by name"""
    try:
        url = f"https://www.thesportsdb.com/api/v1/json/3/searchteams.php?t={team_name}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        teams = data.get('teams', []) or []
        if teams:
            t = teams[0]
            return {
                'name': t.get('strTeam', ''),
                'stadium': t.get('strStadium', ''),
                'stadium_location': t.get('strStadiumLocation', ''),
                'badge': t.get('strTeamBadge', ''),
                'capacity': t.get('intStadiumCapacity', '')
            }
        return {}
    except Exception as e:
        print(f"Error searching team: {e}")
        return {}


def get_all_popular_teams() -> list:
    """Get teams from all major leagues"""
    all_teams = []
    for hebrew_name, english_name in LEAGUES.items():
        teams = get_teams_by_league(english_name)
        for team in teams:
            team['league'] = hebrew_name
        all_teams.extend(teams)
    return all_teams


def get_season_fixtures(league_name: str, season: str = "2024-2025") -> list:
    """Get all fixtures for a league season. Accepts Hebrew or English league name."""
    league_name = _normalize_league_name(league_name)
    if not league_name:
        return []
    return _get_season_fixtures_cached(league_name, season)


@lru_cache(maxsize=32)
def _get_season_fixtures_cached(league_name: str, season: str) -> list:
    """Internal: get fixtures by English league name (cached)."""
    try:
        if league_name == "FIFA World Cup 2026":
            local_file = os.path.join(os.path.dirname(__file__), "worldcup2026.json")
            if os.path.exists(local_file):
                with open(local_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                matches = data.get('matches', []) or []
                return [{
                    'id': str(i),
                    'home_team': m.get('team1', ''),
                    'away_team': m.get('team2', ''),
                    'date': m.get('date', ''),
                    'time': m.get('time', ''),
                    'round': m.get('round', ''),
                    'venue': m.get('venue', '')
                } for i, m in enumerate(matches) if m.get('team1')]
            return []
        
        # Use hardcoded fixtures for Champions League only (others use OpenFootball API)
        if league_name == "UEFA Champions League":
            return list(CHAMPIONS_LEAGUE_FIXTURES)
        
        # Get full season fixtures from OpenFootball API
        url = OPENFOOTBALL_URLS.get(league_name)
        if not url:
            return []
        
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        matches = data.get('matches', []) or []
        if not matches and data.get('rounds'):
            for r in data.get('rounds', []):
                matches.extend(r.get('matches', []) or [])
        out = []
        for i, m in enumerate(matches):
            t1 = m.get('team1')
            t2 = m.get('team2')
            if isinstance(t1, dict):
                t1 = t1.get('name', '')
            if isinstance(t2, dict):
                t2 = t2.get('name', '')
            if not t1 and not t2:
                continue
            out.append({
                'id': str(i),
                'home_team': t1 or '',
                'away_team': t2 or '',
                'date': m.get('date', ''),
                'time': m.get('time', ''),
                'round': m.get('round', '')
            })
        return out
    except Exception as e:
        print(f"Error fetching fixtures: {e}")
        return []


def normalize_team_name(name: str) -> str:
    """Normalize team name for matching"""
    name = name.lower().strip()
    for prefix in ['fc ', 'cf ', 'afc ', 'rcd ', 'real ', 'ac ', 'as ']:
        if name.startswith(prefix):
            name = name[len(prefix):]
    for suffix in [' fc', ' cf', ' afc', ' sc', ' ac', ' fk']:
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return name.strip()


TEAM_EXACT_NAMES = {
    # La Liga (Spain)
    'barcelona': 'fc barcelona',
    'real madrid': 'real madrid cf',
    'atletico madrid': 'club atlético de madrid',
    'athletic bilbao': 'athletic club',
    'real betis': 'real betis balompié',
    'real sociedad': 'real sociedad de fútbol',
    'sevilla': 'sevilla fc',
    'valencia': 'valencia cf',
    'villarreal': 'villarreal cf',
    'osasuna': 'ca osasuna',
    'leganes': 'cd leganés',
    'alaves': 'deportivo alavés',
    'getafe': 'getafe cf',
    'girona': 'girona fc',
    'celta vigo': 'rc celta de vigo',
    'espanyol': 'rcd espanyol de barcelona',
    'mallorca': 'rcd mallorca',
    'rayo vallecano': 'rayo vallecano de madrid',
    'valladolid': 'real valladolid cf',
    'las palmas': 'ud las palmas',
    
    # Premier League (England)
    'manchester united': 'manchester united fc',
    'manchester city': 'manchester city fc',
    'liverpool': 'liverpool fc',
    'chelsea': 'chelsea fc',
    'arsenal': 'arsenal fc',
    'tottenham': 'tottenham hotspur fc',
    'newcastle': 'newcastle united fc',
    'aston villa': 'aston villa fc',
    'bournemouth': 'afc bournemouth',
    'brentford': 'brentford fc',
    'brighton': 'brighton & hove albion fc',
    'crystal palace': 'crystal palace fc',
    'everton': 'everton fc',
    'fulham': 'fulham fc',
    'ipswich': 'ipswich town fc',
    'leicester': 'leicester city fc',
    'nottingham forest': 'nottingham forest fc',
    'southampton': 'southampton fc',
    'west ham': 'west ham united fc',
    'wolves': 'wolverhampton wanderers fc',
    'wolverhampton': 'wolverhampton wanderers fc',
    
    # Serie A (Italy)
    'juventus': 'juventus fc',
    'inter milan': 'fc internazionale milano',
    'inter': 'fc internazionale milano',
    'ac milan': 'ac milan',
    'milan': 'ac milan',
    'napoli': 'ssc napoli',
    'roma': 'as roma',
    'lazio': 'ss lazio',
    'atalanta': 'atalanta bc',
    'fiorentina': 'acf fiorentina',
    'monza': 'ac monza',
    'bologna': 'bologna fc 1909',
    'cagliari': 'cagliari calcio',
    'como': 'como 1907',
    'empoli': 'empoli fc',
    'genoa': 'genoa cfc',
    'verona': 'hellas verona fc',
    'parma': 'parma calcio 1913',
    'torino': 'torino fc',
    'lecce': 'us lecce',
    'udinese': 'udinese calcio',
    'venezia': 'venezia fc',
    
    # Bundesliga (Germany)
    'bayern munich': 'fc bayern münchen',
    'bayern': 'fc bayern münchen',
    'borussia dortmund': 'borussia dortmund',
    'dortmund': 'borussia dortmund',
    'bayer leverkusen': 'bayer 04 leverkusen',
    'leverkusen': 'bayer 04 leverkusen',
    'rb leipzig': 'rb leipzig',
    'leipzig': 'rb leipzig',
    'heidenheim': '1. fc heidenheim 1846',
    'union berlin': '1. fc union berlin',
    'mainz': '1. fsv mainz 05',
    'gladbach': 'borussia mönchengladbach',
    'monchengladbach': 'borussia mönchengladbach',
    'eintracht frankfurt': 'eintracht frankfurt',
    'frankfurt': 'eintracht frankfurt',
    'augsburg': 'fc augsburg',
    'st pauli': 'fc st. pauli 1910',
    'holstein kiel': 'holstein kiel',
    'kiel': 'holstein kiel',
    'freiburg': 'sc freiburg',
    'werder bremen': 'sv werder bremen',
    'bremen': 'sv werder bremen',
    'hoffenheim': 'tsg 1899 hoffenheim',
    'stuttgart': 'vfb stuttgart',
    'bochum': 'vfl bochum 1848',
    'wolfsburg': 'vfl wolfsburg',
    
    # Ligue 1 (France)
    'psg': 'paris saint-germain fc',
    'paris saint germain': 'paris saint-germain fc',
    'marseille': 'olympique de marseille',
    'lyon': 'olympique lyonnais',
    'auxerre': 'aj auxerre',
    'monaco': 'as monaco fc',
    'saint-etienne': 'as saint-étienne',
    'angers': 'angers sco',
    'nantes': 'fc nantes',
    'le havre': 'le havre ac',
    'lille': 'lille osc',
    'montpellier': 'montpellier hsc',
    'nice': 'ogc nice',
    'strasbourg': 'rc strasbourg alsace',
    'lens': 'racing club de lens',
    'brest': 'stade brestois 29',
    'rennes': 'stade rennais fc 1901',
    'reims': 'stade de reims',
    'toulouse': 'toulouse fc',
    
    # World Cup 2026 National Teams
    'ivory coast': "cote d'ivoire",
    'south korea': 'korea republic',
    'korea': 'korea republic',
}


def teams_match(search_name: str, fixture_name: str) -> bool:
    """Check if team names match using exact name mappings"""
    search_lower = search_name.lower().strip()
    fix_lower = fixture_name.lower().strip()
    
    if search_lower == fix_lower:
        return True
    
    expected_name = TEAM_EXACT_NAMES.get(search_lower)
    if expected_name:
        return fix_lower == expected_name
    
    return False


def find_fixture(home_team: str, away_team: str, league_name: str, season: str = "2024-2025") -> dict:
    """Find a specific fixture by home and away team"""
    fixtures = get_season_fixtures(league_name, season)
    
    for fixture in fixtures:
        home_match = teams_match(home_team, fixture['home_team'])
        away_match = teams_match(away_team, fixture['away_team'])
        
        if home_match and away_match:
            if fixture.get('date') and fixture.get('time'):
                return fixture
    
    for fixture in fixtures:
        home_match = teams_match(home_team, fixture['home_team'])
        away_match = teams_match(away_team, fixture['away_team'])
        
        if home_match and away_match:
            return fixture
    
    return {}
