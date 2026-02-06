"""
ממשק אשף להזמנה חדשה - עיצוב מודרני ו-RTL מלא
"""
import streamlit as st
import sys
import os

# הוספת נתיב לשורש הפרויקט
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils_refactored import init_session_state, get_session_value, set_session_value
from services_refactored import save_order_to_db, generate_pdf

# הגדרת עמוד
st.set_page_config(
    page_title="הזמנה חדשה | TikTik",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מקצועי ל-RTL ועיצוב מודרני
st.markdown("""
<style>
    /* הכרחת RTL על כל האפליקציה */
    @import url('https://fonts.googleapis.com/css2?family=Assistant:wght@300;400;600;700&display=swap');
    
    html, body, [data-testid="stAppViewContainer"], .main {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Assistant', sans-serif !important;
    }
    
    /* תיקון תפריט צד */
    [data-testid="stSidebar"] {
        direction: rtl !important;
    }
    
    /* עיצוב פס התקדמות מודרני */
    .st-emotion-cache-1kyx7g3 {
        flex-direction: row-reverse !important;
    }
    
    .wizard-container {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        margin-bottom: 2rem;
    }
    
    .step-header {
        color: #1e3a8a;
        margin-bottom: 1.5rem;
        border-bottom: 2px solid #e0e7ff;
        padding-bottom: 0.5rem;
    }
    
    /* עיצוב כפתורים */
    .stButton > button {
        width: 100%;
        border-radius: 8px !important;
        height: 3em !important;
        font-weight: 600 !important;
    }
    
    /* תיקון שדות קלט ל-RTL */
    input, select, textarea {
        direction: rtl !important;
        text-align: right !important;
    }
    
    div[data-baseweb="select"] {
        direction: rtl !important;
    }
    
    label {
        font-weight: 600 !important;
        color: #374151 !important;
        margin-bottom: 0.5rem !important;
    }
</style>
""", unsafe_allow_html=True)

# אתחול session state
init_session_state('wizard_step', 1)
init_session_state('order_data', {})

# פונקציה להצגת פס התקדמות נקי
def show_progress_bar(current_step):
    steps = ["סוג מוצר", "פרטי אירוע", "לקוח ונוסעים", "סיכום"]
    progress = (current_step - 1) / (len(steps) - 1)
    st.progress(progress)
    
    cols = st.columns(len(steps))
    for i, step in enumerate(steps):
        with cols[len(steps)-1-i]: # RTL order
            color = "#1e3a8a" if i+1 == current_step else "#9ca3af"
            weight = "bold" if i+1 == current_step else "normal"
            st.markdown(f"<p style='text-align: center; color: {color}; font-weight: {weight};'>{step}</p>", unsafe_allow_html=True)

# כותרת ראשית
st.markdown("<h1 style='text-align: center; color: #1e3a8a;'>📝 יצירת הזמנה חדשה</h1>", unsafe_allow_html=True)
current_step = get_session_value('wizard_step', 1)
show_progress_bar(current_step)
st.markdown("---")

# שלב 1: בחירת סוג מוצר
if current_step == 1:
    st.markdown("<h3 class='step-header'>שלב 1: בחירת סוג חבילה</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✈️ חבילה מלאה (טיסה + מלון + כרטיס)", use_container_width=True):
            set_session_value('order_data', {'package_type': 'חבילה מלאה'})
            set_session_value('wizard_step', 2)
            st.rerun()
    with col2:
        if st.button("🎫 כרטיסים בלבד", use_container_width=True):
            set_session_value('order_data', {'package_type': 'כרטיסים בלבד'})
            set_session_value('wizard_step', 2)
            st.rerun()

# שלב 2: פרטי אירוע
elif current_step == 2:
    st.markdown("<h3 class='step-header'>שלב 2: פרטי האירוע</h3>", unsafe_allow_html=True)
    order_data = get_session_value('order_data', {})
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            event_name = st.text_input("שם האירוע", value=order_data.get('event_name', ''))
            event_date = st.date_input("תאריך האירוע")
        with col2:
            event_location = st.text_input("מקום האירוע (עיר/אצטדיון)", value=order_data.get('event_location', ''))
            num_tickets = st.number_input("מספר כרטיסים", min_value=1, value=order_data.get('num_tickets', 1))
            
    if order_data.get('package_type') == 'חבילה מלאה':
        st.markdown("#### פרטי מלון")
        col1, col2 = st.columns(2)
        with col1:
            hotel_name = st.text_input("שם המלון", value=order_data.get('hotel_name', ''))
        with col2:
            hotel_nights = st.number_input("מספר לילות", min_value=1, value=order_data.get('hotel_nights', 1))

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ חזור"):
            set_session_value('wizard_step', 1)
            st.rerun()
    with c2:
        if st.button("המשך לפרטי לקוח ➡️", type="primary"):
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
    st.markdown("<h3 class='step-header'>שלב 3: פרטי לקוח</h3>", unsafe_allow_html=True)
    order_data = get_session_value('order_data', {})
    
    col1, col2, col3 = st.columns(3)
    with col1:
        customer_name = st.text_input("שם הלקוח", value=order_data.get('customer_name', ''))
    with col2:
        customer_email = st.text_input("אימייל", value=order_data.get('customer_email', ''))
    with col3:
        customer_phone = st.text_input("טלפון", value=order_data.get('customer_phone', ''))

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ חזור"):
            set_session_value('wizard_step', 2)
            st.rerun()
    with c2:
        if st.button("המשך לסיכום ➡️", type="primary"):
            order_data.update({
                'customer_name': customer_name,
                'customer_email': customer_email,
                'customer_phone': customer_phone
            })
            set_session_value('order_data', order_data)
            set_session_value('wizard_step', 4)
            st.rerun()

# שלב 4: סיכום ואישור
elif current_step == 4:
    st.markdown("<h3 class='step-header'>שלב 4: סיכום הזמנה</h3>", unsafe_allow_html=True)
    order_data = get_session_value('order_data', {})
    
    col1, col2 = st.columns(2)
    with col1:
        st.info("📋 פרטי האירוע")
        st.write(f"**סוג:** {order_data.get('package_type')}")
        st.write(f"**אירוע:** {order_data.get('event_name')}")
        st.write(f"**תאריך:** {order_data.get('event_date')}")
        st.write(f"**כרטיסים:** {order_data.get('num_tickets')}")
    with col2:
        st.info("👤 פרטי הלקוח")
        st.write(f"**שם:** {order_data.get('customer_name')}")
        st.write(f"**טלפון:** {order_data.get('customer_phone')}")
        st.write(f"**אימייל:** {order_data.get('customer_email')}")

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("⬅️ חזור"):
            set_session_value('wizard_step', 3)
            st.rerun()
    with c2:
        if st.button("❌ ביטול", type="secondary"):
            set_session_value('wizard_step', 1)
            set_session_value('order_data', {})
            st.rerun()
    with c3:
        if st.button("✅ אשר וצור הזמנה", type="primary"):
            # כאן תבוא הלוגיקה של השמירה
            st.success("ההזמנה נוצרה בהצלחה! (סימולציה)")
            # save_order_to_db(order_data)
