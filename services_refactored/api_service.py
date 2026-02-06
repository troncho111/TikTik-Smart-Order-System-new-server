import streamlit as st
import os
import json
from sports_api import LEAGUES, get_teams_by_league, get_hebrew_name, TEAM_HEBREW_NAMES
from stadium_api import get_team_info, get_team_map_path, get_all_teams
from concerts_service import search_artists, search_events_combined, get_popular_artists
from concerts_data import get_venue_map_path

def get_football_leagues():
    return ["-- בחר ליגה --"] + list(LEAGUES.keys())

def get_teams_for_league(league_name):
    if not league_name or league_name == "-- בחר ליגה --":
        return []
    english_league = LEAGUES.get(league_name, "") or league_name
    return get_teams_by_league(english_league)

def get_team_details(team_name):
    return get_team_info(team_name)

def get_stadium_map(team_name):
    return get_team_map_path(team_name)

def search_concert_artists(query):
    return search_artists(query)

def get_concert_events(artist_name, artist_id=''):
    return search_events_combined(artist_name, artist_id)

def get_worldcup_matches(json_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('matches', [])
    except:
        return []
