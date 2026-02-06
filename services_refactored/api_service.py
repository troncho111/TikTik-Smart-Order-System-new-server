import streamlit as st
import os
import json
import io
from sports_api import LEAGUES, get_teams_by_league, get_hebrew_name, TEAM_HEBREW_NAMES
from stadium_api import get_team_info, get_team_map_path, get_all_teams
from concerts_service import search_artists, search_events_combined, get_popular_artists
from concerts_data import get_venue_map_path
from hotel_resolver import resolve_hotel_safe
from flight_ocr import extract_flight_data
from passport_ocr import extract_passport_data

def get_football_leagues():
    return ["-- בחר ליגה --"] + list(LEAGUES.keys())

def get_teams_for_league(league_name):
    if not league_name or league_name == "-- בחר ליגה --":
        return []
    english_league = LEAGUES.get(league_name, "") or league_name
    return get_teams_by_league(english_league)

def handle_hotel_search(hotel_name, order_data):
    if not hotel_name:
        st.warning("⚠️ נא להזין שם מלון לחיפוש")
        return order_data
    
    with st.spinner("מחפש פרטי מלון..."):
        result = resolve_hotel_safe(hotel_name)
        if result.get('error'):
            st.error(f"❌ {result['error']}")
        else:
            order_data.update({
                'hotel_name': result.get('hotel_name', hotel_name),
                'hotel_address': result.get('hotel_address', ''),
                'hotel_stars': result.get('hotel_stars', ''),
                'hotel_rating': result.get('hotel_rating', '')
            })
            st.success(f"✅ נמצא: {result.get('hotel_name')}")
            return order_data
    return order_data

def handle_flight_scan(image_source, order_data):
    if not image_source:
        return order_data
        
    with st.spinner("סורק פרטי טיסות..."):
        try:
            if hasattr(image_source, 'read'):
                image_bytes = image_source.read()
            else:
                img_byte_arr = io.BytesIO()
                image_source.save(img_byte_arr, format='PNG')
                image_bytes = img_byte_arr.getvalue()
            
            result = extract_flight_data(image_bytes)
            if result.get('success') and result.get('flights'):
                order_data['flights'] = result['flights']
                st.success("✅ פרטי הטיסה נסרקו בהצלחה")
                return order_data
            else:
                st.error("❌ לא ניתן היה לחלץ פרטי טיסה מהתמונה")
        except Exception as e:
            st.error(f"❌ שגיאה בסריקה: {str(e)}")
    return order_data

def handle_passport_scan(images_list, order_data):
    if not images_list:
        return order_data
        
    passengers = order_data.get('passengers', [])
    scanned_count = 0
    
    with st.spinner(f"סורק {len(images_list)} דרכונים..."):
        for img_source in images_list:
            try:
                if hasattr(img_source, 'read'):
                    image_bytes = img_source.read()
                elif isinstance(img_source, bytes):
                    image_bytes = img_source
                else:
                    img_byte_arr = io.BytesIO()
                    img_source.save(img_byte_arr, format='PNG')
                    image_bytes = img_byte_arr.getvalue()
                
                result = extract_passport_data(image_bytes)
                if result.get('success'):
                    passengers.append({
                        'first_name': result.get('first_name', ''),
                        'last_name': result.get('last_name', ''),
                        'passport': result.get('passport_number', ''),
                        'birth_date': result.get('birth_date', ''),
                        'passport_expiry': result.get('passport_expiry', '')
                    })
                    scanned_count += 1
            except Exception as e:
                st.error(f"❌ שגיאה בסריקת דרכון: {str(e)}")
                
    if scanned_count > 0:
        order_data['passengers'] = passengers
        st.success(f"✅ נסרקו {scanned_count} דרכונים בהצלחה")
        return order_data
    return order_data
