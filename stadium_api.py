"""
Stadium API - ניהול מפות אצטדיון לטופס הזמנות
מותאם ל-Streamlit
"""
import json
import os

MAPPING_FILE = 'teams_stadiums_mapping.json'
STADIUM_MAPS_DIR = 'stadium_maps'

def load_teams_data():
    """טוען את נתוני הקבוצות מקובץ JSON"""
    try:
        with open(MAPPING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'teams': []}
    except json.JSONDecodeError:
        return {'teams': []}

def _normalize_team_name(name):
    """Remove common prefixes/suffixes from team names for matching"""
    n = name.lower().strip()
    for prefix in ['fc ', 'cf ', 'afc ', 'rcd ', 'ac ', 'as ', 'cd ', 'ud ', 'rc ', 'ssc ', 'deportivo ']:
        if n.startswith(prefix):
            n = n[len(prefix):].strip()
    for suffix in [' fc', ' cf', ' afc', ' sc', ' ac', ' fk', ' de madrid', ' balompié', ' de fútbol']:
        if n.endswith(suffix):
            n = n[:-len(suffix)].strip()
    return n


def get_team_info(team_identifier):
    """
    מחזיר מידע על קבוצה לפי מזהה (תומך בשמות מלאים מ-OpenFootball כמו 'FC Barcelona')

    Args:
        team_identifier: יכול להיות:
            - team.id (לדוגמה: 'real_madrid')
            - שם בעברית (לדוגמה: 'ריאל מדריד')
            - שם באנגלית (לדוגמה: 'Real Madrid' או 'FC Barcelona')

    Returns:
        dict: מידע על הקבוצה או None אם לא נמצאה
    """
    data = load_teams_data()
    identifier_lower = str(team_identifier).lower().strip()
    normalized_id = _normalize_team_name(str(team_identifier))

    # Pass 1: Exact matches (id, full name, Hebrew name, normalized exact)
    for team in data['teams']:
        team_name_lower = team['name_en'].lower()
        team_normalized = _normalize_team_name(team['name_en'])

        if (team['id'] == identifier_lower or
            team_name_lower == identifier_lower or
            team['name_he'] == team_identifier or
            (team_normalized == normalized_id and normalized_id)):
            return team

    # Pass 2: Fuzzy partial match - only if one name fully contains the other
    # and the match is significant (>= 60% of the longer string)
    best_match = None
    best_score = 0
    for team in data['teams']:
        team_name_lower = team['name_en'].lower()
        team_normalized = _normalize_team_name(team['name_en'])

        match = False
        if identifier_lower in team_name_lower or team_name_lower in identifier_lower:
            match = True
        elif team['name_he'] in str(team_identifier):
            match = True

        if match:
            # Score by how close the match is (longer overlap = better)
            overlap = min(len(identifier_lower), len(team_name_lower))
            max_len = max(len(identifier_lower), len(team_name_lower))
            score = overlap / max_len if max_len > 0 else 0
            if score > best_score and score >= 0.5:
                best_score = score
                best_match = team

    return best_match

def get_all_teams():
    """מחזיר רשימה של כל הקבוצות"""
    data = load_teams_data()
    return data['teams']

def get_team_map_path(team_identifier):
    """
    מחזיר את נתיב התמונה של מפת האצטדיון
    
    Args:
        team_identifier: מזהה הקבוצה
    
    Returns:
        str: נתיב יחסי לקובץ התמונה או None
    """
    team = get_team_info(team_identifier)
    if team:
        path = os.path.join(STADIUM_MAPS_DIR, team['map_filename'])
        if os.path.exists(path):
            return path
    return None

def get_teams_for_selectbox():
    """
    מחזיר רשימה מעוצבת לתפריט נפתח של Streamlit
    
    Returns:
        list: רשימה של שמות קבוצות בעברית
    """
    teams = get_all_teams()
    return ["-- בחר קבוצה --"] + [team['name_he'] for team in teams]

def get_team_by_hebrew_name(name_he):
    """
    מחזיר מידע על קבוצה לפי שם בעברית
    """
    if not name_he or name_he == "-- בחר קבוצה --":
        return None
    
    data = load_teams_data()
    for team in data['teams']:
        if team['name_he'] == name_he:
            return team
    return None
