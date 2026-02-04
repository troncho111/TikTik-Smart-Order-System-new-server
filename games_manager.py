"""
Games Manager - Multiple Games Feature
Manages adding, editing, deleting multiple games/events in an order
"""

import streamlit as st
from datetime import datetime
import json


def init_games_list():
    """Initialize games_list in session_state if not present"""
    if 'games_list' not in st.session_state:
        st.session_state.games_list = []


def get_current_game_data():
    """
    Extracts current game/event data from session_state
    Returns a dict with all relevant fields
    """
    game_data = {
        'game_id': datetime.now().timestamp(),  # Unique ID
        'event_type': st.session_state.get('event_type_select', 'כדורגל'),
        
        # Football specific
        'league': st.session_state.get('football_league', ''),
        'home_team': st.session_state.get('home_team_hebrew', ''),
        'away_team': st.session_state.get('away_team_hebrew', ''),
        'home_team_data': st.session_state.get('selected_team_data', {}),
        'away_team_data': st.session_state.get('away_team_data', {}),
        
        # Concert specific
        'artist_name': st.session_state.get('selected_artist_name', ''),
        'artist_name_he': st.session_state.get('selected_artist_name_he', ''),
        
        # Common fields
        'venue': st.session_state.get('venue_name', ''),
        'city': st.session_state.get('city_name', ''),
        'country': st.session_state.get('country_name', ''),
        
        # Date/Time
        'event_date': None,
        'event_time': '',
        'event_date_str': '',
        'event_time_str': '',
        
        # Category & Tickets
        'ticket_category': st.session_state.get('ticket_category', ''),
        'worldcup_category': st.session_state.get('worldcup_category', ''),
        
        # Fixture data (from API)
        'fixture_data': st.session_state.get('fixture_data', {}),
        
        # Stadium/Venue details
        'stadium_map': st.session_state.get('worldcup_stadium_map', ''),
        'venue_address': st.session_state.get('venue_address', ''),
        
        # World Cup specific
        'worldcup_venue': st.session_state.get('worldcup_venue', ''),
        'worldcup_round': st.session_state.get('fixture_data', {}).get('round', ''),
    }
    
    # Extract date/time from fixture_data if available
    fixture_data = st.session_state.get('fixture_data', {})
    if fixture_data.get('date'):
        game_data['event_date_str'] = fixture_data['date']
        try:
            game_data['event_date'] = datetime.strptime(fixture_data['date'], '%Y-%m-%d')
        except:
            pass
    
    if fixture_data.get('time'):
        game_data['event_time_str'] = fixture_data['time']
    
    return game_data


def add_current_game_to_list():
    """
    Adds current game data to games_list
    Returns: (success: bool, message: str)
    """
    init_games_list()
    
    game_data = get_current_game_data()
    
    # Validation
    event_type = game_data['event_type']
    
    if event_type == 'כדורגל':
        if not game_data['home_team'] or not game_data['away_team']:
            return False, "⚠️ נא לבחור שתי קבוצות"
    elif event_type == 'הופעה':
        if not game_data['artist_name']:
            return False, "⚠️ נא לבחור אמן"
    
    if not game_data['venue']:
        return False, "⚠️ נא להזין מיקום האירוע"
    
    # Add to list
    st.session_state.games_list.append(game_data)
    
    # Generate success message
    if event_type == 'כדורגל':
        msg = f"✅ נוסף: {game_data['home_team']} vs {game_data['away_team']}"
    elif event_type == 'הופעה':
        msg = f"✅ נוסף: {game_data['artist_name_he'] or game_data['artist_name']}"
    else:
        msg = "✅ אירוע נוסף בהצלחה"
    
    return True, msg


def remove_game_from_list(game_id):
    """Remove a game from the list by its ID"""
    init_games_list()
    st.session_state.games_list = [
        g for g in st.session_state.games_list 
        if g.get('game_id') != game_id
    ]


def clear_current_game_fields():
    """Clear all game-related fields in session_state"""
    fields_to_clear = [
        'football_league', 'football_team1', 'football_team2',
        'home_team_hebrew', 'away_team_hebrew',
        'selected_team_data', 'away_team_data',
        'fixture_data', 'fixture_lookup_key',
        'selected_artist_name', 'selected_artist_name_he',
        'venue_name', 'city_name', 'country_name',
        'ticket_category', 'worldcup_category',
        'worldcup_venue', 'worldcup_stadium_map',
        'venue_address'
    ]
    
    for field in fields_to_clear:
        if field in st.session_state:
            if isinstance(st.session_state[field], dict):
                st.session_state[field] = {}
            else:
                st.session_state[field] = ''


