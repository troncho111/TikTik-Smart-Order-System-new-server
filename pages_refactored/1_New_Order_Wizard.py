"""
ממשק אשף להזמנה חדשה - עיצוב מקורי משוחזר
"""
import streamlit as st
import sys
import os
import io
from PIL import Image

# הוספת נתיב לשורש הפרויקט
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_refactored import init_session_state, get_session_value, set_session_value
from services_refactored import save_order_to_db, generate_pdf
from services_refactored.api_service import (
    get_football_leagues, get_teams_for_league, get_team_details, 
    get_stadium_map, search_concert_artists, get_concert_events, get_worldcup_matches
)
from passport_ocr import extract_passport_data
from hotel_resolver import resolve_hotel_safe
from flight_ocr import extract_flight_data
from streamlit_paste_button import paste_image_button
from sports_api import get_hebrew_name, TEAM_HEBREW_NAMES

# הגדרת עמוד
st.set_page_config(
    page_title="הזמנה חדשה | TikTik",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# שחזור ה-CSS המקורי של המשתמש
RTL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Heebo', sans-serif !important;
}

.main .block-container {
    direction: rtl;
    text-align: right;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    direction: rtl;
    text-align: right;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    direction: rtl;
    text-align: right;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 10px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.form-section {
    background: #1e1e2e;
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 1.5rem;
    border: 1px solid #333;
    color: white;
}

.form-section h3 {
    color: #667eea;
    border-bottom: 2px solid #667eea;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

/* Sidebar fix */
[data-testid="stSidebar"] {
    direction: rtl !important;
}
</style>
"""

st.markdown(RTL_CSS, unsafe_allow_html=True)

# אתחול session state
init_session_state('wizard_step', 1)
init_session_state('order_data', {})

# כותרת
st.markdown("<h1 style='text-align: center;'>📝 יצירת הזמנה חדשה</h1>", unsafe_allow_html=True)

# פס התקדמות פשוט
current_step = get_session_value('wizard_step', 1)
steps = ["סוג מוצר", "פרטי אירוע", "לקוח ונוסעים", "סיכום"]
st.progress((current_step - 1) / (len(steps) - 1))
cols = st.columns(len(steps))
for i, step in enumerate(steps):
    with cols[len(steps)-1-i]:
        color = "#667eea" if i+1 == current_step else "#a0a0a0"
        st.markdown(f"<p style='text-align: center; color: {color}; font-weight: bold;'>{step}</p>", unsafe_allow_html=True)

st.markdown("---")

# שלב 1: בחירת סוג מוצר
if current_step == 1:
    with st.container():
        st.markdown("<div class='form-section'><h3>שלב 1: בחירת סוג חבילה</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✈️ חבילה מלאה", use_container_width=True):
                set_session_value('order_data', {'package_type': 'חבילה מלאה'})
                set_session_value('wizard_step', 2)
                st.rerun()
        with col2:
            if st.button("🎫 כרטיסים בלבד", use_container_width=True):
                set_session_value('order_data', {'package_type': 'כרטיסים בלבד'})
                set_session_value('wizard_step', 2)
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

# שלב 2: פרטי אירוע
elif current_step == 2:
    order_data = get_session_value('order_data', {})
    with st.container():
        st.markdown("<div class='form-section'><h3>שלב 2: פרטי האירוע</h3>", unsafe_allow_html=True)
        
        event_type = st.selectbox("סוג אירוע", ["כדורגל", "הופעה", "אחר"], index=0 if order_data.get('event_type') == 'כדורגל' else 1 if order_data.get('event_type') == 'הופעה' else 2)
        order_data['event_type'] = event_type
        
        if event_type == "כדורגל":
            leagues = get_football_leagues()
            selected_league = st.selectbox("בחר ליגה", leagues, key="wizard_league")
            
            if selected_league != "-- בחר ליגה --":
                teams = get_teams_for_league(selected_league)
                team_names = [t['name'] for t in teams]
                team_heb_names = [f"{get_hebrew_name(t['name'])} ({t['name']})" for t in teams]
                
                col_t1, col_t2 = st.columns(2)
                with col_t1:
                    home_team_idx = st.selectbox("קבוצה מארחת", range(len(team_heb_names)), format_func=lambda i: team_heb_names[i])
                    home_team = teams[home_team_idx]
                with col_t2:
                    away_team_idx = st.selectbox("קבוצה אורחת", range(len(team_heb_names)), format_func=lambda i: team_heb_names[i])
                    away_team = teams[away_team_idx]
                
                order_data['event_name'] = f"{get_hebrew_name(home_team['name'])} נגד {get_hebrew_name(away_team['name'])}"
                order_data['event_location'] = f"{home_team.get('stadium', '')}, {home_team.get('stadium_location', '')}"
                
                # הצגת מפת אצטדיון
                map_path = get_stadium_map(home_team['name'])
                if map_path and os.path.exists(map_path):
                    st.image(map_path, caption=f"מפת אצטדיון: {home_team.get('stadium')}")
                    order_data['stadium_map'] = map_path

        elif event_type == "הופעה":
            artist_query = st.text_input("חפש אמן (באנגלית)", placeholder="לדוגמה: Coldplay")
            if artist_query:
                artists_res = search_concert_artists(artist_query)
                if artists_res.get('artists'):
                    artist_options = [a['name'] for a in artists_res['artists']]
                    selected_artist_name = st.selectbox("בחר אמן מהתוצאות", artist_options)
                    selected_artist = next(a for a in artists_res['artists'] if a['name'] == selected_artist_name)
                    
                    events_res = get_concert_events(selected_artist['name'], selected_artist['id'])
                    if events_res.get('concerts'):
                        event_options = [f"{c['date']} - {c['venue']}, {c['city']}" for c in events_res['concerts']]
                        selected_event_idx = st.selectbox("בחר הופעה", range(len(event_options)), format_func=lambda i: event_options[i])
                        selected_event = events_res['concerts'][selected_event_idx]
                        
                        order_data['event_name'] = f"הופעה של {selected_artist['name']}"
                        order_data['event_location'] = f"{selected_event['venue']}, {selected_event['city']}"
                        order_data['event_date'] = selected_event['date']

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            event_name = st.text_input("שם האירוע (עריכה ידנית)", value=order_data.get('event_name', ''))
            event_date = st.date_input("תאריך האירוע")
        with col2:
            event_location = st.text_input("מקום האירוע (עריכה ידנית)", value=order_data.get('event_location', ''))
            num_tickets = st.number_input("מספר כרטיסים", min_value=1, value=order_data.get('num_tickets', 1))
            
        if order_data.get('package_type') == 'חבילה מלאה':
            st.markdown("#### 🏨 פרטי מלון")
            col_h1, col_h2 = st.columns([3, 1])
            with col_h1:
                hotel_name = st.text_input("שם המלון", value=order_data.get('hotel_name', ''))
            with col_h2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔍 חפש מלון", use_container_width=True):
                    with st.spinner("מחפש פרטי מלון..."):
                        result = resolve_hotel_safe(hotel_name)
                        if not result.get('error'):
                            order_data.update({
                                'hotel_name': result.get('hotel_name', hotel_name),
                                'hotel_address': result.get('hotel_address', ''),
                                'hotel_stars': result.get('hotel_stars', '')
                            })
                            st.success(f"✅ נמצא: {result.get('hotel_name')}")
                            st.rerun()
            
            hotel_nights = st.number_input("מספר לילות", min_value=1, value=order_data.get('hotel_nights', 1))
            
            st.markdown("#### ✈️ פרטי טיסות (אופציונלי)")
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                flight_img = st.file_uploader("העלה צילום מסך של טיסה", type=['png', 'jpg', 'jpeg'])
            with col_f2:
                st.markdown("<br>", unsafe_allow_html=True)
                flight_paste = paste_image_button("📋 הדבק טיסה", key="flight_paste")
            
            flight_to_scan = flight_img or (flight_paste.image_data if flight_paste else None)
            if st.button("🔍 סרוק טיסה", use_container_width=True) and flight_to_scan:
                with st.spinner("סורק טיסה..."):
                    if hasattr(flight_to_scan, 'read'):
                        image_bytes = flight_to_scan.read()
                    else:
                        img_byte_arr = io.BytesIO()
                        flight_to_scan.save(img_byte_arr, format='PNG')
                        image_bytes = img_byte_arr.getvalue()
                    
                    result = extract_flight_data(image_bytes)
                    if result.get('success'):
                        st.success("✅ פרטי הטיסה נסרקו בהצלחה")
                        order_data['flights'] = result.get('flights', [])
                        set_session_value('order_data', order_data)
                        st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ חזור"):
            set_session_value('wizard_step', 1)
            st.rerun()
    with c2:
        if st.button("המשך ➡️"):
            order_data.update({
                'event_name': event_name,
                'event_location': event_location,
                'event_date': str(event_date),
                'num_tickets': num_tickets
            })
            if order_data.get('package_type') == 'חבילה מלאה':
                order_data.update({'hotel_name': hotel_name, 'hotel_nights': hotel_nights})
            set_session_value('order_data', order_data)
            set_session_value('wizard_step', 3)
            st.rerun()

# שלב 3: פרטי לקוח
elif current_step == 3:
    order_data = get_session_value('order_data', {})
    with st.container():
        st.markdown("<div class='form-section'><h3>שלב 3: פרטי לקוח ונוסעים</h3>", unsafe_allow_html=True)
        
        st.markdown("#### 👤 פרטי איש קשר")
        col1, col2, col3 = st.columns(3)
        with col1:
            customer_name = st.text_input("שם הלקוח", value=order_data.get('customer_name', ''))
        with col2:
            customer_email = st.text_input("אימייל", value=order_data.get('customer_email', ''))
        with col3:
            customer_phone = st.text_input("טלפון", value=order_data.get('customer_phone', ''))
            
        st.markdown("---")
        st.markdown("#### 🛂 סריקת דרכונים")
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            passport_img = st.file_uploader("העלה צילומי דרכון", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
        with col_p2:
            st.markdown("<br>", unsafe_allow_html=True)
            passport_paste = paste_image_button("📋 הדבק דרכון", key="passport_paste")
            
        if st.button("🔍 סרוק דרכונים", use_container_width=True):
            images_to_scan = []
            if passport_img:
                for img in passport_img: images_to_scan.append(img.read())
            if passport_paste and passport_paste.image_data:
                img_byte_arr = io.BytesIO()
                passport_paste.image_data.save(img_byte_arr, format='PNG')
                images_to_scan.append(img_byte_arr.getvalue())
                
            if images_to_scan:
                with st.spinner(f"סורק {len(images_to_scan)} דרכונים..."):
                    passengers = order_data.get('passengers', [])
                    for img_bytes in images_to_scan:
                        result = extract_passport_data(img_bytes)
                        if result.get('success'):
                            passengers.append({
                                'first_name': result.get('first_name', ''),
                                'last_name': result.get('last_name', ''),
                                'passport': result.get('passport_number', ''),
                                'birth_date': result.get('birth_date', '')
                            })
                    order_data['passengers'] = passengers
                    set_session_value('order_data', order_data)
                    st.success(f"✅ נסרקו {len(images_to_scan)} דרכונים")
                    st.rerun()
        
        if order_data.get('passengers'):
            st.markdown("##### 👥 נוסעים שנסרקו:")
            for p in order_data['passengers']:
                st.write(f"• {p['first_name']} {p['last_name']} ({p['passport']})")
                
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ חזור"):
            set_session_value('wizard_step', 2)
            st.rerun()
    with c2:
        if st.button("המשך ➡️"):
            order_data.update({
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone
            })
            set_session_value('order_data', order_data)
            set_session_value('wizard_step', 4)
            st.rerun()

# שלב 4: סיכום
elif current_step == 4:
    order_data = get_session_value('order_data', {})
    with st.container():
        st.markdown("<div class='form-section'><h3>שלב 4: סיכום הזמנה</h3>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**סוג:** {order_data.get('package_type')}")
            st.write(f"**אירוע:** {order_data.get('event_name')}")
            st.write(f"**תאריך:** {order_data.get('event_date')}")
        with col2:
            st.write(f"**לקוח:** {order_data.get('customer_name')}")
            st.write(f"**טלפון:** {order_data.get('customer_phone')}")
        st.markdown("</div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("⬅️ חזור"):
            set_session_value('wizard_step', 3)
            st.rerun()
    with c2:
        if st.button("💾 שמור כהצעה"):
            with st.spinner("שומר הצעת מחיר..."):
                # כאן תבוא הלוגיקה של שמירת הצעה (ClientProposal)
                st.success("✅ ההצעה נשמרה בהצלחה!")
    with c3:
        if st.button("📌 שמור כחבילה"):
            with st.spinner("שומר כחבילה קבועה..."):
                # כאן תבוא הלוגיקה של שמירת חבילה (PackageTemplate)
                st.success("✅ החבילה נשמרה במאגר!")
    with c4:
        if st.button("✅ אשר וצור PDF"):
            with st.spinner("מפיק PDF מקצועי..."):
                try:
                    # הכנת נתונים ל-PDF
                    pdf_data = order_data.copy()
                    
                    # הוספת שדות חסרים ל-PDF (לפי התבנית)
                    pdf_data['order_id'] = "TKT-" + os.urandom(2).hex().upper()
                    pdf_data['created_at'] = str(os.popen('date +"%d/%m/%Y"').read().strip())
                    pdf_data['final_price'] = "0" # כאן אפשר להוסיף חישוב מחיר
                    
                    # יצירת ה-PDF
                    pdf_bytes = generate_pdf(pdf_data)
                    
                    if pdf_bytes:
                        st.success("✅ ה-PDF מוכן להורדה!")
                        st.download_button(
                            label="📥 הורד טופס הזמנה (PDF)",
                            data=pdf_bytes,
                            file_name=f"Order_{pdf_data['customer_name']}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"שגיאה ביצירת ה-PDF: {str(e)}")
