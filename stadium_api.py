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
    מחזיר מידע על קבוצה לפי מזהה
    
    Args:
        team_identifier: יכול להיות:
            - team.id (לדוגמה: 'real_madrid')
            - שם בעברית (לדוגמה: 'ריאל מדריד')
            - שם באנגלית (לדוגמה: 'Real Madrid')
    
    Returns:
        dict: מידע על הקבוצה או None אם לא נמצאה
    """
    data = load_teams_data()
    identifier_lower = str(team_identifier).lower().strip()
    
    for team in data['teams']:
        if (team['id'] == identifier_lower or 
            team['name_en'].lower() == identifier_lower or 
            team['name_he'] == team_identifier or
            identifier_lower in team['name_en'].lower() or
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