def get_game_display_text(game):
    """
    Returns a readable display text for a game
    For use in lists/cards
    """
    event_type = game.get('event_type', '')
    
    if event_type == 'כדורגל':
        home = game.get('home_team', '')
        away = game.get('away_team', '')
        league = game.get('league', '')
        date_str = game.get('event_date_str', '')
        
        text = f"⚽ {home} נגד {away}"
        if league and league != "-- בחר ליגה --":
            text += f" | {league}"
        if date_str:
            text += f" | 📅 {date_str}"
        
        return text
    
    elif event_type == 'הופעה':
        artist = game.get('artist_name_he') or game.get('artist_name', '')
        venue = game.get('venue', '')
        city = game.get('city', '')
        date_str = game.get('event_date_str', '')
        
        text = f"🎤 {artist}"
        if venue:
            text += f" | {venue}"
        if city:
            text += f", {city}"
        if date_str:
            text += f" | 📅 {date_str}"
        
        return text
    
    else:
        return f"🎭 {event_type} | {game.get('venue', 'N/A')}"


def render_games_list():
    """
    Renders the list of added games with delete buttons
    Shows below the "Add Game" section
    """
    init_games_list()
    
    if not st.session_state.games_list:
        st.info("💡 **טרם נוספו משחקים/אירועים**\nלחץ על 'הוסף משחק' למעלה כדי להוסיף את המשחק הראשון")
        return
    
    st.markdown("---")
    st.markdown("### 📋 רשימת משחקים/אירועים שנבחרו")
    st.caption(f"סה\"כ {len(st.session_state.games_list)} אירועים")
    
    for idx, game in enumerate(st.session_state.games_list):
        game_id = game.get('game_id')
        display_text = get_game_display_text(game)
        
        col_text, col_btn = st.columns([4, 1])
        
        with col_text:
            st.markdown(f"**{idx + 1}.** {display_text}")
        
        with col_btn:
            if st.button("🗑️ מחק", key=f"delete_game_{game_id}", type="secondary"):
                remove_game_from_list(game_id)
                st.success("✅ האירוע נמחק")
                st.rerun()


def render_add_game_button():
    """
    Renders the "+ הוסף משחק" button
    Should be placed after the event selection section
    """
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("➕ **הוסף משחק/אירוע לרשימה**", key="add_game_btn", type="primary", use_container_width=True):
            success, message = add_current_game_to_list()
            
            if success:
                st.success(message)
                # Clear fields for next game
                clear_current_game_fields()
                st.rerun()
            else:
                st.error(message)
    
    st.caption("💡 לאחר בחירת המשחק/הופעה, לחץ כאן להוסיף לרשימה")


def get_games_summary_for_order():
    """
    Returns a summary dict of all games for saving to Order
    This will be JSON-serialized and stored in Order.games_data
    """
    init_games_list()
    
    summary = {
        'total_games': len(st.session_state.games_list),
        'games': []
    }
    
    for game in st.session_state.games_list:
        game_summary = {
            'event_type': game.get('event_type'),
            'home_team': game.get('home_team'),
            'away_team': game.get('away_team'),
            'artist_name': game.get('artist_name'),
            'artist_name_he': game.get('artist_name_he'),
            'venue': game.get('venue'),
            'city': game.get('city'),
            'country': game.get('country'),
            'event_date': game.get('event_date_str'),
            'event_time': game.get('event_time_str'),
            'league': game.get('league'),
            'category': game.get('ticket_category') or game.get('worldcup_category'),
            'display_text': get_game_display_text(game)
        }
        summary['games'].append(game_summary)
    
    return summary


def load_games_from_order_data(order_data):
    """
    Loads games from Order.games_data (JSON string) into session_state.games_list
    Used when editing an existing order or loading a template
    """
    if not order_data:
        return
    
    try:
        if isinstance(order_data, str):
            games_data = json.loads(order_data)
        else:
            games_data = order_data
        
        if games_data and games_data.get('games'):
            # Convert back to internal format
            loaded_games = []
            for g in games_data['games']:
                game = {
                    'game_id': datetime.now().timestamp(),  # Generate new ID
                    'event_type': g.get('event_type', ''),
                    'home_team': g.get('home_team', ''),
                    'away_team': g.get('away_team', ''),
                    'artist_name': g.get('artist_name', ''),
                    'artist_name_he': g.get('artist_name_he', ''),
                    'venue': g.get('venue', ''),
                    'city': g.get('city', ''),
                    'country': g.get('country', ''),
                    'event_date_str': g.get('event_date', ''),
                    'event_time_str': g.get('event_time', ''),
                    'league': g.get('league', ''),
                    'ticket_category': g.get('category', ''),
                }
                loaded_games.append(game)
            
            st.session_state.games_list = loaded_games
    except Exception as e:
        st.error(f"⚠️ שגיאה בטעינת משחקים: {e}")


def render_games_info_banner():
    """
    Renders an info banner at the top explaining the multiple games feature
    """
    st.info("""
    ℹ️ **משחקים/אירועים מרובים**
    
    תוכל להוסיף כמה שתרצה משחקים או הופעות להזמנה אחת:
    1. בחר משחק/הופעה מהשדות למטה
    2. לחץ על "➕ הוסף לרשימה"
    3. חזור על התהליך לכל משחק נוסף
    4. המשך למילוי שאר פרטי ההזמנה
    """)
