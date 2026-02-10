"""
New Order Main Page - TikTik Smart Order System
עמוד יצירת הזמנה חדשה - פונקציה ראשית
"""

import streamlit as st
import os
import json
from datetime import datetime, timedelta
from PIL import Image
import io
import random
from models import get_db, PackageTemplate, EventType, generate_order_number
from services.pdf_service import generate_pdf
from services.order_service import save_order_to_db
from services.concert_service import (
    get_saved_concerts, save_concert_to_favorites,
    get_saved_artists, save_artist_to_favorites
)
from ui_helpers import get_random_atmosphere_image
from passport_ocr import extract_passport_data
from hotel_resolver import resolve_hotel_safe
from airports import get_airport_options, get_airport_code, format_airport_display
from flight_ocr import extract_flight_data
from airline_codes import get_airline_from_flight
from streamlit_paste_button import paste_image_button
from stadium_api import get_team_info, get_team_map_path, get_all_teams
from concerts_service import fetch_venue_map_from_ticketmaster, is_ticketmaster_url
from .helpers import show_product_selection, show_event_selection, show_selection_summary

# Project paths
_APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORLDCUP_JSON_PATH = os.path.join(_APP_DIR, "worldcup2026.json")
WORLDCUP_STADIUMS_JSON_PATH = os.path.join(_APP_DIR, "worldcup_stadiums_mapping.json")

