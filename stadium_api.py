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
    
    # Normalize identifier: remove common prefixes/suffixes
    normalized_id = identifier_lower
    for prefix in ['fc ', 'cf ', 'afc ', 'rcd ', 'ac ', 'as ', 'real ', 'cd ', 'ud ', 'rc ', 'deportivo ']:
        if normalized_id.startswith(prefix):
            normalized_id = normalized_id[len(prefix):].strip()
    for suffix in [' fc', ' cf', ' afc', ' sc', ' ac', ' fk', ' de madrid', ' balompié', ' de fútbol']:
        if normalized_id.endswith(suffix):
            normalized_id = normalized_id[:-len(suffix)].strip()
    
    for team in data['teams']:
        team_name_lower = team['name_en'].lower()
        team_normalized = team_name_lower
        for prefix in ['fc ', 'cf ', 'afc ', 'rcd ', 'ac ', 'as ', 'real ', 'cd ', 'ud ', 'rc ']:
            if team_normalized.startswith(prefix):
                team_normalized = team_normalized[len(prefix):].strip()
        for suffix in [' fc', ' cf', ' afc', ' sc', ' ac', ' fk']:
            if team_normalized.endswith(suffix):
                team_normalized = team_normalized[:-len(suffix)].strip()
        
        # Check: exact, normalized, or partial match
        if (team['id'] == identifier_lower or 
            team_name_lower == identifier_lower or 
            team['name_he'] == team_identifier or
            team_normalized == normalized_id or
            normalized_id in team_normalized or
            team_normalized in normalized_id or
            identifier_lower in team_name_lower or
            team['name_he'] in str(team_identifier)):
            return team
    
    return None

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
