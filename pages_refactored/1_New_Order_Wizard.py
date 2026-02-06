import streamlit as st
import os
import sys
from datetime import date

# הוספת נתיב לשורש הפרויקט
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_refactored import init_session_state, get_session_value, set_session_value
from services_refactored import save_order_to_db, generate_pdf
from services_refactored.api_service import (
    get_football_leagues, get_teams_for_league, handle_hotel_search,
    handle_flight_scan, handle_passport_scan, get_stadium_map
)
from streamlit_paste_button import paste_image_button
from sports_api import get_hebrew_name

# הגדרת עמוד
st.set_page_config(page_title="הזמנה חדשה | TikTik", layout="wide")

# שחזור ה-CSS המקורי
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');
* { font-family: 'Heebo', sans-serif !important; }
.main .block-container { direction: rtl; text-align: right; }
.form-section { background: #1e1e2e; padding: 2rem; border-radius: 15px; border: 1px solid #333; margin-bottom: 2rem; color: white; }
.stButton > button { width: 100%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 10px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# אתחול State
if 'order_data' not in st.session_state:
    st.session_state.order_data = {
        'event_type': 'כדורגל', 'event_name': '', 'event_location': '', 'event_date': date.today(),
        'num_tickets': 1, 'hotel_name': '', 'hotel_address': '', 'hotel_stars': '',
        'passengers': [], 'flights': [], 'package_type': 'חבילה מלאה'
    }
if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1

current_step = st.session_state.wizard_step
order_data = st.session_state.order_data

st.title("📝 יצירת הזמנה חדשה")

# תצוגת שלבים
cols = st.columns(4)
steps = ["סוג מוצר", "פרטי אירוע", "לקוח ונוסעים", "סיכום"]
for i, step in enumerate(steps):
    with cols[i]:
        color = "#667eea" if current_step == i+1 else "#a0a0a0"
        st.markdown(f"<p style='text-align:center; color:{color}; font-weight:bold;'>{step}</p>", unsafe_allow_html=True)
        st.progress(1.0 if current_step > i else 0.0)

# שלב 1: סוג מוצר
if current_step == 1:
    with st.container():
        st.markdown("<div class='form-section'><h3>שלב 1: סוג המוצר</h3>", unsafe_allow_html=True)
        order_data['package_type'] = st.radio("בחר סוג חבילה", ["חבילה מלאה", "כרטיסים בלבד", "מלון בלבד"], index=0 if order_data.get('package_type') == 'חבילה מלאה' else 1)
        if st.button("המשך לשלב הבא ⬅️"):
            st.session_state.wizard_step = 2
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# שלב 2: פרטי אירוע
elif current_step == 2:
    with st.container():
        st.markdown("<div class='form-section'><h3>שלב 2: פרטי האירוע</h3>", unsafe_allow_html=True)
        
        event_type = st.selectbox("סוג אירוע", ["כדורגל", "הופעה", "אחר"], index=0 if order_data.get('event_type') == 'כדורגל' else 1)
        order_data['event_type'] = event_type
        
        if event_type == "כדורגל":
            leagues = get_football_leagues()
            selected_league = st.selectbox("בחר ליגה", leagues)
            if selected_league != "-- בחר ליגה --":
                teams = get_teams_for_league(selected_league)
                team_heb_names = [f"{get_hebrew_name(t['name'])} ({t['name']})" for t in teams]
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    h_idx = st.selectbox("קבוצה מארחת", range(len(team_heb_names)), format_func=lambda i: team_heb_names[i])
                    home_team = teams[h_idx]
                with col_t2:
                    a_idx = st.selectbox("קבוצה אורחת", range(len(team_heb_names)), format_func=lambda i: team_heb_names[i])
                    away_team = teams[a_idx]
                
                order_data['event_name'] = f"{get_hebrew_name(home_team['name'])} נגד {get_hebrew_name(away_team['name'])}"
                order_data['event_location'] = f"{home_team.get('stadium', '')}, {home_team.get('stadium_location', '')}"
                
                map_path = get_stadium_map(home_team['name'])
                if map_path and os.path.exists(map_path):
                    st.image(map_path, caption=f"מפת אצטדיון: {home_team.get('stadium')}")

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            order_data['event_name'] = st.text_input("שם האירוע", value=order_data.get('event_name', ''))
            order_data['event_date'] = st.date_input("תאריך האירוע", value=order_data.get('event_date'))
        with col2:
            order_data['event_location'] = st.text_input("מקום האירוע", value=order_data.get('event_location', ''))
            order_data['num_tickets'] = st.number_input("מספר כרטיסים", min_value=1, value=order_data.get('num_tickets', 1))

        if order_data.get('package_type') == 'חבילה מלאה':
            st.markdown("#### 🏨 פרטי מלון")
            h_col1, h_col2 = st.columns([3, 1])
            with h_col1:
                hotel_name = st.text_input("שם המלון", value=order_data.get('hotel_name', ''))
            with h_col2:
                if st.button("🔍 חפש מלון"):
                    order_data = handle_hotel_search(hotel_name, order_data)
                    st.rerun()
            
            if order_data.get('hotel_address'):
                st.info(f"📍 כתובת: {order_data['hotel_address']} | ⭐ דירוג: {order_data.get('hotel_stars', 'N/A')}")

        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("➡️ חזור"):
                st.session_state.wizard_step = 1
                st.rerun()
        with col_next:
            if st.button("המשך לשלב הבא ⬅️"):
                st.session_state.wizard_step = 3
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# שלב 3: לקוח ונוסעים
elif current_step == 3:
    with st.container():
        st.markdown("<div class='form-section'><h3>שלב 3: פרטי לקוח ונוסעים</h3>", unsafe_allow_html=True)
        
        st.markdown("#### 🛂 סריקת דרכונים")
        p_col1, p_col2 = st.columns([1, 1])
        with p_col1:
            uploaded_passports = st.file_util.file_uploader("העלה צילומי דרכון", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
            if uploaded_passports:
                if st.button("📸 סרוק קבצים"):
                    order_data = handle_passport_scan(uploaded_passports, order_data)
                    st.rerun()
        with p_col2:
            st.write("הדבק צילום דרכון (Ctrl+V)")
            pasted_passport = paste_image_button("📋 הדבק דרכון")
            if pasted_passport:
                order_data = handle_passport_scan([pasted_passport], order_data)
                st.rerun()

        st.markdown("---")
        st.write(f"👥 נוסעים שנוספו: {len(order_data.get('passengers', []))}")
        for i, p in enumerate(order_data.get('passengers', [])):
            st.text(f"{i+1}. {p['first_name']} {p['last_name']} - {p['passport']}")

        col_prev, col_next = st.columns(2)
        with col_prev:
            if st.button("➡️ חזור"):
                st.session_state.wizard_step = 2
                st.rerun()
        with col_next:
            if st.button("המשך לסיכום ⬅️"):
                st.session_state.wizard_step = 4
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# שלב 4: סיכום
elif current_step == 4:
    with st.container():
        st.markdown("<div class='form-section'><h3>שלב 4: סיכום והפקה</h3>", unsafe_allow_html=True)
        st.write(f"**אירוע:** {order_data['event_name']}")
        st.write(f"**תאריך:** {order_data['event_date']}")
        st.write(f"**מיקום:** {order_data['event_location']}")
        st.write(f"**נוסעים:** {len(order_data['passengers'])}")
        
        if st.button("✅ אשר וצור PDF"):
            with st.spinner("מפיק PDF..."):
                pdf_path = generate_pdf(order_data)
                if pdf_path:
                    with open(pdf_path, "rb") as f:
                        st.download_button("📥 הורד טופס הזמנה (PDF)", f, file_name=f"Order_{order_data['event_name']}.pdf")
        
        if st.button("➡️ חזור"):
            st.session_state.wizard_step = 3
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