def page_new_order():
    """New order page with stepped UI"""
    render_header()
    
    # Initialize UI step
    if 'ui_step' not in st.session_state:
        st.session_state['ui_step'] = 1
    
    # Initialize other session state
    if 'passengers' not in st.session_state:
        st.session_state.passengers = []
    if 'order_generated' not in st.session_state:
        st.session_state.order_generated = False
    if 'random_data' not in st.session_state:
        st.session_state.random_data = None

    # Load proposal data into form when coming from "ערוך" in הצעות ללקוח
    load_proposal = st.session_state.pop('load_proposal_data', None)
    if load_proposal and isinstance(load_proposal, dict):
        flights_list = load_proposal.get('flights') or []
        outbound = next((f for f in flights_list if f.get('direction') == 'הלוך'), {})
        ret = next((f for f in flights_list if f.get('direction') == 'חזור'), {})
        st.session_state.flights_data = {
            'outbound': {
                'from': outbound.get('from', 'TLV'),
                'to': outbound.get('to', ''),
                'date': outbound.get('date', ''),
                'time': outbound.get('time', ''),
                'flight_no': outbound.get('flight_no', ''),
                'airline': outbound.get('airline', '')
            },
            'return': {
                'from': ret.get('from', ''),
                'to': ret.get('to', 'TLV'),
                'date': ret.get('date', ''),
                'time': ret.get('time', ''),
                'flight_no': ret.get('flight_no', ''),
                'airline': ret.get('airline', '')
            }
        }
        st.session_state.random_data = {
            'customer_name': load_proposal.get('customer_name', ''),
            'customer_id': load_proposal.get('customer_id', ''),
            'customer_phone': load_proposal.get('customer_phone', ''),
            'customer_email': load_proposal.get('customer_email', ''),
            'product_type': 'package' if load_proposal.get('product_type') == 'package' else 'tickets',
            'event_name': load_proposal.get('event_name', ''),
            'event_type': load_proposal.get('event_type', 'כדורגל'),
            'event_date': load_proposal.get('event_date', ''),
            'event_time': load_proposal.get('event_time', ''),
            'venue': load_proposal.get('venue', ''),
            'ticket_description': load_proposal.get('ticket_description', ''),
            'category': load_proposal.get('category', ''),
            'num_tickets': int(load_proposal.get('num_tickets', 0)) or 2,
            'price_euro': float(load_proposal.get('price_per_ticket', 0)) or 330,
            'hotel_name': load_proposal.get('hotel_name', ''),
            'hotel_nights': int(load_proposal.get('hotel_nights', 0)) or 3,
            'hotel_stars': load_proposal.get('hotel_stars', ''),
            'hotel_meals': load_proposal.get('hotel_meals', 'ארוחת בוקר'),
            'outbound_from': outbound.get('from', 'TLV'),
            'outbound_to': outbound.get('to', ''),
            'outbound_date': outbound.get('date', ''),
            'outbound_time': outbound.get('time', ''),
            'outbound_flight': outbound.get('flight_no', ''),
            'outbound_airline': outbound.get('airline', ''),
            'return_from': ret.get('from', ''),
            'return_to': ret.get('to', 'TLV'),
            'return_date': ret.get('date', ''),
            'return_time': ret.get('time', ''),
            'return_flight': ret.get('flight_no', ''),
            'return_airline': ret.get('airline', ''),
            'transfers': bool(load_proposal.get('transfers', False)),
            'bag_trolley': bool(load_proposal.get('bag_trolley', False)),
        }
        saved_games_raw = load_proposal.get('saved_games') or []
        saved_games = []
        for game in saved_games_raw:
            g = dict(game)
            if not g.get('stadium_map_path') and (g.get('worldcup_stadium_map') or g.get('league_stadium_map_path')):
                g['stadium_map_path'] = g.get('worldcup_stadium_map') or g.get('league_stadium_map_path')
            if not g.get('stadium_map_path') and g.get('worldcup_venue'):
                try:
                    venue_name = (g.get('worldcup_venue') or '').split(',')[0].strip()
                    if venue_name and os.path.exists(WORLDCUP_STADIUMS_JSON_PATH):
                        with open(WORLDCUP_STADIUMS_JSON_PATH, 'r', encoding='utf-8') as f:
                            wc_stadiums = json.load(f)
                        stadium_info = (wc_stadiums.get('stadiums') or {}).get(venue_name, {})
                        if stadium_info.get('map_file'):
                            map_file = stadium_info['map_file']
                            base = os.path.dirname(os.path.abspath(__file__))
                            full_path = os.path.join(base, map_file)
                            if os.path.exists(full_path):
                                g['stadium_map_path'] = full_path
                            elif os.path.exists(map_file):
                                g['stadium_map_path'] = map_file
                except Exception:
                    pass
            saved_games.append(g)
        st.session_state.saved_games = saved_games
        if saved_games and not st.session_state.get('football_league'):
            first = saved_games[0]
            if first.get('worldcup_venue') or first.get('worldcup_stadium_map') or (first.get('fixture_data') and isinstance(first.get('fixture_data'), dict)):
                st.session_state['football_league'] = "מונדיאל 2026"
        passengers = load_proposal.get('passengers') or []
        if isinstance(passengers, str):
            try:
                passengers = json.loads(passengers)
            except Exception:
                passengers = []
        # Form uses passenger_list with first_name, last_name, passport, birth_date, passport_expiry, ticket_type
        if passengers:
            pl = []
            for p in passengers:
                pl.append({
                    'first_name': p.get('first_name', p.get('name', '').split()[0] if p.get('name') else ''),
                    'last_name': p.get('last_name', p.get('name', '').split()[-1] if p.get('name') and len(p.get('name', '').split()) > 1 else ''),
                    'passport': p.get('passport', p.get('passport_number', '')),
                    'birth_date': p.get('birth_date', p.get('dob', '')),
                    'passport_expiry': p.get('passport_expiry', ''),
                    'ticket_type': p.get('ticket_type', 'כרטיס רגיל')
                })
            st.session_state.passenger_list = pl
        else:
            st.session_state.passenger_list = [{'first_name': '', 'last_name': '', 'passport': '', 'birth_date': '', 'passport_expiry': '', 'ticket_type': 'כרטיס רגיל'}]
        st.session_state.ui_step = 3
        st.session_state.product_type_selected = 'full_package' if load_proposal.get('product_type') == 'package' else 'tickets_only'
        st.session_state.event_type_selected = 'football' if (load_proposal.get('event_type') == 'כדורגל' or load_proposal.get('event_type') == 'ספורט') else ('concert' if load_proposal.get('event_type') == 'הופעה' else 'other')
        st.rerun()

    # Route to appropriate screen based on ui_step
    if st.session_state['ui_step'] == 1:
        show_product_selection()
        return
    elif st.session_state['ui_step'] == 2:
        show_event_selection()
        return
    elif st.session_state['ui_step'] == 3:
        # Show summary and form
        show_selection_summary()
        # Continue to show the full OLD FORM below (it has all the smart features)
        # We just skip the product_type and event_type selection since already done in steps 1-2
        pass
    
    # === OLD FORM BELOW (WILL BE REMOVED) ===
    # Success message if package loaded
    if st.session_state.get('package_loaded_success'):
        pkg_name = st.session_state['package_loaded_success']
        st.success(f"✅ נטענה חבילה: {pkg_name}")
        st.info("💡 עכשיו רק צריך להוסיף פרטי נוסעים ולקוח!")
        del st.session_state['package_loaded_success']
    
    st.markdown("""
        <a href="https://travel-agents-calculatornew.pages.dev/" target="_blank" style="
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 12px 24px;
            border-radius: 10px;
            text-decoration: none;
            font-weight: bold;
            font-size: 16px;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            margin-bottom: 20px;
        ">
            🧮 מחשבון סוכנים
        </a>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.2, 0.8])
    
    with col1:
        st.markdown("### 📝 פרטי ההזמנה")
        
        rd = st.session_state.random_data or {}
        
        # סוג מוצר - השתמש בבחירה משלב 1 ו-2 אם קיימת
        if st.session_state.get('ui_step') == 3 and st.session_state.get('product_type_selected'):
            product_type = "package" if st.session_state.get('product_type_selected') == 'full_package' else "tickets"
        else:
            st.markdown('<div class="form-section"><h3>📦 סוג המוצר</h3></div>', unsafe_allow_html=True)
            product_options = ["tickets", "package"]
            product_default = 1 if rd.get('product_type') == 'package' else 0
            product_type = st.radio(
                "בחר סוג מוצר",
                options=product_options,
                index=product_default,
                format_func=lambda x: "🎫 כרטיסים בלבד" if x == "tickets" else "✈️ חבילה מלאה (טיסה + מלון + כרטיס)",
                horizontal=True
            )
        
        st.markdown('<div class="form-section"><h3>📦 טעינה מחבילה קבועה</h3></div>', unsafe_allow_html=True)
        
        db = get_db()
        saved_packages = []
        if db:
            try:
                saved_packages = db.query(PackageTemplate).filter(PackageTemplate.is_active == True).order_by(PackageTemplate.name).all()
            except:
                pass
            finally:
                db.close()
        
        if saved_packages:
            package_options = ["-- בחר חבילה --"] + [f"{pkg.name}" for pkg in saved_packages]
            package_ids = [None] + [pkg.id for pkg in saved_packages]
            
            selected_package_idx = st.selectbox(
                "📦 טען פרטים מחבילה שמורה",
                range(len(package_options)),
                format_func=lambda x: package_options[x],
                key="load_package_select"
            )
            
            if selected_package_idx and selected_package_idx > 0:
                pkg_id = package_ids[selected_package_idx]
                selected_pkg = next((p for p in saved_packages if p.id == pkg_id), None)
                
                if selected_pkg and st.button("📥 טען חבילה", type="primary", use_container_width=True):
                    pkg_data = selected_pkg.to_dict()
                    
                    product_val = "package" if pkg_data.get('product_type') == 'full_package' else "tickets"
                    event_type_map = {'concert': 'הופעה', 'football': 'כדורגל', 'other': 'אחר'}
                    
                    flights = pkg_data.get('flights', {})
                    hotel = pkg_data.get('hotel', {})
                    
                    st.session_state.random_data = {
                        'product_type': product_val,
                        'event_name': pkg_data.get('event_name', ''),
                        'event_date': pkg_data.get('event_date', ''),
                        'event_time': pkg_data.get('event_time', ''),
                        'venue': pkg_data.get('venue', ''),
                        'event_type': event_type_map.get(pkg_data.get('event_type'), 'הופעה'),
                        'category': pkg_data.get('ticket_category', ''),
                        'ticket_description': pkg_data.get('ticket_description', ''),
                        'price_euro': int(pkg_data.get('package_price_euro', 0) or 0),
                        'hotel_name': hotel.get('name', ''),
                        'hotel_checkin': hotel.get('check_in', ''),
                        'hotel_checkout': hotel.get('check_out', ''),
                        'outbound_from': flights.get('outbound', {}).get('from', ''),
                        'outbound_to': flights.get('outbound', {}).get('to', ''),
                        'outbound_date': flights.get('outbound', {}).get('date', ''),
                        'outbound_time': flights.get('outbound', {}).get('time', ''),
                        'outbound_flight': flights.get('outbound', {}).get('flight_number', ''),
                        'return_from': flights.get('return', {}).get('from', ''),
                        'return_to': flights.get('return', {}).get('to', ''),
                        'return_date': flights.get('return', {}).get('date', ''),
                        'return_time': flights.get('return', {}).get('time', ''),
                        'return_flight': flights.get('return', {}).get('flight_number', ''),
                        'loaded_from_package': pkg_data.get('name', ''),
                        'package_notes': pkg_data.get('notes', '')
                    }
                    
                    if flights.get('outbound'):
                        st.session_state['flight_outbound_from'] = flights['outbound'].get('from', '')
                        st.session_state['flight_outbound_to'] = flights['outbound'].get('to', '')
                        st.session_state['flight_outbound_date'] = flights['outbound'].get('date', '')
                        st.session_state['flight_outbound_time'] = flights['outbound'].get('time', '')
                        st.session_state['flight_outbound_no'] = flights['outbound'].get('flight_number', '')
                        st.session_state['flight_outbound_airline'] = flights['outbound'].get('airline', '')
                    if flights.get('return'):
                        st.session_state['flight_return_from'] = flights['return'].get('from', '')
                        st.session_state['flight_return_to'] = flights['return'].get('to', '')
                        st.session_state['flight_return_date'] = flights['return'].get('date', '')
                        st.session_state['flight_return_time'] = flights['return'].get('time', '')
                        st.session_state['flight_return_no'] = flights['return'].get('flight_number', '')
                        st.session_state['flight_return_airline'] = flights['return'].get('airline', '')
                    
                    if pkg_data.get('stadium_map_data'):
                        import base64
                        map_bytes = base64.b64decode(pkg_data['stadium_map_data'])
                        st.session_state['saved_stadium_map_bytes'] = map_bytes
                        st.session_state['package_stadium_map_loaded'] = True
                    
                    if hotel:
                        st.session_state.hotel_data = {
                            'hotel_name': hotel.get('name', ''),
                            'hotel_address': hotel.get('address', ''),
                            'hotel_website': hotel.get('website', ''),
                            'hotel_rating': hotel.get('rating', 0),
                            'hotel_stars': hotel.get('stars', '5 כוכבים'),
                            'hotel_image_path': hotel.get('image_path', ''),
                            'hotel_image_path_2': hotel.get('image_path_2', ''),
                            'hotel_checkin': hotel.get('check_in', ''),
                            'hotel_checkout': hotel.get('check_out', ''),
                            'from_package': True
                        }
                    
                    st.session_state['package_loaded_success'] = pkg_data.get('name')
                    st.rerun()
        else:
            st.caption("💡 אין חבילות שמורות. צור חבילות דרך 'חבילות קבועות' בתפריט.")
        
        st.markdown("---")
        
        if st.button("🎲 מילוי רנדומלי לבדיקה", type="secondary"):
            import random
            from sports_api import LEAGUES, get_teams_by_league, get_hebrew_name
            
            sample_football_matches = [
                {"league": "ליגה ספרדית", "home": "Real Madrid", "away": "Barcelona", "stadium": "Santiago Bernabeu", "city": "Madrid", "hotel": "Hotel Villa Magna Madrid"},
                {"league": "פרמיירליג", "home": "Manchester United", "away": "Liverpool", "stadium": "Old Trafford", "city": "Manchester", "hotel": "The Lowry Hotel Manchester"},
                {"league": "בונדסליגה", "home": "Bayern Munich", "away": "Borussia Dortmund", "stadium": "Allianz Arena", "city": "Munich", "hotel": "Mandarin Oriental Munich"},
                {"league": "סריה A", "home": "AC Milan", "away": "Inter", "stadium": "San Siro", "city": "Milan", "hotel": "Armani Hotel Milano"},
                {"league": "ליגה ספרדית", "home": "Atletico Madrid", "away": "Sevilla", "stadium": "Civitas Metropolitano", "city": "Madrid", "hotel": "Four Seasons Hotel Madrid"},
            ]
            
            sample_passengers = [
                [
                    {"first_name": "Israel", "last_name": "Israeli", "passport": "12345678", "birth_date": "15/03/1985", "passport_expiry": "20/05/2030", "ticket_type": "כרטיס רגיל"},
                    {"first_name": "Sarah", "last_name": "Israeli", "passport": "87654321", "birth_date": "22/07/1988", "passport_expiry": "18/09/2029", "ticket_type": "כרטיס רגיל"},
                    {"first_name": "Noam", "last_name": "Israeli", "passport": "11998877", "birth_date": "12/09/2010", "passport_expiry": "12/09/2030", "ticket_type": "כרטיס ילד"},
                    {"first_name": "Tamar", "last_name": "Israeli", "passport": "22334455", "birth_date": "20/11/2015", "passport_expiry": "20/11/2035", "ticket_type": "כרטיס ילד"},
                ],
                [
                    {"first_name": "David", "last_name": "Cohen", "passport": "11223344", "birth_date": "01/01/1990", "passport_expiry": "01/01/2031", "ticket_type": "כרטיס VIP"},
                    {"first_name": "Rachel", "last_name": "Cohen", "passport": "44332211", "birth_date": "15/06/1992", "passport_expiry": "15/06/2032", "ticket_type": "כרטיס VIP"},
                    {"first_name": "Yosef", "last_name": "Cohen", "passport": "55667788", "birth_date": "10/10/2010", "passport_expiry": "10/10/2028", "ticket_type": "כרטיס ילד"},
                    {"first_name": "Maya", "last_name": "Cohen", "passport": "99887766", "birth_date": "25/12/2013", "passport_expiry": "25/12/2033", "ticket_type": "כרטיס ילד"},
                ],
            ]
            
            sample_structured_flights = {
                "Madrid": {
                    'outbound': {'from': 'TLV', 'to': 'MAD', 'date': '15/01/2025', 'time': '09:00', 'flight_number': 'LY315'},
                    'return': {'from': 'MAD', 'to': 'TLV', 'date': '18/01/2025', 'time': '22:00', 'flight_number': 'LY316'}
                },
                "Manchester": {
                    'outbound': {'from': 'TLV', 'to': 'MAN', 'date': '20/02/2025', 'time': '07:30', 'flight_number': 'LY317'},
                    'return': {'from': 'MAN', 'to': 'TLV', 'date': '24/02/2025', 'time': '21:00', 'flight_number': 'LY318'}
                },
                "Munich": {
                    'outbound': {'from': 'TLV', 'to': 'MUC', 'date': '10/03/2025', 'time': '08:00', 'flight_number': 'LH681'},
                    'return': {'from': 'MUC', 'to': 'TLV', 'date': '13/03/2025', 'time': '19:00', 'flight_number': 'LH682'}
                },
                "Milan": {
                    'outbound': {'from': 'TLV', 'to': 'MXP', 'date': '05/04/2025', 'time': '06:30', 'flight_number': 'LY381'},
                    'return': {'from': 'MXP', 'to': 'TLV', 'date': '08/04/2025', 'time': '20:00', 'flight_number': 'LY382'}
                },
            }
            
            passengers = random.choice(sample_passengers)
            currency = 'EUR'
            currency_symbols = {'EUR': '€', 'USD': '$', 'GBP': '£'}
            
            match = random.choice(sample_football_matches)
            home_heb = get_hebrew_name(match['home'])
            away_heb = get_hebrew_name(match['away'])
            event_name = f"{home_heb} נגד {away_heb}"
            venue = f"{match['stadium']}, {match['city']}"
            event_type = "כדורגל"
            hotel = match['hotel']
            
            st.session_state['football_league'] = match['league']
            st.session_state['football_team1'] = f"{home_heb} ({match['home']})"
            st.session_state['football_team2'] = f"{away_heb} ({match['away']})"
            
            league_eng = LEAGUES.get(match['league'], "")
            teams = get_teams_by_league(league_eng)
            
            # Match team by name (handle both 'name' and 'name_en')
            home_team = None
            away_team = None
            for t in teams:
                team_name = t.get('name_en') or t.get('name', '')
                if team_name == match['home']:
                    home_team = t
                    # Ensure 'name' field exists for stadium map loading
                    if 'name' not in home_team and 'name_en' in home_team:
                        home_team = dict(home_team)  # Make a copy
                        home_team['name'] = home_team['name_en']
                if team_name == match['away']:
                    away_team = t
                    if 'name' not in away_team and 'name_en' in away_team:
                        away_team = dict(away_team)
                        away_team['name'] = away_team['name_en']
            
            # If not found in teams list, create minimal team data
            if not home_team:
                home_team = {'name': match['home'], 'stadium': match['stadium']}
            if not away_team:
                away_team = {'name': match['away']}
            
            st.session_state['selected_team_data'] = home_team
            st.session_state['home_team_hebrew'] = home_heb
            st.session_state['away_team_data'] = away_team
            st.session_state['away_team_hebrew'] = away_heb
            
            flights = sample_structured_flights.get(match['city'], sample_structured_flights['Madrid'])
            
            # Populate hotel data for package
            if product_type == "package":
                # Try to get hotel from cache first
                hotel_from_cache = None
                try:
                    db = get_db()  # Already imported at top
                    if db:
                        # Search for hotel in cache by city
                        cached = db.query(HotelCache).filter(
                            HotelCache.search_query.ilike(f'%{match["city"].lower()}%')
                        ).first()
                        if cached:
                            hotel_from_cache = cached.to_dict()
                        db.close()
                except Exception:
                    pass
                
                if hotel_from_cache:
                    # Use real hotel data from cache
                    st.session_state['hotel_data'] = hotel_from_cache
                else:
                    # Use sample data
                    st.session_state['hotel_data'] = {
                        'name': hotel,
                        'check_in': flights['outbound']['date'],
                        'check_out': flights['return']['date'],
                        'address': f"{match['city']}, City Center",
                        'website': f"http://www.{hotel.lower().replace(' ', '').replace('-', '')}.com",
                        'rating': random.choice([4.3, 4.5, 4.7, 4.8]),
                        'stars': "5 כוכבים",
                        'nights': 3,
                        'meals': "ארוחת בוקר"
                    }
            
            st.session_state.random_data = {
                'product_type': product_type,
                'event_name': event_name,
                'venue': venue,
                'event_type': event_type,
                'hotel_name': hotel,
                'hotel_nights': 3,
                'hotel_stars': "5 כוכבים",
                'hotel_meals': "ארוחת בוקר",
                'transfers': True,
                'outbound_from': flights['outbound']['from'],
                'outbound_to': flights['outbound']['to'],
                'outbound_date': flights['outbound']['date'],
                'outbound_time': flights['outbound']['time'],
                'outbound_flight': flights['outbound']['flight_number'],
                'return_from': flights['return']['from'],
                'return_to': flights['return']['to'],
                'return_date': flights['return']['date'],
                'return_time': flights['return']['time'],
                'return_flight': flights['return']['flight_number'],
                'bag_trolley': True,
                'bag_checked': '23kg',
                'customer_name': passengers[0]['first_name'] + " " + passengers[0]['last_name'],
                'customer_id': ''.join([str(random.randint(0, 9)) for _ in range(9)]),
                'customer_phone': f"052-{random.randint(1000000, 9999999)}",
                'customer_email': f"{passengers[0]['first_name'].lower()}.{passengers[0]['last_name'].lower()}@gmail.com",
                'category': random.choice(["CAT 1", "CAT 2", "CAT 3"]),
                'ticket_description': "כרטיסים בקטגוריה מול המגרש",
                'currency': currency,
                'currency_symbol': currency_symbols[currency],
                'price_euro': random.choice([350, 450, 550, 750]),
                'num_tickets': len(passengers),
                'passengers': passengers,
                'use_sample_images': True
            }
            
            st.session_state.passenger_list = passengers
            for i, p in enumerate(passengers):
                st.session_state[f"first_name_{i}"] = p['first_name']
                st.session_state[f"last_name_{i}"] = p['last_name']
                st.session_state[f"passport_{i}"] = p['passport']
                st.session_state[f"birth_date_{i}"] = p['birth_date']
                st.session_state[f"passport_expiry_{i}"] = p['passport_expiry']
            
            st.session_state['flight_outbound_from'] = flights['outbound']['from']
            st.session_state['flight_outbound_to'] = flights['outbound']['to']
            st.session_state['flight_outbound_date'] = flights['outbound']['date']
            st.session_state['flight_outbound_time'] = flights['outbound']['time']
            st.session_state['flight_outbound_no'] = flights['outbound']['flight_number']
            st.session_state['flight_outbound_airline'] = get_airline_from_flight(flights['outbound']['flight_number'])
            st.session_state['flight_return_from'] = flights['return']['from']
            st.session_state['flight_return_to'] = flights['return']['to']
            st.session_state['flight_return_date'] = flights['return']['date']
            st.session_state['flight_return_time'] = flights['return']['time']
            st.session_state['flight_return_no'] = flights['return']['flight_number']
            st.session_state['flight_return_airline'] = get_airline_from_flight(flights['return']['flight_number'])
            
            st.rerun()
        
        col_random, col_clear = st.columns(2)
        with col_clear:
            if st.button("🗑️ ניקוי טופס", type="secondary"):
                keys_to_clear = [
                    'random_data', 'passenger_list', 'order_generated', 'pdf_bytes',
                    'current_order_number', 'current_order_id', 'selected_team_data',
                    'away_team_data', 'home_team_hebrew', 'away_team_hebrew',
                    'football_league', 'hotel_data', 'pasted_passports', '_passport_paste_refresh', 'pasted_flight',
                    'worldcup_match', 'worldcup_venue', 'fixture_data', 'worldcup_stadium_map',
                    'pasted_stadium_map', 'saved_stadium_map_path', 'saved_stadium_map_bytes', '_selected_concert',
                    '_from_saved_concert', 'concert_venue_info', 'concert_artist_en',
                    'concert_artist_he', 'concert_venue_name', 'concert_venue_city',
                    'concert_selected_category', '_concert_venue_id', 'games', 'saved_games', 'finished_adding_games',
                    'flights_data', 'show_save_package_form', 'show_save_proposal_form'
                ]
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                for key in list(st.session_state.keys()):
                    if key.startswith(('first_name_', 'last_name_', 'passport_', 'birth_date_', 'passport_expiry_', 'flight_')):
                        del st.session_state[key]
                st.session_state.passenger_list = [{'first_name': '', 'last_name': '', 'passport': '', 'birth_date': '', 'passport_expiry': '', 'ticket_type': 'כרטיס רגיל'}]
                st.success("✅ הטופס נוקה!")
                st.rerun()
        
        # Initialize saved games list
        if 'saved_games' not in st.session_state:
            st.session_state['saved_games'] = []
        
        st.markdown('<div class="form-section"><h3>🎭 פרטי האירועים</h3></div>', unsafe_allow_html=True)
        
        # Display saved games (improved: expanders/cards with details and delete)
        if st.session_state['saved_games']:
            st.markdown("##### ✅ אירועים שנשמרו:")
            saved_list = st.session_state['saved_games']
            for idx, saved_game in enumerate(saved_list):
                game_text = saved_game.get('display_text', f"אירוע {idx + 1}")
                details = saved_game.get('details', '')
                title = f"אירוע {idx + 1}: {game_text}"
                if len(saved_list) >= 2:
                    with st.expander(title, expanded=(idx == 0)):
                        if details:
                            st.caption(details)
                        if st.button("🗑️ מחק אירוע", key=f"delete_saved_game_{idx}", help="מחק אירוע"):
                            st.session_state['saved_games'].pop(idx)
                            st.rerun()
                else:
                    st.success(f"**{idx + 1}.** {game_text}")
                    if details:
                        st.caption(details)
                    if st.button("🗑️", key=f"delete_saved_game_{idx}", help="מחק אירוע"):
                        st.session_state['saved_games'].pop(idx)
                        st.rerun()
            st.markdown("---")
        
        if st.session_state.get('finished_adding_games', False):
            # User chose "Save and finish" – show only list + add-another button, then skip to hotel
            if st.button("➕ הוסף אירוע נוסף", key="add_another_event_btn", type="primary", use_container_width=True):
                st.session_state['finished_adding_games'] = False
                st.rerun()
            # Set event_name, venue, event_date, event_time, event_type, category from first saved game for downstream
            from datetime import datetime as _dt, date as _date, time as _time
            saved = st.session_state.get('saved_games', [])
            if saved:
                first = saved[0]
                event_type = first.get('event_type', 'כדורגל')
                event_name = first.get('display_text', 'אירוע')
                fixture = first.get('fixture_data', {})
                venue = first.get('worldcup_venue') or ''
                if not venue and fixture:
                    venue = (fixture.get('venue') or '') + (f", {fixture.get('city')}" if fixture.get('city') else '')
                if not venue and first.get('concert_venue_name'):
                    venue = first.get('concert_venue_name', '') + (f", {first.get('concert_venue_city', '')}" if first.get('concert_venue_city') else '')
                if fixture.get('date'):
                    try:
                        event_date = _dt.strptime(fixture['date'], "%Y-%m-%d").date()
                    except Exception:
                        event_date = _date.today()
                else:
                    event_date = _date.today()
                if fixture.get('time'):
                    try:
                        tstr = (fixture.get('time') or '')[:5]
                        event_time = _dt.strptime(tstr, "%H:%M").time() if len(tstr) == 5 else _time(12, 0)
                    except Exception:
                        event_time = _time(12, 0)
                else:
                    event_time = _time(12, 0)
                category = first.get('worldcup_category') or first.get('concert_selected_category') or 'CAT 1'
            else:
                event_type = 'כדורגל'
                event_name = ''
                venue = ''
                event_date = _date.today()
                event_time = _time(12, 0)
                category = 'CAT 1'
            # So col2 and order_data don't fail when form was skipped (UnboundLocalError)
            stadium_image = None
            auto_stadium_map = None
            is_date_final = False
            seats_together = False
            st.markdown("---")
        else:
            if st.session_state['saved_games']:
                st.info(f"💡 סה\"כ {len(st.session_state['saved_games'])} אירועים נשמרו. ממשיך למלא פרטי אירוע נוסף...")
                st.markdown("---")
        
                # Determine event type
            if st.session_state.get('ui_step') == 3 and st.session_state.get('event_type_selected'):
                event_map = {'concert': 'הופעה', 'football': 'כדורגל', 'worldcup_2026': 'כדורגל'}
                event_type = event_map.get(st.session_state.get('event_type_selected'), 'כדורגל')
                # אם נבחר מונדיאל, נגדיר את הליגה אוטומטית
                if st.session_state.get('event_type_selected') == 'worldcup_2026':
                    st.session_state['football_league'] = "מונדיאל 2026"
            else:
                event_types = ["כדורגל", "הופעה", "אחר"]
                default_type_idx = event_types.index(rd.get('event_type', 'כדורגל')) if rd.get('event_type') in event_types else 0
                event_type = st.selectbox("סוג אירוע", event_types, index=default_type_idx)
        
            if event_type == "כדורגל":
                from sports_api import LEAGUES, get_teams_by_league, get_hebrew_name, TEAM_HEBREW_NAMES, find_fixture
            
                st.markdown("##### ⚽ בחירת קבוצות (השלמה אוטומטית)")
            
                col_league = st.columns([1])[0]
                with col_league:
                    league_options = ["-- בחר ליגה --"] + list(LEAGUES.keys())
                    selected_league = st.selectbox("ליגה", league_options, key="football_league")
            
                is_worldcup = selected_league == "מונדיאל 2026"
            
                if is_worldcup:
                    try:
                        with open(WORLDCUP_JSON_PATH, 'r', encoding='utf-8') as f:
                            wc_data = json.load(f)
                        wc_matches = wc_data.get('matches', [])
                    except Exception as e:
                        wc_matches = []
                        if not os.path.exists(WORLDCUP_JSON_PATH):
                            st.error(f"קובץ משחקי מונדיאל לא נמצא: {WORLDCUP_JSON_PATH}")
                        else:
                            st.error(f"שגיאה בטעינת משחקי מונדיאל: {e}")
                
                    NATIONAL_TEAM_HEBREW = {
                        "Mexico": "מקסיקו", "South Africa": "דרום אפריקה", "South Korea": "דרום קוריאה",
                        "Canada": "קנדה", "USA": "ארה\"ב", "Paraguay": "פרגוואי", "Haiti": "האיטי",
                        "Scotland": "סקוטלנד", "Australia": "אוסטרליה", "Brazil": "ברזיל", "Morocco": "מרוקו",
                        "Qatar": "קטאר", "Switzerland": "שוויץ", "Ivory Coast": "חוף השנהב",
                        "Ecuador": "אקוודור", "Germany": "גרמניה", "Curacao": "קוראסאו",
                        "Netherlands": "הולנד", "Japan": "יפן", "Tunisia": "טוניסיה",
                        "Saudi Arabia": "סעודיה", "Uruguay": "אורוגוואי", "Spain": "ספרד",
                        "Cabo Verde": "קאבו ורדה", "Iran": "איראן", "New Zealand": "ניו זילנד",
                        "Belgium": "בלגיה", "Egypt": "מצרים", "France": "צרפת", "Senegal": "סנגל",
                        "Norway": "נורבגיה", "Argentina": "ארגנטינה", "Algeria": "אלג'יריה",
                        "Austria": "אוסטריה", "Jordan": "ירדן", "Ghana": "גאנה", "Panama": "פנמה",
                        "England": "אנגליה", "Croatia": "קרואטיה", "Portugal": "פורטוגל",
                        "Uzbekistan": "אוזבקיסטן", "Colombia": "קולומביה"
                    }
                
                    def get_team_heb(name):
                        return NATIONAL_TEAM_HEBREW.get(name, name)
                
                    def format_date(date_str):
                        try:
                            from datetime import datetime as dt
                            d = dt.strptime(date_str, "%Y-%m-%d")
                            return d.strftime("%d/%m/%Y")
                        except:
                            return date_str
                
                    match_options = ["-- בחר משחק --"]
                    for m in wc_matches:
                        team1_heb = get_team_heb(m['team1'])
                        team2_heb = get_team_heb(m['team2'])
                        date_fmt = format_date(m['date'])
                        option = f"משחק {m['match_num']}: {team1_heb} נגד {team2_heb} ({date_fmt})"
                        match_options.append(option)
                
                    selected_match = st.selectbox("🏆 בחר משחק מונדיאל", match_options, key="worldcup_match")
                
                    if selected_match and selected_match != "-- בחר משחק --":
                        match_num = int(selected_match.split(":")[0].replace("משחק ", "").strip())
                        match_data = next((m for m in wc_matches if m['match_num'] == match_num), None)
                    
                        if match_data:
                            team1_heb = get_team_heb(match_data['team1'])
                            team2_heb = get_team_heb(match_data['team2'])
                            st.session_state['home_team_hebrew'] = team1_heb
                            st.session_state['away_team_hebrew'] = team2_heb
                            st.session_state['selected_team_data'] = {'name': match_data['team1']}
                            st.session_state['away_team_data'] = {'name': match_data['team2']}
                            st.session_state['fixture_data'] = {
                                'date': match_data['date'],
                                'time': match_data['time'],
                                'venue': match_data['venue'],
                                'city': match_data['city'],
                                'round': match_data['round']
                            }
                            st.session_state['worldcup_venue'] = f"{match_data['venue']}, {match_data['city']}"
                        
                            try:
                                with open(WORLDCUP_STADIUMS_JSON_PATH, 'r', encoding='utf-8') as f:
                                    wc_stadiums = json.load(f)
                                stadium_info = wc_stadiums.get('stadiums', {}).get(match_data['venue'], {})
                                if stadium_info.get('map_file'):
                                    st.session_state['worldcup_stadium_map'] = stadium_info['map_file']
                                else:
                                    st.session_state['worldcup_stadium_map'] = ''
                            except:
                                st.session_state['worldcup_stadium_map'] = ''
                        
                            st.info(f"🏆 **{match_data['round']}** | {team1_heb} נגד {team2_heb}")
                            st.caption(f"📍 {match_data['venue']}, {match_data['city']} | 📅 {format_date(match_data['date'])} {match_data['time']}")
                        
                            wc_categories = ["קטגוריה 3/4", "קטגוריה 3", "קטגוריה 2", "קטגוריה 1"]
                            st.selectbox("🎫 בחר קטגוריית כרטיסים", wc_categories, key="worldcup_category")
                    else:
                        st.session_state['fixture_data'] = {}
                        st.session_state['selected_team_data'] = {}
                        st.session_state['away_team_data'] = {}
                        st.session_state['home_team_hebrew'] = ''
                        st.session_state['away_team_hebrew'] = ''
                        st.session_state['worldcup_venue'] = ''
                else:
                    from sports_api import get_season_fixtures
                
                    teams = []
                    fixtures = []
                    if selected_league and selected_league != "-- בחר ליגה --":
                        english_league = LEAGUES.get(selected_league, "") or selected_league
                        teams = get_teams_by_league(english_league)
                        fixtures = get_season_fixtures(english_league)
                        if not fixtures and selected_league:
                            fixtures = get_season_fixtures(selected_league)
                        if not teams and selected_league:
                            teams = get_teams_by_league(selected_league)
                    else:
                        st.session_state['fixture_data'] = {}
                        st.session_state['selected_team_data'] = {}
                        st.session_state['away_team_data'] = {}
                
                    selection_modes = ["🎯 בחר משחק מרשימה", "✏️ בחר קבוצות ידנית"]
                    selection_mode = st.radio("אופן בחירה", selection_modes, horizontal=True, key="football_selection_mode", label_visibility="collapsed")
                
                    prev_mode = st.session_state.get('_prev_football_mode', '')
                    if prev_mode != selection_mode:
                        st.session_state['_prev_football_mode'] = selection_mode
                        st.session_state['fixture_data'] = {}
                        st.session_state['selected_team_data'] = {}
                        st.session_state['away_team_data'] = {}
                        st.session_state['home_team_hebrew'] = ''
                        st.session_state['away_team_hebrew'] = ''
                
                    if selection_mode == "🎯 בחר משחק מרשימה" and not fixtures:
                        st.warning("⚠️ אין נתוני משחקים זמינים לליגה זו. השתמש בבחירה ידנית.")
                
                    if selection_mode == "🎯 בחר משחק מרשימה" and fixtures:
                        team_filter = st.text_input("🔍 חפש קבוצה (עברית/אנגלית)", placeholder="למשל: ברצלונה, Real Madrid", key="football_team_filter")
                    
                        def format_fixture_date(date_str):
                            try:
                                from datetime import datetime as dt
                                d = dt.strptime(date_str, "%Y-%m-%d")
                                return d.strftime("%d/%m/%Y")
                            except:
                                return date_str
                    
                        from datetime import datetime as dt
                        today = dt.now().date()
                        future_fixtures = []
                        for f in fixtures:
                            try:
                                match_date = dt.strptime(f.get('date', '') or '', "%Y-%m-%d").date()
                                if match_date >= today:
                                    future_fixtures.append(f)
                            except Exception:
                                future_fixtures.append(f)
                        # If no future fixtures, show all so list is never empty
                        if not future_fixtures and fixtures:
                            future_fixtures = fixtures
                        filtered_fixtures = future_fixtures
                        if team_filter:
                            filter_lower = team_filter.lower().strip()
                            eng_name = TEAM_HEBREW_NAMES.get(team_filter.strip(), '')
                        
                            filtered_fixtures = []
                            for f in future_fixtures:
                                home_lower = f['home_team'].lower()
                                away_lower = f['away_team'].lower()
                                home_heb = get_hebrew_name(f['home_team']).lower()
                                away_heb = get_hebrew_name(f['away_team']).lower()
                            
                                match_found = (
                                    filter_lower in home_lower or filter_lower in away_lower or
                                    filter_lower in home_heb or filter_lower in away_heb or
                                    home_lower in filter_lower or away_lower in filter_lower or
                                    (eng_name and (eng_name.lower() in home_lower or eng_name.lower() in away_lower))
                                )
                                if match_found:
                                    filtered_fixtures.append(f)
                    
                        filtered_fixtures = sorted(filtered_fixtures, key=lambda x: x.get('date', ''))
                    
                        match_options = ["-- בחר משחק --"]
                        for f in filtered_fixtures:
                            home_heb = get_hebrew_name(f['home_team'])
                            away_heb = get_hebrew_name(f['away_team'])
                            date_fmt = format_fixture_date(f['date'])
                            time_str = f.get('time', '')[:5] if f.get('time') else ''
                            round_str = f.get('round', '')
                        
                            option = f"⚽ {home_heb} נגד {away_heb}"
                            option += f" | 📅 {date_fmt}"
                            if time_str and time_str != '00:00':
                                option += f" ⏰ {time_str}"
                            match_options.append((option, f))
                    
                        match_display_options = [m[0] if isinstance(m, tuple) else m for m in match_options]
                        filter_key = f"league_match_{len(filtered_fixtures)}_{team_filter[:10] if team_filter else 'all'}"
                        selected_match_idx = st.selectbox("⚽ בחר משחק", range(len(match_display_options)), 
                                                           format_func=lambda x: match_display_options[x], 
                                                           key=filter_key)
                    
                        if selected_match_idx > 0 and selected_match_idx < len(match_options) and isinstance(match_options[selected_match_idx], tuple):
                            selected_fixture = match_options[selected_match_idx][1]
                            home_team = next((t for t in teams if t['name'].lower() == (selected_fixture.get('home_team') or '').lower() or 
                                              (selected_fixture.get('home_team') or '').lower() in t['name'].lower() or
                                              t['name'].lower() in (selected_fixture.get('home_team') or '').lower()), None)
                            away_team = next((t for t in teams if t['name'].lower() == (selected_fixture.get('away_team') or '').lower() or
                                              (selected_fixture.get('away_team') or '').lower() in t['name'].lower() or
                                              t['name'].lower() in (selected_fixture.get('away_team') or '').lower()), None)
                            if not home_team:
                                home_team = {'name': selected_fixture.get('home_team', ''), 'stadium': '', 'stadium_location': ''}
                            if not away_team:
                                away_team = {'name': selected_fixture.get('away_team', ''), 'stadium': '', 'stadium_location': ''}
                            home_heb = get_hebrew_name(selected_fixture.get('home_team', ''))
                            away_heb = get_hebrew_name(selected_fixture.get('away_team', ''))
                            st.session_state['selected_team_data'] = home_team
                            st.session_state['away_team_data'] = away_team
                            st.session_state['home_team_hebrew'] = home_heb
                            st.session_state['away_team_hebrew'] = away_heb
                            st.session_state['fixture_data'] = {
                                'date': selected_fixture.get('date', ''),
                                'time': selected_fixture.get('time', ''),
                                'round': selected_fixture.get('round', '')
                            }
                            st.success(f"✅ **{home_heb}** נגד **{away_heb}**")
                            date_fmt = format_fixture_date(selected_fixture.get('date', ''))
                            time_str = selected_fixture.get('time', '')[:5] if selected_fixture.get('time') else ''
                            info_text = f"📅 {date_fmt}"
                            if time_str and time_str != '00:00':
                                info_text += f" | ⏰ {time_str}"
                            if home_team.get('stadium'):
                                info_text += f" | 🏟️ {home_team['stadium']}"
                            st.caption(info_text)
                        else:
                            st.session_state['fixture_data'] = {}
                            st.session_state['selected_team_data'] = {}
                            st.session_state['away_team_data'] = {}
                            st.session_state['home_team_hebrew'] = ''
                            st.session_state['away_team_hebrew'] = ''
                    
                        if not fixtures:
                            st.info("💡 לא נמצאו משחקים לליגה זו. נסה לבחור קבוצות ידנית.")
                
                    else:
                        col_team1, col_team2 = st.columns(2)
                        with col_team1:
                            if teams:
                                team_options = ["-- קבוצה מארחת --"] + [f"{get_hebrew_name(t['name'])} ({t['name']})" for t in teams]
                                selected_team1 = st.selectbox("קבוצה מארחת 🏠", team_options, key="football_team1")
                            
                                if selected_team1 and selected_team1 != "-- קבוצה מארחת --":
                                    team_name_eng = selected_team1.split("(")[-1].replace(")", "").strip()
                                    selected_team = next((t for t in teams if t['name'] == team_name_eng), None)
                                    if selected_team:
                                        st.session_state['selected_team_data'] = selected_team
                                        st.session_state['home_team_hebrew'] = selected_team1.split(" (")[0]
                                else:
                                    st.session_state['selected_team_data'] = {}
                                    st.session_state['home_team_hebrew'] = ''
                            else:
                                st.selectbox("קבוצה מארחת 🏠", ["-- בחר ליגה קודם --"], disabled=True, key="team1_disabled")
                    
                        with col_team2:
                            if teams:
                                team_options2 = ["-- קבוצה אורחת --"] + [f"{get_hebrew_name(t['name'])} ({t['name']})" for t in teams]
                                selected_team2 = st.selectbox("קבוצה אורחת ✈️", team_options2, key="football_team2")
                            
                                if selected_team2 and selected_team2 != "-- קבוצה אורחת --":
                                    team_name_eng2 = selected_team2.split("(")[-1].replace(")", "").strip()
                                    away_team = next((t for t in teams if t['name'] == team_name_eng2), None)
                                    if away_team:
                                        st.session_state['away_team_data'] = away_team
                                    st.session_state['away_team_hebrew'] = selected_team2.split(" (")[0]
                                else:
                                    st.session_state['away_team_data'] = {}
                                    st.session_state['away_team_hebrew'] = ''
                            else:
                                st.selectbox("קבוצה אורחת ✈️", ["-- בחר ליגה קודם --"], disabled=True, key="team2_disabled")
                
                    team_data = st.session_state.get('selected_team_data', {})
                    home_heb = st.session_state.get('home_team_hebrew', '')
                    away_heb = st.session_state.get('away_team_hebrew', '')
                
                    if team_data.get('badge') and home_heb:
                        col_badge, col_info = st.columns([1, 3])
                        with col_badge:
                            st.image(team_data['badge'], width=60)
                        with col_info:
                            match_text = f"**{home_heb}**" + (f" נגד **{away_heb}**" if away_heb else "")
                            st.markdown(match_text)
                            if team_data.get('stadium'):
                                st.caption(f"🏟️ {team_data['stadium']}")
                
                    current_key = f"{selected_league}_{team_data.get('name', '')}_{st.session_state.get('away_team_data', {}).get('name', '')}"
                    if st.session_state.get('fixture_lookup_key') != current_key:
                        st.session_state['fixture_data'] = {}
                        st.session_state['fixture_lookup_key'] = current_key
                
                    if team_data.get('name') and st.session_state.get('away_team_data', {}).get('name'):
                        home_name = team_data['name']
                        away_name = st.session_state['away_team_data']['name']
                        english_league = LEAGUES.get(selected_league, "")
                    
                        if not st.session_state.get('fixture_data'):
                            fixture = find_fixture(home_name, away_name, english_league)
                            if fixture and fixture.get('date'):
                                time_str = fixture.get('time', '')
                                if time_str and time_str not in ('00:00:00', '00:00', ''):
                                    st.session_state['fixture_data'] = fixture
                                    st.success(f"📅 נמצא משחק: {fixture['date']} {time_str[:5]}")
                                elif fixture.get('date'):
                                    st.session_state['fixture_data'] = {'date': fixture['date']}
                                    st.success(f"📅 נמצא משחק: {fixture['date']}")
        
            elif event_type == "הופעה":
                from concerts_data import get_all_venues
                from concerts_service import search_artists, get_events_by_attraction_id, get_popular_artists, format_concert_for_display, search_events_combined, search_concerts_by_location
            
                st.markdown("##### 🎤 בחירת אמן")
            
                popular_artists = get_popular_artists()
                saved_concerts = get_saved_concerts()
                saved_artists = get_saved_artists()
            
                artist_options = ["-- בחר אמן --"]
                if saved_concerts:
                    artist_options.append("⭐ הופעות שמורות")
                artist_options.append("📸 סריקת הופעה מתמונה")
                artist_options += [f"{a['name_he']} ({a['name_en']})" for a in popular_artists]
                if saved_artists:
                    artist_options += [f"⭐ {a['name_he']} ({a['name_en']})" for a in saved_artists]
                artist_options.append("🔍 חיפוש אמן אחר...")
            
                selected_artist_option = st.selectbox("🎤 אמן", artist_options, key="concert_artist_select")
            
                artist_id = None
                artist_name_en = ''
                artist_name_he = ''
            
                if selected_artist_option == "⭐ הופעות שמורות":
                    st.markdown("##### ⭐ הופעות שמורות")
                
                    if saved_concerts:
                        saved_options = ["-- בחר הופעה שמורה --"]
                        for sc in saved_concerts:
                            date_str = sc.get('date', '')
                            if date_str:
                                try:
                                    from datetime import datetime as dt
                                    date_obj = dt.strptime(date_str, '%Y-%m-%d')
                                    date_str = date_obj.strftime('%d/%m/%Y')
                                except:
                                    pass
                            artist_name = sc.get('artist_he') or sc.get('artist', '')
                            venue = sc.get('venue', '')
                            city = sc.get('city', '')
                            display = f"{artist_name} @ {venue}"
                            if city:
                                display += f", {city}"
                            if date_str:
                                display += f" ({date_str})"
                            saved_options.append(display)
                    
                        selected_saved_idx = st.selectbox(
                            "⭐ בחר הופעה שמורה",
                            range(len(saved_options)),
                            format_func=lambda i: saved_options[i],
                            key="saved_concert_select"
                        )
                    
                        if selected_saved_idx and selected_saved_idx > 0:
                            selected_saved = saved_concerts[selected_saved_idx - 1]
                            artist_name_en = selected_saved.get('artist', '')
                            artist_name_he = selected_saved.get('artist_he') or artist_name_en
                        
                            st.session_state['concert_artist_en'] = artist_name_en
                            st.session_state['concert_artist_he'] = artist_name_he
                            st.session_state['concert_venue_name'] = selected_saved.get('venue', '')
                            st.session_state['concert_venue_city'] = selected_saved.get('city', '')
                            st.session_state['_selected_concert'] = selected_saved
                            st.session_state['concert_venue_info'] = {
                                'name_he': selected_saved.get('venue', ''),
                                'city_he': selected_saved.get('city', ''),
                                'country': selected_saved.get('country', '')
                            }
                            st.session_state['concert_selected_category'] = selected_saved.get('category', 'General Admission')
                            st.session_state['_from_saved_concert'] = True
                        
                            # Load stadium map from database (base64) or file path
                            if selected_saved.get('stadium_map_data'):
                                import base64
                                from io import BytesIO
                                img_data = base64.b64decode(selected_saved.get('stadium_map_data'))
                                st.session_state['saved_stadium_map_bytes'] = img_data
                            elif selected_saved.get('stadium_map_path') and os.path.exists(selected_saved.get('stadium_map_path')):
                                with open(selected_saved.get('stadium_map_path'), 'rb') as f:
                                    st.session_state['saved_stadium_map_bytes'] = f.read()
                        
                            has_map = selected_saved.get('stadium_map_data') or (selected_saved.get('stadium_map_path') and os.path.exists(selected_saved.get('stadium_map_path', '')))
                            st.success(f"✅ נטען: {artist_name_he} @ {selected_saved.get('venue', '')}" + (" (כולל תרשים מושבים)" if has_map else ""))
                            st.caption(f"📍 {selected_saved.get('city', '')}, {selected_saved.get('country', '')} | 🎫 {selected_saved.get('category', 'General Admission')}")
                        
                            if selected_saved.get('date'):
                                st.session_state['_extracted_date'] = selected_saved.get('date', '')
                                st.session_state['_extracted_time'] = selected_saved.get('time', '')
                        
                            if selected_saved.get('url'):
                                st.markdown(f"🔗 [קישור לאירוע]({selected_saved.get('url')})")
                        
                            categories = ['VIP', 'Golden Circle', 'Floor', 'Lower Tier', 'Upper Tier', 'General Admission']
                            default_cat_idx = categories.index(selected_saved.get('category', 'General Admission')) if selected_saved.get('category') in categories else 5
                            selected_cat = st.selectbox("🎫 קטגוריית כרטיסים", categories, index=default_cat_idx, key="saved_concert_category")
                            st.session_state['concert_selected_category'] = selected_cat
                    else:
                        st.info("אין הופעות שמורות. שמור הופעות מ'הזנה ידנית' כדי לראות אותן כאן.")
            
                elif selected_artist_option == "📸 סריקת הופעה מתמונה":
                    from concert_ocr import extract_concert_data
                
                    st.markdown("##### 📸 סריקת הופעה מתמונה")
                    st.info("💡 העלה צילום מסך של דף ההופעה והמערכת תחלץ את הפרטים אוטומטית")
                
                    col_upload, col_paste = st.columns([3, 1])
                    with col_upload:
                        concert_screenshot = st.file_uploader(
                            "📷 העלה צילום מסך של דף האירוע",
                            type=['png', 'jpg', 'jpeg'],
                            key="concert_ocr_upload",
                            help="צלם מסך מאתר המכירות והעלה כאן"
                        )
                    with col_paste:
                        concert_paste = paste_image_button("📋 הדבק", key="concert_ocr_paste")
                        if concert_paste.image_data:
                            st.session_state['concert_pasted_image'] = concert_paste.image_data
                            st.image(concert_paste.image_data, caption="תמונה שהודבקה", width=100)
                
                    concert_image_to_scan = concert_screenshot or st.session_state.get('concert_pasted_image')
                
                    scan_concert_btn = st.button("🔍 סרוק פרטי הופעה", type="primary", use_container_width=True, key="scan_concert_btn")
                
                    if st.session_state.get('concert_ocr_result'):
                        ocr_result = st.session_state['concert_ocr_result']
                        st.success("✅ הסריקה הושלמה! הפרטים מולאו בטופס למטה.")
                    
                        st.markdown("**פרטים שזוהו:**")
                        if ocr_result.get('artist_name'):
                            st.write(f"🎤 אמן: {ocr_result.get('artist_name')}")
                        if ocr_result.get('event_name'):
                            st.write(f"🎭 אירוע: {ocr_result.get('event_name')}")
                        if ocr_result.get('event_date'):
                            st.write(f"📅 תאריך: {ocr_result.get('event_date')} {ocr_result.get('event_time', '')}")
                        if ocr_result.get('venue_name'):
                            st.write(f"📍 מקום: {ocr_result.get('venue_name')}, {ocr_result.get('venue_city', '')}")
                        if ocr_result.get('categories'):
                            cats = ocr_result.get('categories', [])
                            if cats:
                                st.write("🎫 קטגוריות:")
                                for cat in cats[:5]:
                                    price_str = f" - €{cat.get('price')}" if cat.get('price') else ""
                                    st.write(f"  • {cat.get('name', 'כללי')}{price_str}")
                    
                        st.session_state['concert_artist_en'] = ocr_result.get('artist_name', '')
                        st.session_state['concert_artist_he'] = ocr_result.get('artist_name', '')
                        st.session_state['concert_venue_name'] = ocr_result.get('venue_name', '')
                        st.session_state['concert_venue_city'] = ocr_result.get('venue_city', '')
                        st.session_state['concert_venue_info'] = {
                            'name_he': ocr_result.get('venue_name', ''),
                            'city_he': ocr_result.get('venue_city', ''),
                            'country': ocr_result.get('venue_country', '')
                        }
                        st.session_state['_ocr_event_name'] = ocr_result.get('event_name', '')
                        st.session_state['_ocr_event_date'] = ocr_result.get('event_date', '')
                        st.session_state['_ocr_event_time'] = ocr_result.get('event_time', '')
                        st.session_state['_ocr_categories'] = ocr_result.get('categories', [])
                    
                        if ocr_result.get('categories'):
                            cat_names = [c.get('name', 'General') for c in ocr_result.get('categories', [])]
                            selected_ocr_cat = st.selectbox("🎫 בחר קטגוריה", cat_names, key="ocr_category_select")
                            st.session_state['concert_selected_category'] = selected_ocr_cat
                    
                        st.markdown("---")
                        if st.button("⭐ שמור הופעה לשימוש חוזר", use_container_width=True, key="save_ocr_concert"):
                            from models import SavedConcert as SavedConcertModel
                            db = get_db()
                            if db:
                                try:
                                    date_str = ocr_result.get('event_date', '')
                                    try:
                                        from datetime import datetime as dt
                                        if '/' in date_str:
                                            parsed = dt.strptime(date_str, '%d/%m/%Y')
                                            date_str = parsed.strftime('%Y-%m-%d')
                                    except:
                                        pass
                                
                                    new_concert = SavedConcertModel(
                                        artist_name=ocr_result.get('artist_name', ''),
                                        artist_name_he=ocr_result.get('artist_name', ''),
                                        event_name=ocr_result.get('event_name', ''),
                                        venue_name=ocr_result.get('venue_name', ''),
                                        city=ocr_result.get('venue_city', ''),
                                        country=ocr_result.get('venue_country', ''),
                                        event_date=date_str,
                                        event_time=ocr_result.get('event_time', ''),
                                        category=st.session_state.get('concert_selected_category', 'General Admission'),
                                        source='ocr'
                                    )
                                    db.add(new_concert)
                                    db.commit()
                                    st.success("✅ ההופעה נשמרה! תוכל לבחור אותה מ'הופעות שמורות'.")
                                except Exception as e:
                                    db.rollback()
                                    st.error(f"❌ שגיאה בשמירה: {str(e)}")
                                finally:
                                    db.close()
                
                    if scan_concert_btn:
                        if concert_image_to_scan:
                            with st.spinner("🔍 סורק את פרטי ההופעה..."):
                                if concert_screenshot:
                                    image_bytes = concert_screenshot.read()
                                else:
                                    pasted_img = st.session_state['concert_pasted_image']
                                    img_byte_arr = io.BytesIO()
                                    pasted_img.save(img_byte_arr, format='PNG')
                                    image_bytes = img_byte_arr.getvalue()
                            
                                result = extract_concert_data(image_bytes)
                            
                                if result.get('success'):
                                    st.session_state['concert_ocr_result'] = result
                                    st.rerun()
                                else:
                                    st.error(f"❌ לא הצלחנו לזהות פרטי הופעה: {result.get('error', 'נסה תמונה ברורה יותר')}")
                        else:
                            st.warning("⚠️ יש להעלות צילום מסך לפני הסריקה")
            
                elif selected_artist_option == "🔍 חיפוש אמן אחר...":
                    artist_search = st.text_input(
                        "🔍 חיפוש באנגלית", 
                        value=st.session_state.get('_artist_search_query', ''),
                        placeholder="Type artist name in English...",
                        key="artist_search_input"
                    )
                    st.session_state['_artist_search_query'] = artist_search
                
                    if artist_search and len(artist_search.strip()) >= 2:
                        search_key = f"search_{artist_search.strip().lower()}"
                    
                        if st.session_state.get('_last_artist_search') != search_key:
                            st.session_state['_last_artist_search'] = search_key
                            st.session_state['_artist_results'] = []
                        
                            with st.spinner("🔍 מחפש אמנים ב-Ticketmaster..."):
                                result = search_artists(artist_search.strip())
                                if result.get('error'):
                                    st.warning(f"⚠️ שגיאה בחיפוש: {result['error']}")
                                elif result.get('artists'):
                                    st.session_state['_artist_results'] = result['artists']
                                else:
                                    st.info("לא נמצאו אמנים. נסה חיפוש אחר.")
                    
                        artist_results = st.session_state.get('_artist_results', [])
                    
                        if artist_results:
                            search_options = ["-- בחר מתוצאות החיפוש --"]
                            for a in artist_results:
                                events_txt = f" ({a.get('upcoming_events', 0)} הופעות)" if a.get('upcoming_events', 0) > 0 else ""
                                genre_txt = f" • {a.get('genre', '')}" if a.get('genre') else ""
                                search_options.append(f"{a['name']}{genre_txt}{events_txt}")
                        
                            selected_search_idx = st.selectbox(
                                "🎤 בחר אמן מתוצאות החיפוש",
                                range(len(search_options)),
                                format_func=lambda i: search_options[i],
                                key="concert_search_result_select"
                            )
                        
                            if selected_search_idx and selected_search_idx > 0:
                                selected = artist_results[selected_search_idx - 1]
                                artist_id = selected.get('id', '')
                                artist_name_en = selected.get('name', '')
                                artist_name_he = artist_name_en
                                selected_genre = selected.get('genre', '')
                                selected_image = selected.get('image_url', '')
                            
                                st.session_state['_search_selected_artist_id'] = artist_id
                                st.session_state['_search_selected_artist_name'] = artist_name_en
                                st.session_state['_search_selected_artist_genre'] = selected_genre
                                st.session_state['_search_selected_artist_image'] = selected_image
                            
                                if st.button("⭐ הוסף לאמנים שלי", key="save_artist_btn", use_container_width=True):
                                    success = save_artist_to_favorites(
                                        name_en=artist_name_en,
                                        name_he=artist_name_en,
                                        ticketmaster_id=artist_id,
                                        genre=selected_genre,
                                        image_url=selected_image
                                    )
                                    if success:
                                        st.success(f"✅ האמן {artist_name_en} נוסף לרשימה שלך!")
                                        st.rerun()
                                    else:
                                        st.error("❌ שגיאה בהוספת האמן")
                            elif st.session_state.get('_search_selected_artist_id'):
                                artist_id = st.session_state.get('_search_selected_artist_id', '')
                                artist_name_en = st.session_state.get('_search_selected_artist_name', '')
                                artist_name_he = artist_name_en
            
                elif selected_artist_option and selected_artist_option not in ["-- בחר אמן --", "🔍 חיפוש אמן אחר..."]:
                    is_saved_artist = selected_artist_option.startswith("⭐ ")
                    clean_option = selected_artist_option[2:] if is_saved_artist else selected_artist_option
                
                    artist_name_he = clean_option.split(" (")[0]
                    artist_name_en = clean_option.split("(")[-1].replace(")", "").strip()
                
                    if is_saved_artist:
                        artist_info = next((a for a in saved_artists if a['name_en'] == artist_name_en), None)
                    else:
                        artist_info = next((a for a in popular_artists if a['name_en'] == artist_name_en), None)
                
                    if artist_info:
                        artist_id = artist_info['id']
                        st.session_state['_artist_results'] = []
                        st.session_state['_artist_search_query'] = ''
                        st.session_state['_search_selected_artist_id'] = ''
                        st.session_state['_search_selected_artist_name'] = ''
            
                # For search mode, always use session state values if available
                if selected_artist_option == "🔍 חיפוש אמן אחר..." and st.session_state.get('_search_selected_artist_id'):
                    artist_id = st.session_state.get('_search_selected_artist_id', '')
                    artist_name_en = st.session_state.get('_search_selected_artist_name', '')
                    artist_name_he = artist_name_en
            
                if artist_id or (artist_name_en and selected_artist_option == "🔍 חיפוש אמן אחר..."):
                    if artist_name_en:
                        st.session_state['concert_artist_en'] = artist_name_en
                        st.session_state['concert_artist_he'] = artist_name_he or artist_name_en
                        st.session_state['_selected_artist_id'] = artist_id or ''
                
                    events_key = f"events_combined_{artist_id or artist_name_en}"
                
                    if st.session_state.get('_last_events_fetch') != events_key:
                        st.session_state['_last_events_fetch'] = events_key
                    
                        with st.spinner(f"🎫 מחפש הופעות של {artist_name_he or artist_name_en} (Ticketmaster + מקורות נוספים)..."):
                            events_result = search_events_combined(artist_name_en, artist_id or '', size=50)
                        
                            if events_result.get('error'):
                                st.warning(f"⚠️ שגיאה: {events_result['error']}")
                                st.session_state['_live_concerts'] = []
                            elif events_result.get('concerts'):
                                st.session_state['_live_concerts'] = events_result['concerts']
                                sources_text = ""
                                if events_result.get('sources'):
                                    sources_text = " (ממספר מקורות)"
                                st.success(f"🎫 נמצאו {events_result['total']} הופעות קרובות של {artist_name_he or artist_name_en} באירופה{sources_text}")
                            else:
                                st.session_state['_live_concerts'] = []
                                st.info(f"🎤 {artist_name_he or artist_name_en} - לא נמצאו הופעות קרובות באירופה")
                else:
                    if selected_artist_option == "-- בחר אמן --":
                        st.session_state['_live_concerts'] = []
                        st.session_state['_selected_artist_id'] = ''
                        st.session_state['concert_artist_en'] = ''
                        st.session_state['concert_artist_he'] = ''
                        st.session_state['_last_events_fetch'] = ''
            
                live_concerts = st.session_state.get('_live_concerts', [])
            
                if live_concerts:
                    concert_options = ["-- בחר הופעה --"]
                    for i, c in enumerate(live_concerts):
                        date_str = c.get('date', '')
                        if date_str:
                            try:
                                from datetime import datetime as dt
                                date_obj = dt.strptime(date_str, '%Y-%m-%d')
                                date_str = date_obj.strftime('%d/%m/%Y')
                            except:
                                pass
                        time_str = c.get('time', '')
                        venue = c.get('venue', '')
                        city = c.get('city', '')
                        country = c.get('country', '')
                        display = f"{date_str} {time_str} - {venue}, {city} ({country})"
                        concert_options.append(display)
                
                    concert_options.append("✏️ הזנה ידנית...")
                    manual_entry_idx = len(concert_options) - 1
                
                    prev_venue = st.session_state.get('_prev_concert_venue', '')
                    selected_concert_idx = st.selectbox(
                        "🏟️ מקום ההופעה", 
                        range(len(concert_options)),
                        format_func=lambda i: concert_options[i],
                        key="concert_venue_dropdown"
                    )
                
                    if selected_concert_idx == manual_entry_idx:
                        st.session_state['_manual_concert_entry'] = True
                    
                        # Check if coming from saved concert - preserve data
                        from_saved = st.session_state.get('_from_saved_concert', False)
                        saved_concert_data = st.session_state.get('_selected_concert', {}) if from_saved else {}
                    
                        if not from_saved:
                            st.session_state['_selected_concert'] = {}
                            st.session_state['concert_venue_name'] = ''
                            st.session_state['concert_venue_city'] = ''
                            st.session_state['_concert_venue_id'] = ''
                            st.session_state['concert_venue_info'] = {}
                        else:
                            # Pre-populate extracted_concert with saved concert data for form fields
                            if saved_concert_data and '_extracted_concert' not in st.session_state:
                                st.session_state['_extracted_concert'] = {
                                    'venue': saved_concert_data.get('venue', ''),
                                    'city': saved_concert_data.get('city', ''),
                                    'country': saved_concert_data.get('country', ''),
                                    'date': saved_concert_data.get('date', ''),
                                    'time': saved_concert_data.get('time', ''),
                                    'url': saved_concert_data.get('url', ''),
                                    'source': 'saved'
                                }
                    
                        st.markdown("---")
                        st.markdown("##### ✏️ הזנה ידנית של פרטי ההופעה")
                    
                        st.markdown("**🔗 יש לך לינק לאירוע?** הדבק אותו ונחלץ את הפרטים אוטומטית:")
                    
                        url_col1, url_col2 = st.columns([4, 1])
                        with url_col1:
                            event_url = st.text_input("🔗 לינק לאירוע", key="manual_event_url", placeholder="https://www.ticketmaster.com/...", label_visibility="collapsed")
                        with url_col2:
                            extract_btn = st.button("🔍 חלץ", key="extract_url_btn", use_container_width=True)
                    
                        if extract_btn and event_url:
                            from concerts_service import extract_concert_from_url
                            with st.spinner("מחלץ פרטי אירוע..."):
                                result = extract_concert_from_url(event_url)
                                if result.get('error'):
                                    st.error(f"❌ {result['error']}")
                                elif result.get('concert'):
                                    extracted = result['concert']
                                    st.session_state['_extracted_concert'] = extracted
                                    st.session_state['_from_saved_concert'] = False  # Reset flag since we got new data
                                    st.success(f"✅ נמצא! מקור: {extracted.get('source', 'Unknown')}")
                                    st.rerun()
                    
                        extracted = st.session_state.get('_extracted_concert', {})
                    
                        manual_venue = st.text_input("🏟️ שם מקום ההופעה *", 
                            value=extracted.get('venue', ''),
                            key="manual_venue_name", 
                            placeholder="לדוגמה: O2 Arena")
                    
                        mcol1, mcol2 = st.columns(2)
                        with mcol1:
                            manual_city = st.text_input("🌆 עיר", 
                                value=extracted.get('city', ''),
                                key="manual_venue_city", 
                                placeholder="לדוגמה: לונדון")
                        with mcol2:
                            manual_country = st.text_input("🌍 מדינה", 
                                value=extracted.get('country', ''),
                                key="manual_venue_country", 
                                placeholder="לדוגמה: אנגליה")
                    
                        if extracted.get('date') or extracted.get('time'):
                            st.caption(f"📅 תאריך שחולץ: {extracted.get('date', '')} {extracted.get('time', '')}")
                            st.session_state['_extracted_date'] = extracted.get('date', '')
                            st.session_state['_extracted_time'] = extracted.get('time', '')
                    
                        if manual_venue:
                            st.session_state['concert_venue_name'] = manual_venue
                            st.session_state['concert_venue_city'] = manual_city or ''
                            st.session_state['_concert_venue_id'] = ''
                            st.session_state['concert_venue_info'] = {
                                'name_he': manual_venue,
                                'city_he': manual_city or '',
                                'country': manual_country or ''
                            }
                        
                            categories = ['VIP', 'Golden Circle', 'Floor', 'Lower Tier', 'Upper Tier', 'General Admission']
                            selected_cat = st.selectbox("🎫 קטגוריית כרטיסים", categories, key="concert_category_dropdown")
                            st.session_state['concert_selected_category'] = selected_cat
                        
                            st.markdown("---")
                            if st.button("⭐ שמור להופעות קבועות", key="save_concert_btn_1", use_container_width=True):
                                artist_en = st.session_state.get('concert_artist_en', '')
                                artist_he = st.session_state.get('concert_artist_he', artist_en)
                                if artist_en and manual_venue:
                                    map_data = None
                                    map_mime = None
                                    if 'pasted_stadium_map' in st.session_state and st.session_state['pasted_stadium_map']:
                                        try:
                                            from io import BytesIO
                                            img_buffer = BytesIO()
                                            st.session_state['pasted_stadium_map'].save(img_buffer, format='PNG')
                                            map_data = img_buffer.getvalue()
                                            map_mime = 'image/png'
                                        except Exception as e:
                                            st.warning(f"⚠️ לא הצלחתי לשמור את התרשים: {e}")
                                
                                    success = save_concert_to_favorites(
                                        artist_name=artist_en,
                                        artist_name_he=artist_he,
                                        venue_name=manual_venue,
                                        city=manual_city,
                                        country=manual_country,
                                        event_date=extracted.get('date'),
                                        event_time=extracted.get('time'),
                                        event_url=event_url if event_url else extracted.get('url'),
                                        category=selected_cat,
                                        source=extracted.get('source', 'manual'),
                                        stadium_map_data=map_data,
                                        stadium_map_mime=map_mime
                                    )
                                    if success:
                                        st.success("✅ ההופעה נשמרה לקבועות!" + (" (כולל תרשים מושבים)" if map_data else ""))
                                    else:
                                        st.error("❌ שגיאה בשמירת ההופעה")
                                else:
                                    st.warning("⚠️ נא לבחור אמן ולהזין שם מקום ההופעה")
                        else:
                            st.warning("⚠️ נא להזין שם מקום ההופעה")
                    
                    elif selected_concert_idx and selected_concert_idx > 0:
                        st.session_state['_manual_concert_entry'] = False
                        selected_concert = live_concerts[selected_concert_idx - 1]
                        st.session_state['concert_venue_name'] = selected_concert.get('venue', '')
                        st.session_state['concert_venue_city'] = selected_concert.get('city', '')
                        st.session_state['_concert_venue_id'] = selected_concert.get('id', '')
                        st.session_state['_selected_concert'] = selected_concert
                    
                        st.caption(f"📍 {selected_concert.get('venue', '')}, {selected_concert.get('city', '')} ({selected_concert.get('country', '')})")
                    
                        if selected_concert.get('address'):
                            st.caption(f"📮 כתובת: {selected_concert.get('address', '')}")
                    
                        if selected_concert.get('capacity'):
                            st.caption(f"👥 קיבולת: {selected_concert.get('capacity', ''):,} אנשים")
                    
                        if selected_concert.get('price_min') or selected_concert.get('price_max'):
                            price_info = f"💰 מחירים: {selected_concert.get('price_min', 'N/A')} - {selected_concert.get('price_max', 'N/A')} {selected_concert.get('currency', 'EUR')}"
                            st.caption(price_info)
                    
                        if selected_concert.get('url'):
                            st.markdown(f"🎫 [מעבר לעמוד ההזמנה של Ticketmaster]({selected_concert.get('url')})")
                    
                        categories = ['VIP', 'Golden Circle', 'Floor', 'Lower Tier', 'Upper Tier', 'General Admission']
                        selected_cat = st.selectbox("🎫 קטגוריית כרטיסים", categories, key="concert_category_dropdown")
                        st.session_state['concert_selected_category'] = selected_cat
                    
                        # Save to favorites button for API concerts
                        if st.button("⭐ שמור להופעות קבועות", key="save_concert_btn_api", use_container_width=True):
                            artist_en = st.session_state.get('concert_artist_en', '')
                            artist_he = st.session_state.get('concert_artist_he', artist_en)
                            if artist_en and selected_concert.get('venue'):
                                success = save_concert_to_favorites(
                                    artist_name=artist_en,
                                    artist_name_he=artist_he,
                                    venue_name=selected_concert.get('venue', ''),
                                    city=selected_concert.get('city', ''),
                                    country=selected_concert.get('country', ''),
                                    event_date=selected_concert.get('date'),
                                    event_time=selected_concert.get('time'),
                                    event_url=selected_concert.get('url'),
                                    category=selected_cat,
                                    source='ticketmaster'
                                )
                                if success:
                                    st.success("✅ ההופעה נשמרה לקבועות!")
                                else:
                                    st.error("❌ שגיאה בשמירת ההופעה")
                            else:
                                st.warning("⚠️ נא לבחור אמן ומקום הופעה")
                    elif prev_venue != selected_concert_idx:
                        st.session_state['concert_venue_info'] = {}
                        st.session_state['concert_venue_name'] = ''
                        st.session_state['concert_venue_city'] = ''
                        st.session_state['concert_selected_category'] = ''
                        st.session_state['_concert_venue_id'] = ''
                        st.session_state['_selected_concert'] = {}
                        st.session_state['_manual_concert_entry'] = False
                    st.session_state['_prev_concert_venue'] = selected_concert_idx
                else:
                    # Check if we have a selected artist from search with no European concerts
                    has_selected_search_artist = (
                        selected_artist_option == "🔍 חיפוש אמן אחר..." and 
                        st.session_state.get('_search_selected_artist_id')
                    )
                
                    if has_selected_search_artist:
                        # Artist from search has no European concerts - go directly to manual entry
                        st.session_state['_manual_concert_entry'] = True
                    
                        st.markdown("---")
                        st.markdown("##### ✏️ הזנה ידנית של פרטי ההופעה")
                        st.info("💡 לא נמצאו הופעות אירופאיות. ניתן להזין פרטים ידנית או להדביק לינק לאירוע.")
                    
                        st.markdown("**🔗 יש לך לינק לאירוע?** הדבק אותו ונחלץ את הפרטים אוטומטית:")
                    
                        url_col1, url_col2 = st.columns([4, 1])
                        with url_col1:
                            event_url = st.text_input("🔗 לינק לאירוע", key="manual_event_url_search", placeholder="https://www.ticketmaster.com/...", label_visibility="collapsed")
                        with url_col2:
                            extract_btn = st.button("🔍 חלץ", key="extract_url_btn_search", use_container_width=True)
                    
                        if extract_btn and event_url:
                            from concerts_service import extract_concert_from_url
                            with st.spinner("מחלץ פרטי אירוע..."):
                                result = extract_concert_from_url(event_url)
                                if result.get('error'):
                                    st.error(f"❌ {result['error']}")
                                elif result.get('concert'):
                                    extracted = result['concert']
                                    st.session_state['_extracted_concert'] = extracted
                                    st.success(f"✅ נמצא! מקור: {extracted.get('source', 'Unknown')}")
                                    st.rerun()
                    
                        extracted = st.session_state.get('_extracted_concert', {})
                    
                        manual_venue = st.text_input("🏟️ שם מקום ההופעה *", 
                            value=extracted.get('venue', ''),
                            key="manual_venue_name_search", 
                            placeholder="לדוגמה: O2 Arena")
                    
                        mcol1, mcol2 = st.columns(2)
                        with mcol1:
                            manual_city = st.text_input("🌆 עיר", 
                                value=extracted.get('city', ''),
                                key="manual_venue_city_search", 
                                placeholder="לדוגמה: לונדון")
                        with mcol2:
                            manual_country = st.text_input("🌍 מדינה", 
                                value=extracted.get('country', ''),
                                key="manual_venue_country_search", 
                                placeholder="לדוגמה: אנגליה")
                    
                        if extracted.get('date') or extracted.get('time'):
                            st.caption(f"📅 תאריך שחולץ: {extracted.get('date', '')} {extracted.get('time', '')}")
                            st.session_state['_extracted_date'] = extracted.get('date', '')
                            st.session_state['_extracted_time'] = extracted.get('time', '')
                    
                        if manual_venue:
                            st.session_state['concert_venue_name'] = manual_venue
                            st.session_state['concert_venue_city'] = manual_city or ''
                            st.session_state['_concert_venue_id'] = ''
                            st.session_state['concert_venue_info'] = {
                                'name_he': manual_venue,
                                'city_he': manual_city or '',
                                'country': manual_country or ''
                            }
                        
                            categories = ['VIP', 'Golden Circle', 'Floor', 'Lower Tier', 'Upper Tier', 'General Admission']
                            selected_cat = st.selectbox("🎫 קטגוריית כרטיסים", categories, key="concert_category_dropdown_search")
                            st.session_state['concert_selected_category'] = selected_cat
                        
                            st.markdown("---")
                            if st.button("⭐ שמור להופעות קבועות", key="save_concert_btn_2", use_container_width=True):
                                artist_en = st.session_state.get('concert_artist_en', '') or st.session_state.get('_search_selected_artist_name', '')
                                artist_he = st.session_state.get('concert_artist_he', artist_en)
                                if artist_en and manual_venue:
                                    map_data = None
                                    map_mime = None
                                    if 'pasted_stadium_map' in st.session_state and st.session_state['pasted_stadium_map']:
                                        try:
                                            from io import BytesIO
                                            img_buffer = BytesIO()
                                            st.session_state['pasted_stadium_map'].save(img_buffer, format='PNG')
                                            map_data = img_buffer.getvalue()
                                            map_mime = 'image/png'
                                        except:
                                            pass
                                    success = save_concert_to_favorites(
                                        artist_name=artist_en,
                                        artist_name_he=artist_he,
                                        venue_name=manual_venue,
                                        city=manual_city,
                                        country=manual_country,
                                        event_date=extracted.get('date'),
                                        event_time=extracted.get('time'),
                                        event_url=event_url if event_url else extracted.get('url'),
                                        category=selected_cat,
                                        source=extracted.get('source', 'manual'),
                                        stadium_map_data=map_data,
                                        stadium_map_mime=map_mime
                                    )
                                    if success:
                                        st.success("✅ ההופעה נשמרה לקבועות!" + (" (כולל תרשים מושבים)" if map_data else ""))
                                    else:
                                        st.error("❌ שגיאה בשמירת ההופעה")
                                else:
                                    st.warning("⚠️ נא לבחור אמן ולהזין שם מקום ההופעה")
                        else:
                            st.warning("⚠️ נא להזין שם מקום ההופעה")
                    else:
                        # No artist selected - show generic venue list
                        venues = get_all_venues()
                        venue_options = ["-- בחר מקום הופעה --"] + [f"{v['name_he']} - {v['city_he']}" for v in venues] + ["✏️ הזנה ידנית..."]
                        manual_venue_idx = len(venue_options) - 1
                    
                        prev_venue = st.session_state.get('_prev_concert_venue', '')
                        selected_venue = st.selectbox("🏟️ מקום ההופעה", venue_options, key="concert_venue_dropdown")
                
                        if selected_venue == "✏️ הזנה ידנית...":
                            st.session_state['_manual_concert_entry'] = True
                            st.session_state['_selected_concert'] = {}
                            st.session_state['concert_venue_name'] = ''
                            st.session_state['concert_venue_city'] = ''
                            st.session_state['_concert_venue_id'] = ''
                            st.session_state['concert_venue_info'] = {}
                        
                            st.markdown("---")
                            st.markdown("##### ✏️ הזנה ידנית של פרטי ההופעה")
                        
                            st.markdown("**🔗 יש לך לינק לאירוע?** הדבק אותו ונחלץ את הפרטים אוטומטית:")
                        
                            url_col1, url_col2 = st.columns([4, 1])
                            with url_col1:
                                event_url = st.text_input("🔗 לינק לאירוע", key="manual_event_url_fallback", placeholder="https://www.ticketmaster.com/...", label_visibility="collapsed")
                            with url_col2:
                                extract_btn = st.button("🔍 חלץ", key="extract_url_btn_fallback", use_container_width=True)
                        
                            if extract_btn and event_url:
                                from concerts_service import extract_concert_from_url
                                with st.spinner("מחלץ פרטי אירוע..."):
                                    result = extract_concert_from_url(event_url)
                                    if result.get('error'):
                                        st.error(f"❌ {result['error']}")
                                    elif result.get('concert'):
                                        extracted = result['concert']
                                        st.session_state['_extracted_concert'] = extracted
                                        st.success(f"✅ נמצא! מקור: {extracted.get('source', 'Unknown')}")
                                        st.rerun()
                        
                            extracted = st.session_state.get('_extracted_concert', {})
                        
                            manual_venue = st.text_input("🏟️ שם מקום ההופעה *", 
                                value=extracted.get('venue', ''),
                                key="manual_venue_name_fallback", 
                                placeholder="לדוגמה: O2 Arena")
                        
                            mcol1, mcol2 = st.columns(2)
                            with mcol1:
                                manual_city = st.text_input("🌆 עיר", 
                                    value=extracted.get('city', ''),
                                    key="manual_venue_city_fallback", 
                                    placeholder="לדוגמה: לונדון")
                            with mcol2:
                                manual_country = st.text_input("🌍 מדינה", 
                                    value=extracted.get('country', ''),
                                    key="manual_venue_country_fallback", 
                                    placeholder="לדוגמה: אנגליה")
                        
                            if extracted.get('date') or extracted.get('time'):
                                st.caption(f"📅 תאריך שחולץ: {extracted.get('date', '')} {extracted.get('time', '')}")
                                st.session_state['_extracted_date'] = extracted.get('date', '')
                                st.session_state['_extracted_time'] = extracted.get('time', '')
                        
                            if manual_venue:
                                st.session_state['concert_venue_name'] = manual_venue
                                st.session_state['concert_venue_city'] = manual_city or ''
                                st.session_state['_concert_venue_id'] = ''
                                st.session_state['concert_venue_info'] = {
                                    'name_he': manual_venue,
                                    'city_he': manual_city or '',
                                    'country': manual_country or ''
                                }
                            
                                categories = ['VIP', 'Golden Circle', 'Floor', 'Lower Tier', 'Upper Tier', 'General Admission']
                                selected_cat = st.selectbox("🎫 קטגוריית כרטיסים", categories, key="concert_category_dropdown")
                                st.session_state['concert_selected_category'] = selected_cat
                            
                                st.markdown("---")
                                manual_artist_name = st.text_input("🎤 שם אמן (באנגלית)", key="manual_artist_fallback", placeholder="לדוגמה: Ed Sheeran")
                                if st.button("⭐ שמור להופעות קבועות", key="save_concert_btn_3", use_container_width=True):
                                    if manual_artist_name and manual_venue:
                                        map_data = None
                                        map_mime = None
                                        if 'pasted_stadium_map' in st.session_state and st.session_state['pasted_stadium_map']:
                                            try:
                                                from io import BytesIO
                                                img_buffer = BytesIO()
                                                st.session_state['pasted_stadium_map'].save(img_buffer, format='PNG')
                                                map_data = img_buffer.getvalue()
                                                map_mime = 'image/png'
                                            except:
                                                pass
                                        success = save_concert_to_favorites(
                                            artist_name=manual_artist_name,
                                            artist_name_he=manual_artist_name,
                                            venue_name=manual_venue,
                                            city=manual_city,
                                            country=manual_country,
                                            event_date=extracted.get('date'),
                                            event_time=extracted.get('time'),
                                            event_url=event_url if event_url else extracted.get('url'),
                                            category=selected_cat,
                                            source=extracted.get('source', 'manual'),
                                            stadium_map_data=map_data,
                                            stadium_map_mime=map_mime
                                        )
                                        if success:
                                            st.success("✅ ההופעה נשמרה לקבועות!" + (" (כולל תרשים מושבים)" if map_data else ""))
                                        else:
                                            st.error("❌ שגיאה בשמירת ההופעה")
                                    else:
                                        st.warning("⚠️ נא להזין שם אמן ושם מקום ההופעה")
                            else:
                                st.warning("⚠️ נא להזין שם מקום ההופעה")
                            
                        elif selected_venue and selected_venue != "-- בחר מקום הופעה --":
                            venue_he = selected_venue.split(" - ")[0]
                            venue_info = next((v for v in venues if v['name_he'] == venue_he), None)
                            if venue_info:
                                st.session_state['concert_venue_info'] = venue_info
                                st.session_state['concert_venue_name'] = venue_info['name_he']
                                st.session_state['concert_venue_city'] = venue_info['city_he']
                                st.session_state['_concert_venue_id'] = venue_info.get('id', '')
                            
                                st.caption(f"📍 {venue_info['city_he']}, {venue_info['country']} | 👥 קיבולת: {venue_info['capacity']:,}")
                            
                                categories = venue_info.get('categories', ['General Admission'])
                                selected_cat = st.selectbox("🎫 קטגוריית כרטיסים", categories, key="concert_category_dropdown")
                                st.session_state['concert_selected_category'] = selected_cat
                        elif prev_venue != selected_venue:
                            st.session_state['concert_venue_info'] = {}
                            st.session_state['concert_venue_name'] = ''
                            st.session_state['concert_venue_city'] = ''
                            st.session_state['concert_selected_category'] = ''
                            st.session_state['_concert_venue_id'] = ''
                        st.session_state['_prev_concert_venue'] = selected_venue
        
            default_event_name = rd.get('event_name', '')
            team_data = st.session_state.get('selected_team_data', {})
            home_heb = st.session_state.get('home_team_hebrew', '')
            away_heb = st.session_state.get('away_team_hebrew', '')
            if event_type == "כדורגל" and home_heb and not default_event_name:
                if away_heb:
                    default_event_name = f"{home_heb} נגד {away_heb}"
                else:
                    default_event_name = f"{home_heb} נגד "
            elif event_type == "הופעה" and not default_event_name:
                ocr_event_name = st.session_state.get('_ocr_event_name', '')
                if ocr_event_name:
                    default_event_name = ocr_event_name
                else:
                    artist_he = st.session_state.get('concert_artist_he', '')
                    venue_name = st.session_state.get('concert_venue_name', '')
                    if artist_he and venue_name:
                        default_event_name = f"הופעה של {artist_he} ב{venue_name}"
                    elif artist_he:
                        default_event_name = f"הופעה של {artist_he}"
        
            event_name = st.text_input("שם האירוע", value=default_event_name, placeholder="לדוגמה: Real Madrid vs Barcelona")
        
            fixture_data = st.session_state.get('fixture_data', {})
            selected_concert = st.session_state.get('_selected_concert', {})
            default_date = None
            default_time = None
        
            if fixture_data.get('date'):
                try:
                    from datetime import datetime as dt
                    default_date = dt.strptime(fixture_data['date'], "%Y-%m-%d").date()
                except:
                    pass
            if fixture_data.get('time'):
                try:
                    from datetime import datetime as dt
                    time_str = fixture_data['time'][:5] if len(fixture_data['time']) >= 5 else fixture_data['time']
                    default_time = dt.strptime(time_str, "%H:%M").time()
                except:
                    pass
        
            if selected_concert.get('date') and not default_date:
                try:
                    from datetime import datetime as dt
                    default_date = dt.strptime(selected_concert['date'], "%Y-%m-%d").date()
                except:
                    pass
            if selected_concert.get('time') and not default_time:
                try:
                    from datetime import datetime as dt
                    time_str = selected_concert['time'][:5] if len(selected_concert['time']) >= 5 else selected_concert['time']
                    default_time = dt.strptime(time_str, "%H:%M").time()
                except:
                    pass
        
            extracted_date = st.session_state.get('_extracted_date', '')
            extracted_time = st.session_state.get('_extracted_time', '')
            if extracted_date and not default_date:
                try:
                    from datetime import datetime as dt
                    default_date = dt.strptime(extracted_date, "%Y-%m-%d").date()
                except:
                    pass
            if extracted_time and not default_time:
                try:
                    from datetime import datetime as dt
                    time_str = extracted_time[:5] if len(extracted_time) >= 5 else extracted_time
                    default_time = dt.strptime(time_str, "%H:%M").time()
                except:
                    pass
        
            ocr_date = st.session_state.get('_ocr_event_date', '')
            ocr_time = st.session_state.get('_ocr_event_time', '')
            if ocr_date and not default_date:
                try:
                    from datetime import datetime as dt
                    default_date = dt.strptime(ocr_date, "%d/%m/%Y").date()
                except:
                    try:
                        default_date = dt.strptime(ocr_date, "%Y-%m-%d").date()
                    except:
                        pass
            if ocr_time and not default_time:
                try:
                    from datetime import datetime as dt
                    time_str = ocr_time[:5] if len(ocr_time) >= 5 else ocr_time
                    default_time = dt.strptime(time_str, "%H:%M").time()
                except:
                    pass
        
            col_date, col_time = st.columns(2)
            with col_date:
                if default_date:
                    event_date = st.date_input("תאריך האירוע", value=default_date)
                else:
                    event_date = st.date_input("תאריך האירוע")
            with col_time:
                if default_time:
                    event_time = st.time_input("שעת האירוע", value=default_time)
                else:
                    event_time = st.time_input("שעת האירוע")
        
            date_status = st.radio(
                "סטטוס התאריך",
                options=["התאריך אינו סופי", "התאריך הינו סופי"],
                index=0,
                horizontal=True,
                key="date_status_radio"
            )
            is_date_final = (date_status == "התאריך הינו סופי")
        
            seats_together = st.checkbox("🪑 ישיבה 3 יחד", value=False, key="seats_together_checkbox")
        
            default_venue = rd.get('venue', '')
            if st.session_state.get('worldcup_venue'):
                default_venue = st.session_state['worldcup_venue']
            elif event_type == "כדורגל" and team_data.get('stadium') and not default_venue:
                default_venue = f"{team_data['stadium']}, {team_data.get('stadium_location', '')}"
            elif event_type == "הופעה" and not default_venue:
                venue_name = st.session_state.get('concert_venue_name', '')
                venue_city = st.session_state.get('concert_venue_city', '')
                if venue_name and venue_city:
                    default_venue = f"{venue_name}, {venue_city}"
        
            venue = st.text_input("מקום האירוע / אצטדיון", value=default_venue, placeholder="לדוגמה: Santiago Bernabeu, Madrid")
        
            st.markdown("**🗺️ תרשים מושבים (Seat Map)**")
        
            auto_stadium_map = None
        
            wc_map = st.session_state.get('worldcup_stadium_map', '')
            if wc_map and os.path.exists(wc_map):
                auto_stadium_map = wc_map
                venue_name = st.session_state.get('fixture_data', {}).get('venue', '')
                st.success(f"✅ נמצאה מפת אצטדיון FIFA עבור {venue_name}")
                st.image(wc_map, caption="מפת קטגוריות מושבים - FIFA World Cup 2026", use_container_width=True)
            elif event_type == "כדורגל" and team_data.get('name'):
                team_name_eng = team_data.get('name', '')
                map_path = get_team_map_path(team_name_eng)
                if map_path and os.path.exists(map_path):
                    auto_stadium_map = map_path
                    st.success(f"✅ נמצאה מפת אצטדיון אוטומטית עבור {st.session_state.get('home_team_hebrew', team_name_eng)}")
                    st.image(map_path, caption="מפת אצטדיון", use_container_width=True)
            elif event_type == "הופעה":
                from concerts_data import get_venue_map_path, CONCERT_DEFAULT_BG
            
                concert_venue_info = st.session_state.get('concert_venue_info', {})
                concert_venue_id = st.session_state.get('_concert_venue_id', '')
                selected_concert = st.session_state.get('_selected_concert', {})
            
                if selected_concert:
                    venue_name = selected_concert.get('venue', '')
                    venue_city = selected_concert.get('city', '')
                    capacity = selected_concert.get('capacity', 0)
                    concert_url = selected_concert.get('url', '')
                
                    concert_map_path = None
                    if concert_venue_id:
                        # Check for existing maps with any extension
                        for map_ext in ['png', 'jpg', 'jpeg', 'gif', 'webp']:
                            possible_map = f"attached_assets/concert_venue_maps/{concert_venue_id}.{map_ext}"
                            if os.path.exists(possible_map):
                                concert_map_path = possible_map
                                break
                
                    if concert_map_path:
                        auto_stadium_map = concert_map_path
                        st.success(f"✅ נמצאה מפת מושבים שמורה עבור {venue_name}")
                        st.image(concert_map_path, caption=f"מפת מושבים - {venue_name}", use_container_width=True)
                    
                        if st.button("🗑️ מחק מפה שמורה", key=f"delete_map_{concert_venue_id}"):
                            try:
                                os.remove(concert_map_path)
                                st.success("✅ המפה נמחקה!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ שגיאה במחיקה: {str(e)}")
                    else:
                        if capacity:
                            st.info(f"🎤 **{venue_name}, {venue_city}** - קיבולת: {capacity:,} מושבים")
                        else:
                            st.info(f"🎤 **{venue_name}, {venue_city}**")
                    
                        # Try to auto-fetch map from Ticketmaster CDN
                        venue_id_tm = selected_concert.get('venue_id', '')
                        auto_map_found = False
                    
                        if venue_id_tm and not concert_map_path:
                            # Try common Ticketmaster seatmap URL patterns
                            map_patterns = [
                                f"https://media.ticketmaster.co.uk/tm/en-gb/tmimages/venue/maps/uk2/{venue_id_tm}s.gif",
                                f"https://media.ticketmaster.eu/tm/en-eu/tmimages/venue/maps/eu/{venue_id_tm}s.gif",
                                f"https://s1.ticketm.net/tm/en-us/tmimages/venue/maps/nyc/{venue_id_tm}s.gif",
                            ]
                        
                            for pattern_url in map_patterns:
                                try:
                                    headers = {'User-Agent': 'Mozilla/5.0'}
                                    test_resp = requests.head(pattern_url, headers=headers, timeout=5)
                                    if test_resp.status_code == 200:
                                        # Found a map! Download it
                                        img_resp = requests.get(pattern_url, headers=headers, timeout=15)
                                        if img_resp.status_code == 200:
                                            os.makedirs('attached_assets/concert_venue_maps', exist_ok=True)
                                            ext = 'gif' if 'gif' in pattern_url else 'png'
                                            save_path = f'attached_assets/concert_venue_maps/{concert_venue_id}.{ext}'
                                            with open(save_path, 'wb') as f:
                                                f.write(img_resp.content)
                                            st.success(f"✅ נמצאה והורדה מפת מושבים אוטומטית!")
                                            auto_map_found = True
                                            concert_map_path = save_path
                                            st.image(save_path, caption=f"מפת מושבים - {venue_name}", use_container_width=True)
                                            break
                                except:
                                    continue
                    
                        if not auto_map_found:
                            st.markdown("**📥 הדבק מפת מושבים** (תישמר לשימוש עתידי)")
                        
                            venue_url = selected_concert.get('venue_url', '')
                            if venue_url:
                                st.markdown(f"🔗 [לחץ כאן לפתוח את עמוד האולם ב-Ticketmaster]({venue_url})")
                            elif concert_url:
                                st.markdown(f"🔗 [לחץ כאן לפתוח את דף האירוע ב-Ticketmaster]({concert_url})")
                        
                            st.info("📋 **צלם את מפת המושבים עם מספריים (Win+Shift+S) והדבק כאן:**")
                        
                            from streamlit_paste_button import paste_image_button as pbutton
                        
                            paste_result = pbutton(
                                label="📋 הדבק מפה מהמספריים (Ctrl+V)",
                                key=f"paste_map_{concert_venue_id}"
                            )
                        
                            if paste_result and paste_result.image_data:
                                try:
                                    os.makedirs('attached_assets/concert_venue_maps', exist_ok=True)
                                    save_path = f'attached_assets/concert_venue_maps/{concert_venue_id}.png'
                                    paste_result.image_data.save(save_path, 'PNG')
                                    st.success("✅ המפה נשמרה! היא תופיע אוטומטית בפעם הבאה שתבחר את ההופעה הזו.")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ שגיאה בשמירה: {str(e)}")
            
                elif concert_venue_info:
                    venue_name_he = concert_venue_info.get('name_he', '')
                    capacity = concert_venue_info.get('capacity', 0)
                    categories = concert_venue_info.get('categories', [])
                
                    specific_venue_map = get_venue_map_path(concert_venue_id, use_fallback=False)
                    if specific_venue_map and os.path.exists(specific_venue_map):
                        auto_stadium_map = specific_venue_map
                        st.success(f"✅ נמצאה מפת מושבים אוטומטית עבור {venue_name_he}")
                        st.image(specific_venue_map, caption=f"מפת מושבים - {venue_name_he}", use_container_width=True)
                    else:
                        venue_map_fallback = get_venue_map_path(concert_venue_id, use_fallback=True)
                        if venue_map_fallback and os.path.exists(venue_map_fallback):
                            auto_stadium_map = venue_map_fallback
                            st.info(f"🎤 **{venue_name_he}** - קיבולת: {capacity:,} מושבים\n\n📍 קטגוריות זמינות: {', '.join(categories)}")
                            st.caption("תמונת אווירה כללית תופיע במסמך. ניתן להעלות מפת מושבים ספציפית:")
                        else:
                            st.info(f"🎤 **{venue_name_he}** - קיבולת: {capacity:,} מושבים\n\n📍 קטגוריות זמינות: {', '.join(categories)}")
                            st.markdown("*העלה תרשים מושבים של האולם להצגה במסמך ההזמנה:*")
        
            stadium_image = None
        
            # Check for saved concert map bytes first (from database)
            saved_map_bytes = st.session_state.get('saved_stadium_map_bytes')
            if saved_map_bytes:
                from io import BytesIO
                st.success("✅ תרשים מושבים מההופעה השמורה")
                st.image(saved_map_bytes, caption="תרשים מושבים (מההופעה השמורה)", use_container_width=True)
                stadium_image = Image.open(BytesIO(saved_map_bytes))
                if st.button("🗑️ הסר תרשים", key="remove_saved_map"):
                    del st.session_state['saved_stadium_map_bytes']
                    st.rerun()
            elif 'pasted_stadium_map' in st.session_state and st.session_state['pasted_stadium_map']:
                stadium_image = st.session_state['pasted_stadium_map']
                st.image(stadium_image, caption="תרשים מושבים (מהלוח)", use_container_width=True)
                if st.button("🗑️ הסר תרשים", key="remove_pasted_map"):
                    del st.session_state['pasted_stadium_map']
                    st.rerun()
            else:
                col_paste, col_upload = st.columns([1, 1])
                with col_paste:
                    paste_map = paste_image_button(
                        label="📋 הדבק תרשים מהלוח",
                        key="paste_stadium_map",
                        background_color="#667eea",
                        hover_background_color="#5a6fd6"
                    )
                    if paste_map and paste_map.image_data:
                        st.session_state['pasted_stadium_map'] = paste_map.image_data
                        st.rerun()
            
                with col_upload:
                    uploaded_map = st.file_uploader("📁 העלה קובץ", type=['png', 'jpg', 'jpeg'], key="upload_stadium_map")
                    if uploaded_map:
                        st.session_state['pasted_stadium_map'] = Image.open(uploaded_map)
                        st.rerun()
            
                if not auto_stadium_map:
                    st.caption("💡 ניתן גם להשתמש בכלי **🗺️ הורדת מפות** בסרגל הכלים")
        
            stadium_photo = None
        
            # === SAVE EVENT BUTTONS (MOVED HERE - BEFORE HOTEL/FLIGHTS) ===
            st.markdown("---")
            st.markdown("---")
        
            event_label = {
                'concert': 'הופעה',
                'football': 'משחק כדורגל',
                'worldcup_2026': 'משחק מונדיאל'
            }.get(st.session_state.get('event_type_selected'), 'אירוע')
        
            col_add, col_finish, col_skip = st.columns([2, 2, 1])
        
            # Shared save logic function
            def save_current_game():
                game_data = {
                    'event_type': event_type,
                    'home_team_hebrew': st.session_state.get('home_team_hebrew', ''),
                    'away_team_hebrew': st.session_state.get('away_team_hebrew', ''),
                    'selected_team_data': st.session_state.get('selected_team_data', {}),
                    'away_team_data': st.session_state.get('away_team_data', {}),
                    'fixture_data': st.session_state.get('fixture_data', {}),
                    'concert_artist_en': st.session_state.get('concert_artist_en', ''),
                    'concert_artist_he': st.session_state.get('concert_artist_he', ''),
                    'concert_venue_name': st.session_state.get('concert_venue_name', ''),
                    'concert_venue_city': st.session_state.get('concert_venue_city', ''),
                    'concert_venue_info': st.session_state.get('concert_venue_info', {}),
                    'concert_selected_category': st.session_state.get('concert_selected_category', ''),
                    'worldcup_venue': st.session_state.get('worldcup_venue', ''),
                    'worldcup_category': st.session_state.get('worldcup_category', ''),
                    'worldcup_stadium_map': st.session_state.get('worldcup_stadium_map', ''),
                    'saved_stadium_map_bytes': st.session_state.get('saved_stadium_map_bytes', None),
                    'pasted_stadium_map': st.session_state.get('pasted_stadium_map', None),
                    'football_league': st.session_state.get('football_league', ''),
                    '_extracted_date': st.session_state.get('_extracted_date', ''),
                    '_extracted_time': st.session_state.get('_extracted_time', '')
                }
            
                # Persist league stadium map path so PDF can show it (league maps from stadium_maps/ are not in worldcup/saved_bytes)
                if event_type == "כדורגל":
                    team_data = st.session_state.get('selected_team_data', {}) or game_data.get('selected_team_data', {})
                    if isinstance(team_data, dict) and team_data.get('name'):
                        league_map = get_team_map_path(team_data['name'])
                        if league_map and os.path.exists(league_map):
                            game_data['league_stadium_map_path'] = league_map
                # Create display text
                if event_type == "כדורגל":
                    home = game_data.get('home_team_hebrew', '')
                    away = game_data.get('away_team_hebrew', '')
                    if home and away:
                        game_data['display_text'] = f"{home} נגד {away}"
                        fixture = game_data.get('fixture_data', {})
                        if fixture.get('date'):
                            game_data['details'] = f"📅 {fixture['date']}"
                            if fixture.get('time'):
                                game_data['details'] += f" ⏰ {fixture['time']}"
                    else:
                        game_data['display_text'] = "משחק כדורגל"
                elif event_type == "הופעה":
                    artist = game_data.get('concert_artist_he') or game_data.get('concert_artist_en', '')
                    venue = game_data.get('concert_venue_name', '')
                    city = game_data.get('concert_venue_city', '')
                    if artist:
                        game_data['display_text'] = f"{artist}"
                        if venue:
                            game_data['details'] = f"📍 {venue}"
                            if city:
                                game_data['details'] += f", {city}"
                    else:
                        game_data['display_text'] = "הופעה"
            
                st.session_state['saved_games'].append(game_data)
            
                # Clear current event data for next one
                event_keys_to_clear = [
                    'selected_team_data', 'away_team_data', 'home_team_hebrew', 'away_team_hebrew',
                    'football_league', 'fixture_data', 'worldcup_match', 'worldcup_venue', 'worldcup_stadium_map',
                    'worldcup_category', 'concert_artist_en', 'concert_artist_he', 'concert_venue_name',
                    'concert_venue_city', 'concert_venue_info', 'concert_selected_category', '_concert_venue_id',
                    '_selected_concert', '_from_saved_concert', 'pasted_stadium_map', 'saved_stadium_map_bytes',
                    '_extracted_date', '_extracted_time', '_artist_results', '_live_concerts', '_selected_artist_id',
                    '_last_events_fetch', '_manual_concert_entry', '_extracted_concert', 'concert_ocr_result',
                    'concert_pasted_image', '_prev_concert_venue', '_artist_search_query', '_last_artist_search',
                    '_search_selected_artist_id', '_search_selected_artist_name', 'fixture_lookup_key',
                    '_prev_football_mode'
                ]
                for key in event_keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
        
            with col_add:
                if st.button(f"💾 שמור והוסף עוד", type="primary", use_container_width=True, key="save_and_add_another"):
                    save_current_game()
                    st.success(f"✅ {event_label} נשמר! תוכל להוסיף עוד אחד.")
                    st.rerun()
        
            with col_finish:
                if st.button(f"✅ שמור וסיים", type="secondary", use_container_width=True, key="save_and_finish"):
                    save_current_game()
                    st.session_state['finished_adding_games'] = True
                    st.success(f"✅ {event_label} נשמר! ממשיך לשאר הטופס...")
                    st.rerun()
        
            with col_skip:
                st.caption("← או דלג אם זה המשחק האחרון")
        
            st.markdown("---")
            # === END SAVE EVENT SECTION ===
        
        st.markdown("---")
        hotel_image = None
        hotel_image_2 = None
        
        if product_type == "package":
            st.markdown('<div class="form-section"><h3>🏨 פרטי המלון והטיסה</h3></div>', unsafe_allow_html=True)
            
            if 'hotel_data' not in st.session_state:
                st.session_state.hotel_data = {}
            
            hd = st.session_state.hotel_data
            
            if hd.get('hotel_image_path') and os.path.exists(hd.get('hotel_image_path', '')):
                hotel_image = hd.get('hotel_image_path')
            if hd.get('hotel_image_path_2') and os.path.exists(hd.get('hotel_image_path_2', '')):
                hotel_image_2 = hd.get('hotel_image_path_2')
            
            if hd.get('from_package') and hd.get('hotel_address'):
                st.success(f"✅ פרטי המלון נטענו מהחבילה: {hd.get('hotel_name', '')}")
            
            col_hotel, col_btn = st.columns([3, 1])
            with col_hotel:
                hotel_name = st.text_input("שם המלון", value=hd.get('hotel_name') or rd.get('hotel_name', ''), placeholder="לדוגמה: Hilton Madrid")
            with col_btn:
                st.markdown("<br>", unsafe_allow_html=True)
                lookup_hotel = st.button("🔍 חפש מלון", use_container_width=True)
            
            if lookup_hotel and hotel_name:
                city = venue.split(',')[-1].strip() if ',' in venue else ''
                query = f"{hotel_name}, {city}" if city else hotel_name
                
                with st.spinner("מחפש פרטי מלון..."):
                    result = resolve_hotel_safe(query)
                    
                    if result.get('error'):
                        st.error(f"❌ {result['error']}")
                    else:
                        if result.get('hotel_rating'):
                            rating = float(result['hotel_rating'])
                            if rating >= 4.5:
                                result['hotel_stars'] = "5 כוכבים"
                            elif rating >= 3.5:
                                result['hotel_stars'] = "4 כוכבים"
                            else:
                                result['hotel_stars'] = "3 כוכבים"
                        st.session_state.hotel_data = result
                        if result.get('from_cache'):
                            st.success(f"✅ נמצא (מהזיכרון): {result.get('hotel_name', hotel_name)}")
                        else:
                            st.success(f"✅ נמצא: {result.get('hotel_name', hotel_name)}")
                        if result.get('hotel_rating'):
                            st.info(f"⭐ דירוג: {result['hotel_rating']} ({result.get('hotel_stars', '')})")
                        st.rerun()
            
            if hd.get('hotel_address'):
                st.markdown(f"""
                <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; border-right: 4px solid #667eea; margin: 0.5rem 0;">
                    <p style="color: #333; margin: 5px 0;"><strong>📍 כתובת:</strong> {hd.get('hotel_address', '')}</p>
                    <p style="color: #333; margin: 5px 0;"><strong>🌐 אתר:</strong> {hd.get('hotel_website', 'לא זמין')}</p>
                    <p style="color: #333; margin: 5px 0;"><strong>⭐ דירוג:</strong> {hd.get('hotel_rating', 'לא זמין')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            col_nights, col_stars = st.columns(2)
            with col_nights:
                hotel_nights = st.number_input("מספר לילות", min_value=1, value=int(rd.get('hotel_nights') or 3))
            with col_stars:
                stars_options = ["3 כוכבים", "4 כוכבים", "5 כוכבים"]
                default_stars = hd.get('hotel_stars') or rd.get('hotel_stars', '5 כוכבים')
                stars_default = stars_options.index(default_stars) if default_stars in stars_options else 2
                hotel_stars = st.selectbox("דירוג המלון", stars_options, index=stars_default)
            
            meals_options = ["ללא ארוחות", "ארוחת בוקר", "חצי פנסיון", "פנסיון מלא"]
            meals_default = meals_options.index(rd.get('hotel_meals', 'ארוחת בוקר')) if rd.get('hotel_meals') in meals_options else 1
            hotel_meals = st.selectbox("ארוחות", meals_options, index=meals_default)
            
            st.markdown("**✈️ פרטי טיסות**")
            
            if 'flights_data' not in st.session_state:
                if rd.get('outbound_from'):
                    st.session_state.flights_data = {
                        'outbound': {'from': rd.get('outbound_from', 'TLV'), 'to': rd.get('outbound_to', ''), 'date': rd.get('outbound_date', ''), 'time': rd.get('outbound_time', ''), 'flight_no': rd.get('outbound_flight', ''), 'airline': rd.get('outbound_airline', '')},
                        'return': {'from': rd.get('return_from', ''), 'to': rd.get('return_to', 'TLV'), 'date': rd.get('return_date', ''), 'time': rd.get('return_time', ''), 'flight_no': rd.get('return_flight', ''), 'airline': rd.get('return_airline', '')}
                    }
                else:
                    st.session_state.flights_data = {
                        'outbound': {'from': 'TLV', 'to': '', 'date': '', 'time': '', 'flight_no': '', 'airline': ''},
                        'return': {'from': '', 'to': 'TLV', 'date': '', 'time': '', 'flight_no': '', 'airline': ''}
                    }
            
            fd = st.session_state.flights_data
            airport_options = [""] + get_airport_options()
            
            st.markdown("""
            <div style="background: linear-gradient(135deg, #667eea22, #764ba222); padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #667eea44;">
                <p style="margin: 0; font-size: 14px;">📷 <strong>סריקת טיסות אוטומטית:</strong> העלה צילום מסך של פרטי הטיסות והמערכת תמלא את השדות!</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_flight_upload, col_flight_paste = st.columns([3, 1])
            with col_flight_upload:
                flight_screenshot = st.file_uploader(
                    "📷 העלה צילום מסך של טיסות",
                    type=['png', 'jpg', 'jpeg'],
                    key="flight_scan_upload",
                    help="צלם מסך מאתר הזמנת הטיסות והעלה כאן"
                )
            with col_flight_paste:
                flight_paste = paste_image_button("📋 הדבק טיסות", key="flight_paste")
                if flight_paste.image_data:
                    st.session_state['pasted_flight'] = flight_paste.image_data
                    st.image(flight_paste.image_data, caption="צילום מסך שהודבק", width=100)
            
            scan_flights_btn = st.button("🔍 סרוק פרטי טיסות", type="secondary", use_container_width=True)
            
            flight_image_to_scan = flight_screenshot or st.session_state.get('pasted_flight')
            if scan_flights_btn and flight_image_to_scan:
                with st.spinner("סורק פרטי טיסות..."):
                    if flight_screenshot:
                        image_bytes = flight_screenshot.read()
                    else:
                        pasted_img = st.session_state['pasted_flight']
                        img_byte_arr = io.BytesIO()
                        pasted_img.save(img_byte_arr, format='PNG')
                        image_bytes = img_byte_arr.getvalue()
                    result = extract_flight_data(image_bytes)
                    
                    if result.get('success') and result.get('flights'):
                        flights = result['flights']
                        
                        for f in flights:
                            direction = f.get('direction', 'outbound')
                            if direction in ['outbound', 'return']:
                                for key in [f"flight_{direction}_from", f"flight_{direction}_to", 
                                           f"flight_{direction}_date", f"flight_{direction}_time", 
                                           f"flight_{direction}_no", f"flight_{direction}_airline"]:
                                    if key in st.session_state:
                                        del st.session_state[key]
                                
                                from_code = f.get('from', '').upper().strip()
                                to_code = f.get('to', '').upper().strip()
                                flight_no = f.get('flight_no', '')
                                airline = f.get('airline', '') or get_airline_from_flight(flight_no)
                                
                                st.session_state.flights_data[direction] = {
                                    'from': from_code,
                                    'to': to_code,
                                    'date': f.get('date', ''),
                                    'time': f.get('time', ''),
                                    'flight_no': flight_no,
                                    'airline': airline
                                }
                                
                                from_display = format_airport_display(from_code) if from_code else ""
                                to_display = format_airport_display(to_code) if to_code else ""
                                
                                st.session_state[f"flight_{direction}_from"] = from_display
                                st.session_state[f"flight_{direction}_to"] = to_display
                                st.session_state[f"flight_{direction}_date"] = f.get('date', '')
                                st.session_state[f"flight_{direction}_time"] = f.get('time', '')
                                st.session_state[f"flight_{direction}_no"] = f.get('flight_no', '')
                                st.session_state[f"flight_{direction}_airline"] = airline
                        
                        st.success(f"✅ נסרקו {len(flights)} טיסות!")
                        st.rerun()
                    else:
                        st.error(f"❌ לא הצלחנו לזהות פרטי טיסות: {result.get('error', 'נסה תמונה ברורה יותר')}")
            elif scan_flights_btn and not flight_screenshot:
                st.warning("⚠️ יש להעלות צילום מסך לפני הסריקה")
            
            st.markdown("**טיסת הלוך:**")
            col_out1, col_out2 = st.columns(2)
            with col_out1:
                if "flight_outbound_from" not in st.session_state:
                    out_from_default = format_airport_display(fd['outbound'].get('from', 'TLV')) if fd['outbound'].get('from') else airport_options[0]
                    st.session_state["flight_outbound_from"] = out_from_default
                outbound_from = st.selectbox("מ:", airport_options, key="flight_outbound_from")
            with col_out2:
                if "flight_outbound_to" not in st.session_state:
                    out_to_default = format_airport_display(fd['outbound'].get('to', '')) if fd['outbound'].get('to') else airport_options[0]
                    st.session_state["flight_outbound_to"] = out_to_default
                outbound_to = st.selectbox("אל:", airport_options, key="flight_outbound_to")
            
            col_out3, col_out4, col_out5 = st.columns(3)
            with col_out3:
                if "flight_outbound_date" not in st.session_state:
                    st.session_state["flight_outbound_date"] = fd['outbound'].get('date', '')
                outbound_date = st.text_input("תאריך", placeholder="15/01", key="flight_outbound_date")
            with col_out4:
                if "flight_outbound_time" not in st.session_state:
                    st.session_state["flight_outbound_time"] = fd['outbound'].get('time', '')
                outbound_time = st.text_input("שעה", placeholder="09:00", key="flight_outbound_time")
            with col_out5:
                if "flight_outbound_no" not in st.session_state:
                    st.session_state["flight_outbound_no"] = fd['outbound'].get('flight_no', '')
                outbound_no = st.text_input("מס' טיסה", placeholder="LY315", key="flight_outbound_no")
            
            # Auto-detect airline from flight number
            detected_outbound_airline = ""
            if outbound_no:
                detected_outbound_airline = get_airline_from_flight(outbound_no)
                if detected_outbound_airline:
                    st.caption(f"✓ זוהה: {detected_outbound_airline}")
            
            # Initialize with detected value or from saved data
            default_outbound_airline = detected_outbound_airline or fd['outbound'].get('airline', '')
            outbound_airline = st.text_input("חברת תעופה", value=default_outbound_airline, placeholder="Air Europa", key="flight_outbound_airline")
            
            st.markdown("**טיסת חזור:**")
            col_ret1, col_ret2 = st.columns(2)
            with col_ret1:
                if "flight_return_from" not in st.session_state:
                    ret_from_default = format_airport_display(fd['return'].get('from', '')) if fd['return'].get('from') else airport_options[0]
                    st.session_state["flight_return_from"] = ret_from_default
                return_from = st.selectbox("מ:", airport_options, key="flight_return_from")
            with col_ret2:
                if "flight_return_to" not in st.session_state:
                    ret_to_default = format_airport_display(fd['return'].get('to', 'TLV')) if fd['return'].get('to') else airport_options[0]
                    st.session_state["flight_return_to"] = ret_to_default
                return_to = st.selectbox("אל:", airport_options, key="flight_return_to")
            
            col_ret3, col_ret4, col_ret5 = st.columns(3)
            with col_ret3:
                if "flight_return_date" not in st.session_state:
                    st.session_state["flight_return_date"] = fd['return'].get('date', '')
                return_date = st.text_input("תאריך", placeholder="18/01", key="flight_return_date")
            with col_ret4:
                if "flight_return_time" not in st.session_state:
                    st.session_state["flight_return_time"] = fd['return'].get('time', '')
                return_time = st.text_input("שעה", placeholder="22:00", key="flight_return_time")
            with col_ret5:
                if "flight_return_no" not in st.session_state:
                    st.session_state["flight_return_no"] = fd['return'].get('flight_no', '')
                return_no = st.text_input("מס' טיסה", placeholder="LY316", key="flight_return_no")
            
            # Auto-detect airline from return flight number
            detected_return_airline = ""
            if return_no:
                detected_return_airline = get_airline_from_flight(return_no)
                if detected_return_airline:
                    st.caption(f"✓ זוהה: {detected_return_airline}")
            
            # Initialize with detected value or from saved data
            default_return_airline = detected_return_airline or fd['return'].get('airline', '')
            return_airline = st.text_input("חברת תעופה", value=default_return_airline, placeholder="El Al", key="flight_return_airline")
            
            out_from_code = get_airport_code(outbound_from)
            out_to_code = get_airport_code(outbound_to)
            ret_from_code = get_airport_code(return_from)
            ret_to_code = get_airport_code(return_to)
            
            flights_list = []
            if out_from_code and out_to_code:
                flights_list.append({
                    'direction': 'הלוך',
                    'from': out_from_code,
                    'to': out_to_code,
                    'date': outbound_date,
                    'time': outbound_time,
                    'flight_no': outbound_no,
                    'airline': outbound_airline
                })
            if ret_from_code and ret_to_code:
                flights_list.append({
                    'direction': 'חזור',
                    'from': ret_from_code,
                    'to': ret_to_code,
                    'date': return_date,
                    'time': return_time,
                    'flight_no': return_no,
                    'airline': return_airline
                })
            
            flight_details = ""
            if flights_list:
                lines = []
                for f in flights_list:
                    line = f"{f['direction']}: {f['from']}-{f['to']}"
                    if f['date']:
                        line += f" {f['date']}"
                    if f['time']:
                        line += f" {f['time']}"
                    if f.get('airline') and f.get('flight_no'):
                        line += f" ({f['airline']} - {f['flight_no']})"
                    elif f.get('flight_no'):
                        line += f" ({f['flight_no']})"
                    lines.append(line)
                flight_details = "\n".join(lines)
            
            st.markdown("**🧳 כבודה:**")
            col_bag1, col_bag2 = st.columns(2)
            with col_bag1:
                bag_trolley = st.checkbox("כולל טרולי עד 7 ק\"ג", value=rd.get('bag_trolley', True), key="bag_trolley")
            with col_bag2:
                bag_options = ["ללא כבודה רשומה", "כולל כבודה עד 20 ק\"ג", "כולל כבודה עד 23 ק\"ג", "כולל כבודה עד 25 ק\"ג"]
                bag_default_idx = 0
                if rd.get('bag_checked'):
                    for i, opt in enumerate(bag_options):
                        if rd.get('bag_checked') in opt:
                            bag_default_idx = i
                            break
                bag_checked = st.selectbox("כבודה רשומה:", bag_options, index=bag_default_idx, key="bag_checked")
            
            transfers = st.checkbox("כולל העברות משדה התעופה", value=rd.get('transfers', True))
            
        else:
            hotel_name = ""
            hotel_nights = 0
            hotel_stars = ""
            hotel_meals = ""
            flight_details = ""
            flights_list = []
            transfers = False
            bag_trolley = False
            bag_checked = ""
        
        st.markdown('<div class="form-section"><h3>👤 פרטי הלקוח</h3></div>', unsafe_allow_html=True)
        
        customer_name = st.text_input("שם מלא", value=rd.get('customer_name', ''), placeholder="ישראל ישראלי")
        
        col_id, col_phone = st.columns(2)
        with col_id:
            customer_id = st.text_input("תעודת זהות", value=rd.get('customer_id', ''), placeholder="123456789")
        with col_phone:
            customer_phone = st.text_input("טלפון", value=rd.get('customer_phone', ''), placeholder="050-1234567")
        
        customer_email = st.text_input("אימייל", value=rd.get('customer_email', ''), placeholder="example@email.com")
        
        st.markdown('<div class="form-section"><h3>🎫 פרטי הכרטיסים</h3></div>', unsafe_allow_html=True)
        
        ticket_description = st.text_area(
            "תיאור הכרטיסים",
            value=rd.get('ticket_description', ''),
            placeholder="לדוגמה: שני כרטיסים בישיבה בטבעת הרביעית מאחורי השער",
            height=80
        )
        
        default_category = rd.get('category', '')
        if not default_category:
            if event_type == "כדורגל" and st.session_state.get('worldcup_category'):
                default_category = st.session_state.get('worldcup_category', '')
            elif event_type == "הופעה" and st.session_state.get('concert_selected_category'):
                default_category = st.session_state.get('concert_selected_category', '')
        
        category = st.text_input("קטגוריה", value=default_category, placeholder="CAT 1 / VIP / Premium")
        
        from exchange_rates import fetch_exchange_rates, get_currency_symbol, get_currency_name_hebrew
        
        currency_options = ['EUR', 'USD', 'GBP']
        currency_labels = ['€ יורו', '$ דולר', '£ פאונד']
        
        col_currency, col_price, col_qty = st.columns([1, 1, 1])
        with col_currency:
            selected_currency = st.selectbox(
                "מטבע", 
                currency_options,
                format_func=lambda x: currency_labels[currency_options.index(x)]
            )
        with col_price:
            currency_symbol = get_currency_symbol(selected_currency)
            currency_name = get_currency_name_hebrew(selected_currency)
            price_foreign = st.number_input(f"מחיר לאדם ({currency_symbol})", min_value=0, value=int(rd.get('price_euro') or 330))
        with col_qty:
            num_tickets = st.number_input("מספר כרטיסים", min_value=1, value=int(rd.get('num_tickets') or 2))
        
        rates = fetch_exchange_rates()
        exchange_rate = rates.get(selected_currency, 3.78)
        
        st.markdown(f"""
        <div style="background: #f0f2f6; padding: 10px; border-radius: 8px; margin: 10px 0;">
            📊 שער המרה ({currency_name} לשקל): <strong>{exchange_rate}</strong> ₪ 
            <span style="color: #666; font-size: 12px;">(כולל מרווח 5 אג')</span>
        </div>
        """, unsafe_allow_html=True)
        
        price_nis = int(price_foreign * exchange_rate)
        total_foreign = price_foreign * num_tickets
        total_nis = int(total_foreign * exchange_rate)
        
        st.markdown(f"""
        <div class="price-display">
            💰 סה"כ: {total_foreign} {currency_symbol} = {total_nis:,} ש"ח
        </div>
        """, unsafe_allow_html=True)
        
        price_euro = price_foreign if selected_currency == 'EUR' else 0
        total_euro = total_foreign if selected_currency == 'EUR' else 0
        
        st.markdown('<div class="form-section"><h3>✈️ פרטי הנוסעים</h3></div>', unsafe_allow_html=True)
        
        if 'passenger_list' not in st.session_state:
            st.session_state.passenger_list = [{
                'first_name': '', 
                'last_name': '', 
                'passport': '', 
                'birth_date': '',
                'passport_expiry': '',
                'ticket_type': 'כרטיס רגיל'
            }]
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #667eea22, #764ba222); padding: 15px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #667eea44;">
            <p style="margin: 0; font-size: 14px;">📷 <strong>סריקת דרכונים אוטומטית:</strong> העלה תמונות דרכונים - כל דרכון יוסיף נוסע חדש עם הפרטים שנסרקו!</p>
        </div>
        """, unsafe_allow_html=True)
        
        col_passport_upload, col_passport_paste = st.columns([3, 1])
        with col_passport_upload:
            passport_uploads = st.file_uploader(
                "📷 העלה תמונות דרכונים (ניתן להעלות מספר קבצים)",
                type=['png', 'jpg', 'jpeg'],
                key="passport_scan_upload",
                accept_multiple_files=True,
                help="העלה צילומים ברורים של דרכונים - כל דרכון יוסיף נוסע חדש"
            )
        with col_passport_paste:
            # Initialize
            if 'pasted_passports' not in st.session_state:
                st.session_state['pasted_passports'] = []
            if '_passport_paste_refresh' not in st.session_state:
                st.session_state['_passport_paste_refresh'] = 0
            
            # Dynamic key with refresh counter
            paste_key = f"passport_paste_{st.session_state['_passport_paste_refresh']}"
            passport_paste = paste_image_button("📋 הדבק דרכון", key=paste_key)
            
            if passport_paste.image_data:
                # Add to list and force component refresh
                st.session_state['pasted_passports'].append(passport_paste.image_data)
                st.session_state['_passport_paste_refresh'] += 1
                st.success(f"✅ דרכון {len(st.session_state['pasted_passports'])} נוסף!")
                st.rerun()
        
        # Display all pasted passports
        if st.session_state.get('pasted_passports'):
            st.info(f"📋 {len(st.session_state['pasted_passports'])} דרכונים מהלוח מוכנים לסריקה")
            cols = st.columns(min(len(st.session_state['pasted_passports']), 5))
            for i, pasted_img in enumerate(st.session_state['pasted_passports']):
                with cols[i % 5]:
                    st.image(pasted_img, caption=f"#{i+1}", width=80)
            if st.button("🗑️ מחק הכל", key="clear_all_pasted"):
                st.session_state['pasted_passports'] = []
                st.session_state['_passport_paste_refresh'] += 1
                st.rerun()
        
        has_passport_input = passport_uploads or st.session_state.get('pasted_passports')
        if passport_uploads:
            st.info(f"📁 {len(passport_uploads)} דרכונים הועלו")
        
        scan_button = st.button("🔍 סרוק דרכונים והוסף נוסעים", type="primary", use_container_width=True)
        
        if scan_button and has_passport_input:
            progress_bar = st.progress(0)
            status_text = st.empty()
            scanned_passengers = []
            
            images_to_scan = []
            if passport_uploads:
                for pf in passport_uploads:
                    images_to_scan.append(('file', pf))
            if st.session_state.get('pasted_passports'):
                for pasted_img in st.session_state['pasted_passports']:
                    images_to_scan.append(('pasted', pasted_img))
            
            for idx, (source_type, passport_data) in enumerate(images_to_scan):
                source_name = f"דרכון מהלוח" if source_type == 'pasted' else passport_data.name
                status_text.text(f"🔄 סורק {source_name} ({idx + 1} מתוך {len(images_to_scan)})...")
                progress_bar.progress((idx + 1) / len(images_to_scan))
                
                if source_type == 'file':
                    image_bytes = passport_data.read()
                else:
                    img_byte_arr = io.BytesIO()
                    passport_data.save(img_byte_arr, format='PNG')
                    image_bytes = img_byte_arr.getvalue()
                
                result = extract_passport_data(image_bytes)
                
                if result.get('success'):
                    scanned_passengers.append({
                        'first_name': result.get('first_name', ''),
                        'last_name': result.get('last_name', ''),
                        'passport': result.get('passport_number', ''),
                        'birth_date': result.get('birth_date', ''),
                        'passport_expiry': result.get('passport_expiry', ''),
                        'ticket_type': 'כרטיס רגיל'
                    })
                else:
                    st.error(f"❌ שגיאה בסריקת {source_name}: {result.get('error', 'לא ניתן לקרוא')}")
            
            if scanned_passengers:
                is_first_empty = len(st.session_state.passenger_list) == 1 and not st.session_state.passenger_list[0].get('first_name')
                
                for i, passenger in enumerate(scanned_passengers):
                    if is_first_empty and i == 0:
                        passenger_idx = 0
                        st.session_state.passenger_list[0] = passenger
                    else:
                        passenger_idx = len(st.session_state.passenger_list)
                        st.session_state.passenger_list.append(passenger)
                    
                    for key in [f"first_name_{passenger_idx}", f"last_name_{passenger_idx}", 
                               f"passport_{passenger_idx}", f"birth_date_{passenger_idx}", 
                               f"passport_expiry_{passenger_idx}"]:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    st.session_state[f"first_name_{passenger_idx}"] = passenger['first_name']
                    st.session_state[f"last_name_{passenger_idx}"] = passenger['last_name']
                    st.session_state[f"passport_{passenger_idx}"] = passenger['passport']
                    st.session_state[f"birth_date_{passenger_idx}"] = passenger['birth_date']
                    st.session_state[f"passport_expiry_{passenger_idx}"] = passenger['passport_expiry']
                
                status_text.text(f"✅ סריקה הושלמה! {len(scanned_passengers)} נוסעים נוספו.")
                st.rerun()
            else:
                status_text.text("❌ לא הצלחנו לסרוק אף דרכון")
        elif scan_button and not has_passport_input:
            st.warning("⚠️ יש להעלות או להדביק תמונות דרכונים לפני הסריקה")
        
        st.markdown("---")
        
        ticket_type_options = ['כרטיס רגיל', 'כרטיס VIP', 'כרטיס ילד', 'כרטיס מלווה']
        
        for i, passenger in enumerate(st.session_state.passenger_list):
            st.markdown(f"**נוסע {i+1}**")
            
            fn_key = f"first_name_{i}"
            ln_key = f"last_name_{i}"
            type_key = f"type_{i}"
            passport_key = f"passport_{i}"
            birth_key = f"birth_date_{i}"
            exp_key = f"passport_expiry_{i}"
            
            # Always sync from passenger_list to session_state on each render
            # This ensures OCR-scanned data is properly displayed
            stored_first = passenger.get('first_name', '')
            stored_last = passenger.get('last_name', '')
            stored_passport = passenger.get('passport', '')
            stored_birth = passenger.get('birth_date', '')
            stored_exp = passenger.get('passport_expiry', '')
            
            # Initialize if not in session state, or if passenger_list has newer data
            if fn_key not in st.session_state or (stored_first and not st.session_state.get(fn_key)):
                st.session_state[fn_key] = stored_first
            if ln_key not in st.session_state or (stored_last and not st.session_state.get(ln_key)):
                st.session_state[ln_key] = stored_last
            if passport_key not in st.session_state or (stored_passport and not st.session_state.get(passport_key)):
                st.session_state[passport_key] = stored_passport
            if birth_key not in st.session_state or (stored_birth and not st.session_state.get(birth_key)):
                st.session_state[birth_key] = stored_birth
            if exp_key not in st.session_state or (stored_exp and not st.session_state.get(exp_key)):
                st.session_state[exp_key] = stored_exp
            
            col_fn, col_ln, col_type, col_del = st.columns([1.3, 1.3, 1.2, 0.3])
            with col_fn:
                first_name = st.text_input("שם פרטי", key=fn_key, placeholder="John")
                st.session_state.passenger_list[i]['first_name'] = first_name
            with col_ln:
                last_name = st.text_input("שם משפחה", key=ln_key, placeholder="Doe")
                st.session_state.passenger_list[i]['last_name'] = last_name
            with col_type:
                current_type = passenger.get('ticket_type', 'כרטיס רגיל')
                type_index = ticket_type_options.index(current_type) if current_type in ticket_type_options else 0
                ticket_type = st.selectbox("סוג כרטיס", options=ticket_type_options, index=type_index, key=type_key)
                st.session_state.passenger_list[i]['ticket_type'] = ticket_type
            with col_del:
                if len(st.session_state.passenger_list) > 1:
                    if st.button("🗑️", key=f"del_{i}"):
                        st.session_state.passenger_list.pop(i)
                        st.rerun()
            
            col_passport, col_birth, col_exp = st.columns(3)
            with col_passport:
                passport = st.text_input("מספר דרכון", key=passport_key, placeholder="12345678")
                st.session_state.passenger_list[i]['passport'] = passport
            with col_birth:
                birth_date = st.text_input("תאריך לידה (DD/MM/YYYY)", key=birth_key, placeholder="15/03/1990")
                st.session_state.passenger_list[i]['birth_date'] = birth_date
            with col_exp:
                passport_expiry = st.text_input("תוקף דרכון (DD/MM/YYYY)", key=exp_key, placeholder="15/03/2030")
                st.session_state.passenger_list[i]['passport_expiry'] = passport_expiry
        
        if st.button("➕ הוסף נוסע"):
            st.session_state.passenger_list.append({
                'first_name': '', 
                'last_name': '', 
                'passport': '', 
                'birth_date': '',
                'passport_expiry': '',
                'ticket_type': 'כרטיס רגיל'
            })
            st.rerun()
        
        passengers = [p for p in st.session_state.passenger_list if (p.get('first_name', '').strip() or p.get('last_name', '').strip() or p.get('name', '').strip())]
    
    with col2:
        st.markdown("### 👁️ תצוגה מקדימה")
        
        if stadium_image:
            try:
                st.image(stadium_image, caption="תרשים מושבים", use_container_width=True)
            except Exception:
                st.caption("תרשים מושבים (לא זמין)")
        elif auto_stadium_map and os.path.exists(auto_stadium_map):
            try:
                st.image(auto_stadium_map, caption="תרשים מושבים (אוטומטי)", use_container_width=True)
            except Exception:
                st.caption("תרשים מושבים (לא זמין)")
        if hotel_image or hotel_image_2:
            if hotel_image and hotel_image_2:
                col_h1, col_h2 = st.columns(2)
                with col_h1:
                    st.image(hotel_image, caption="תמונת המלון 1", use_container_width=True)
                with col_h2:
                    st.image(hotel_image_2, caption="תמונת המלון 2", use_container_width=True)
            elif hotel_image:
                st.image(hotel_image, caption="תמונת המלון", use_container_width=True)
        
        st.markdown("#### 📋 סיכום ההזמנה")
        
        saved_games_summary = st.session_state.get('saved_games', [])
        if saved_games_summary:
            st.write("**אירועים:**")
            for idx, sg in enumerate(saved_games_summary):
                txt = sg.get('display_text', f"אירוע {idx + 1}")
                det = sg.get('details', '')
                st.write(f"- **אירוע {idx + 1}:** {txt}")
                if det:
                    st.caption(det)
            if event_date:
                st.write(f"**תאריך (אירוע ראשון):** {event_date.strftime('%d/%m/%Y')} {event_time.strftime('%H:%M')}")
            if venue:
                st.write(f"**מקום:** {venue}")
        else:
            if event_name:
                st.info(f"**אירוע:** {event_name}")
            if event_date:
                st.write(f"**תאריך:** {event_date.strftime('%d/%m/%Y')} {event_time.strftime('%H:%M')}")
            if venue:
                st.write(f"**מקום:** {venue}")
        if customer_name:
            st.write(f"**לקוח:** {customer_name}")
        if category:
            st.write(f"**קטגוריה:** {category}")
        
        if passengers:
            st.write("**נוסעים:**")
            for p in passengers:
                if isinstance(p, dict):
                    name = f"{p.get('first_name', '')} {p.get('last_name', '')}".strip()
                    if not name:
                        name = p.get('name', '')
                    st.write(f"- {name} ({p.get('ticket_type', 'כרטיס רגיל')})")
                else:
                    st.write(f"- {p}")
        
        if total_foreign > 0:
            st.success(f"**סה\"כ:** {total_foreign} {currency_symbol} = {total_nis:,} ש\"ח")
        
        st.markdown("---")
        
        can_generate = all([event_name, customer_name, customer_email, category])
        
        if can_generate:
            hd = st.session_state.get('hotel_data', {})
            
            team_data = st.session_state.get('selected_team_data', {})
            away_team_data = st.session_state.get('away_team_data', {})
            
            order_data = {
                'product_type': product_type,
                'event_name': event_name,
                'event_type': event_type,
                'event_date': f"{event_date.strftime('%d/%m/%Y')} {event_time.strftime('%H:%M')}",
                'event_date_str': event_date.strftime('%d/%m/%Y'),
                'event_time_str': event_time.strftime('%H:%M'),
                'venue': venue or '',
                'customer_name': customer_name,
                'customer_id': customer_id or '',
                'customer_phone': customer_phone or '',
                'customer_email': customer_email,
                'ticket_description': ticket_description or '',
                'category': category,
                'currency': selected_currency,
                'currency_symbol': currency_symbol,
                'price_per_ticket': price_foreign,
                'price_nis': price_nis,
                'total_foreign': total_foreign,
                'total_euro': total_foreign,
                'total_nis': total_nis,
                'num_tickets': num_tickets,
                'passengers': passengers,
                'exchange_rate': exchange_rate,
                'home_team_badge': team_data.get('badge', ''),
                'away_team_badge': away_team_data.get('badge', ''),
                'home_team_name': st.session_state.get('home_team_hebrew', ''),
                'away_team_name': st.session_state.get('away_team_hebrew', ''),
                'hotel_name': hd.get('hotel_name') or hotel_name,
                'hotel_nights': hotel_nights,
                'hotel_stars': hotel_stars,
                'hotel_meals': hotel_meals,
                'hotel_address': hd.get('hotel_address', ''),
                'hotel_website': hd.get('hotel_website', ''),
                'hotel_rating': hd.get('hotel_rating', ''),
                'hotel_image_path': hd.get('hotel_image_path', ''),
                'hotel_image_path_2': hd.get('hotel_image_path_2', ''),
                'flight_details': flight_details,
                'flights': flights_list if product_type == 'package' else [],
                'transfers': transfers,
                'bag_trolley': bag_trolley if product_type == 'package' else False,
                'bag_checked': bag_checked if product_type == 'package' else '',
                'is_date_final': is_date_final,
                'seats_together': seats_together,
                'saved_games': st.session_state.get('saved_games', [])  # Include all saved games
            }
            
            stadium_img = None
            stadium_photo_img = None
            hotel_img = None
            hotel_img_2 = None
            
            def safe_open_image(path_or_image):
                """Safely open image, skipping SVG files that PIL can't handle"""
                try:
                    if path_or_image is None:
                        return None
                    if isinstance(path_or_image, Image.Image):
                        return path_or_image
                    if isinstance(path_or_image, str):
                        # Skip SVG files - PIL can't handle them
                        if path_or_image.lower().endswith('.svg'):
                            return None
                        if os.path.exists(path_or_image):
                            return Image.open(path_or_image)
                    return None
                except Exception as e:
                    print(f"Error opening image: {e}")
                    return None
            
            if stadium_image:
                stadium_img = safe_open_image(stadium_image)
            elif auto_stadium_map:
                stadium_img = safe_open_image(auto_stadium_map)
            
            if not stadium_img and rd.get('use_sample_images') and os.path.exists('attached_assets/stock_images/football_stadium_int_9fde699a.jpg'):
                stadium_img = Image.open('attached_assets/stock_images/football_stadium_int_9fde699a.jpg')
            
            random_atmosphere = get_random_atmosphere_image(event_type)
            if random_atmosphere:
                stadium_photo_img = safe_open_image(random_atmosphere)
            
            if hotel_image:
                hotel_img = safe_open_image(hotel_image)
            elif rd.get('use_sample_images') and os.path.exists('attached_assets/stock_images/luxury_hotel_exterio_3264e2db.jpg'):
                hotel_img = Image.open('attached_assets/stock_images/luxury_hotel_exterio_3264e2db.jpg')
            
            if hotel_image_2:
                hotel_img_2 = safe_open_image(hotel_image_2)
            
            template_version = 2
            
            st.markdown("### 📤 פעולות")
            
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            with col_btn1:
                if st.button("📦 שמור כחבילה קבועה", type="secondary", use_container_width=True):
                    st.session_state['show_save_package_form'] = True
            with col_btn2:
                if st.button("💼 שמור כהצעה ללקוח", type="secondary", use_container_width=True):
                    st.session_state['show_save_proposal_form'] = True
            with col_btn3:
                generate_pdf_btn = st.button("📄 צור PDF ושמור הזמנה", type="primary", use_container_width=True)
            
            if st.session_state.get('package_saved_success'):
                st.success(f"✅ החבילה '{st.session_state['package_saved_success']}' נשמרה בהצלחה!")
                st.info("💡 תוכל למצוא אותה ב'חבילות קבועות' בתפריט או לטעון אותה מהרשימה למעלה.")
                del st.session_state['package_saved_success']
            
            if st.session_state.get('proposal_saved_success'):
                st.success(f"✅ ההצעה '{st.session_state['proposal_saved_success']}' נשמרה בהצלחה!")
                st.info("💡 תוכל למצוא אותה ב'הצעות ללקוח' בתפריט.")
                del st.session_state['proposal_saved_success']
            
            if st.session_state.get('show_save_proposal_form'):
                st.markdown("---")
                st.markdown("#### 💼 שמירה כהצעה ללקוח")
                
                default_prop_name = f"{customer_name} - {event_name}" if event_name and customer_name else ""
                prop_name_input = st.text_input("📝 שם ההצעה", value=default_prop_name, placeholder="למשל: משפחת כהן - ריאל מדריד", key="save_prop_name")
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    confirm_save_prop = st.button("💾 אשר שמירת הצעה", use_container_width=True, type="primary")
                with col_cancel:
                    if st.button("❌ ביטול", use_container_width=True, key="cancel_proposal"):
                        st.session_state['show_save_proposal_form'] = False
                        st.rerun()
                
                if confirm_save_prop:
                    if not prop_name_input:
                        st.error("❌ יש להזין שם להצעה")
                    elif not customer_name:
                        st.error("❌ יש למלא שם לקוח")
                    else:
                        from models import ClientProposal, ProposalStatus
                        db = get_db()
                        if db:
                            try:
                                # Collect all proposal data (json already imported at top level)
                                proposal_data = {
                                    'customer_name': customer_name,
                                    'customer_id': customer_id,
                                    'customer_phone': customer_phone,
                                    'customer_email': customer_email,
                                    'product_type': product_type,
                                    'event_name': event_name,
                                    'event_type': event_type,
                                    'event_date': event_date.strftime('%d/%m/%Y'),
                                    'event_time': event_time.strftime('%H:%M'),
                                    'venue': venue,
                                    'ticket_description': ticket_description,
                                    'category': category,
                                    'num_tickets': num_tickets,
                                    'currency': selected_currency,
                                    'price_per_ticket': price_foreign,
                                    'total_foreign': total_foreign,
                                    'total_nis': total_nis,
                                    'passengers': passengers,
                                    'saved_games': st.session_state.get('saved_games', []),
                                    'hotel_name': hotel_name if product_type == 'package' else '',
                                    'hotel_nights': hotel_nights if product_type == 'package' else 0,
                                    'hotel_stars': hotel_stars if product_type == 'package' else '',
                                    'hotel_meals': hotel_meals if product_type == 'package' else '',
                                    'flights': flights_list if product_type == 'package' else [],
                                    'transfers': transfers if product_type == 'package' else False
                                }
                                
                                new_proposal = ClientProposal(
                                    proposal_name=prop_name_input,
                                    customer_name=customer_name,
                                    customer_email=customer_email or '',
                                    customer_phone=customer_phone or '',
                                    proposal_data=json.dumps(proposal_data),
                                    total_price_euro=float(total_foreign),
                                    total_price_nis=float(total_nis),
                                    status=ProposalStatus.DRAFT
                                )
                                
                                db.add(new_proposal)
                                db.commit()
                                st.session_state['proposal_saved_success'] = prop_name_input
                                st.session_state['show_save_proposal_form'] = False
                                st.rerun()
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ שגיאה בשמירה: {str(e)}")
                            finally:
                                db.close()
            
            if st.session_state.get('show_save_package_form'):
                st.markdown("---")
                st.markdown("#### 📦 שמירה כחבילה קבועה")
                
                default_pkg_name = f"{event_name} - {category}" if event_name else ""
                pkg_name_input = st.text_input("📝 שם החבילה", value=default_pkg_name, placeholder="למשל: סטינג לימסול 2026 - גולדן", key="save_pkg_name")
                
                col_save, col_cancel = st.columns(2)
                with col_save:
                    confirm_save = st.button("💾 אשר שמירת חבילה", use_container_width=True, type="primary")
                with col_cancel:
                    if st.button("❌ ביטול", use_container_width=True):
                        st.session_state['show_save_package_form'] = False
                        st.rerun()
                
                if confirm_save:
                    if not pkg_name_input:
                        st.error("❌ יש להזין שם לחבילה")
                    else:
                        db = get_db()
                        if db:
                            try:
                                event_type_map = {'הופעה': EventType.CONCERT, 'כדורגל': EventType.FOOTBALL, 'אחר': EventType.OTHER}
                                event_type_enum = event_type_map.get(event_type, EventType.OTHER)
                                product_type_val = "full_package" if product_type == "package" else "tickets_only"
                                
                                hotel_data_json = {}
                                if product_type == "package":
                                    hd_save = st.session_state.get('hotel_data', {})
                                    hotel_data_json = {
                                        'name': hd_save.get('hotel_name') or hotel_name,
                                        'check_in': hd_save.get('check_in', ''),
                                        'check_out': hd_save.get('check_out', ''),
                                        'address': hd_save.get('hotel_address', ''),
                                        'website': hd_save.get('hotel_website', ''),
                                        'rating': hd_save.get('hotel_rating', ''),
                                        'stars': hotel_stars,
                                        'nights': hotel_nights,
                                        'meals': hotel_meals
                                    }
                                
                                flight_data_json = {}
                                if product_type == "package" and flights_list:
                                    outbound_flight = next((f for f in flights_list if f.get('direction') == 'הלוך'), {})
                                    return_flight = next((f for f in flights_list if f.get('direction') == 'חזור'), {})
                                    flight_data_json = {
                                        'outbound': {
                                            'from': outbound_flight.get('from', ''),
                                            'to': outbound_flight.get('to', ''),
                                            'date': outbound_flight.get('date', ''),
                                            'time': outbound_flight.get('time', ''),
                                            'flight_number': outbound_flight.get('flight_no', ''),
                                            'airline': outbound_flight.get('airline', '')
                                        },
                                        'return': {
                                            'from': return_flight.get('from', ''),
                                            'to': return_flight.get('to', ''),
                                            'date': return_flight.get('date', ''),
                                            'time': return_flight.get('time', ''),
                                            'flight_number': return_flight.get('flight_no', ''),
                                            'airline': return_flight.get('airline', '')
                                        }
                                    }
                                
                                stadium_map_bytes = None
                                if st.session_state.get('saved_stadium_map_bytes'):
                                    stadium_map_bytes = st.session_state.get('saved_stadium_map_bytes')
                                elif st.session_state.get('pasted_stadium_map'):
                                    pasted_img = st.session_state.get('pasted_stadium_map')
                                    img_byte_arr = io.BytesIO()
                                    pasted_img.save(img_byte_arr, format='PNG')
                                    stadium_map_bytes = img_byte_arr.getvalue()
                                elif auto_stadium_map and os.path.exists(auto_stadium_map):
                                    with open(auto_stadium_map, 'rb') as f:
                                        stadium_map_bytes = f.read()
                                
                                if hotel_data_json and product_type == "package":
                                    hotel_data_json['image_path'] = hd_save.get('hotel_image_path', '')
                                    hotel_data_json['image_path_2'] = hd_save.get('hotel_image_path_2', '')
                                
                                new_pkg = PackageTemplate(
                                    name=pkg_name_input,
                                    event_type=event_type_enum,
                                    product_type=product_type_val,
                                    event_name=event_name,
                                    event_date=event_date.strftime('%d/%m/%Y'),
                                    event_time=event_time.strftime('%H:%M'),
                                    venue=venue,
                                    ticket_description=ticket_description,
                                    ticket_category=category,
                                    price_per_ticket_euro=float(price_foreign),
                                    hotel_data=json.dumps(hotel_data_json) if hotel_data_json else None,
                                    flight_data=json.dumps(flight_data_json) if flight_data_json else None,
                                    package_price_euro=float(price_foreign),
                                    stadium_map_data=stadium_map_bytes,
                                    stadium_map_mime='image/png' if stadium_map_bytes else None,
                                    notes=""
                                )
                                
                                db.add(new_pkg)
                                db.commit()
                                st.session_state['package_saved_success'] = pkg_name_input
                                st.session_state['show_save_package_form'] = False
                                st.rerun()
                            except Exception as e:
                                db.rollback()
                                st.error(f"❌ שגיאה בשמירה: {str(e)}")
                            finally:
                                db.close()
            
            if generate_pdf_btn:
                order_number = generate_order_number()
                order_data['order_number'] = order_number
                pdf_bytes = None
                with st.spinner("יוצר PDF..."):
                    try:
                        pdf_bytes = generate_pdf(order_data, stadium_img, hotel_img, hotel_img_2, stadium_photo_img, template_version)
                        st.session_state.pdf_bytes = pdf_bytes
                        st.session_state.order_generated = True
                        st.session_state.current_order_number = order_number
                        st.success("✅ ה-PDF נוצר בהצלחה!")
                        st.info(f"📋 מספר הזמנה: {order_number}")
                    except Exception as e:
                        st.error(f"❌ יצירת PDF נכשלה: {str(e)}")
                        st.code(str(e), language="text")
                        import traceback
                        with st.expander("פרטי השגיאה"):
                            st.code(traceback.format_exc())

                if pdf_bytes:
                    try:
                        saved_order = save_order_to_db(order_data, pdf_bytes)
                        if saved_order:
                            st.session_state.current_order_id = saved_order.id
                    except Exception as e:
                        st.warning("⚠️ ההזמנה לא נשמרה במסד הנתונים, אך ה-PDF זמין להורדה.")
            
            if st.session_state.get('order_generated') and st.session_state.get('pdf_bytes'):
                filename = f"הזמנה_{customer_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
                
                st.download_button(
                    label="⬇️ הורד PDF",
                    data=st.session_state.pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    use_container_width=True
                )
                
                st.markdown("---")
                
                st.markdown("### 📧 שלח ללקוח באימייל")
                
                email_subject = st.text_input(
                    "נושא המייל",
                    value=f"הצעת מחיר - {event_name}"
                )
                
                email_body = st.text_area(
                    "תוכן ההודעה",
                    value=f"""שלום {customer_name},

מצורפת הצעת המחיר שלך לאירוע:
🎟️ {event_name}
📅 {event_date.strftime('%d/%m/%Y')} בשעה {event_time.strftime('%H:%M')}
📍 {venue}

סה"כ: {total_euro} יורו ({total_nis:,} ש"ח)

לאישור ההזמנה, אנא השב למייל זה או צור קשר בטלפון.

בברכה,
צוות TikTik
972-732726000
""",
                    height=200
                )
                
                if st.button("📧 שלח מייל ללקוח", use_container_width=True):
                    resend_api_key = os.environ.get('RESEND_API_KEY')
                    if resend_api_key:
                        try:
                            import resend
                            resend.api_key = resend_api_key
                            
                            pdf_base64 = base64.b64encode(st.session_state.pdf_bytes).decode()
                            
                            resend.Emails.send({
                                "from": "TikTik <orders@tiktik.co.il>",
                                "to": [customer_email],
                                "subject": email_subject,
                                "text": email_body,
                                "attachments": [{
                                    "filename": filename,
                                    "content": pdf_base64
                                }]
                            })
                            
                            if st.session_state.get('current_order_id'):
                                update_order_status(st.session_state.current_order_id, OrderStatus.SENT)
                            
                            st.success(f"✅ המייל נשלח בהצלחה ל-{customer_email}!")
                        except Exception as e:
                            st.error(f"❌ שגיאה בשליחת המייל: {str(e)}")
                    else:
                        st.warning("⚠️ לא הוגדר מפתח API לשליחת מיילים. הורד את ה-PDF ושלח ידנית.")
                        st.info("💡 טיפ: הוסף את מפתח ה-RESEND_API_KEY בהגדרות הסביבה כדי להפעיל שליחת מיילים אוטומטית.")
        else:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.info("📝 מלא את הפרטים הנדרשים: שם אירוע, שם לקוח, אימייל ובלוק")
            st.markdown('</div>', unsafe_allow_html=True)

