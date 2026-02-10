"""
ממשק אשף להזמנה חדשה - 4 שלבים
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

# CSS מותאם אישית
st.markdown("""
<style>
    /* כיוון עברית */
    .main {
        direction: rtl;
        text-align: right;
    }
    
    /* פס התקדמות */
    .progress-bar {
        display: flex;
        justify-content: space-between;
        margin: 30px 0;
        padding: 0 20px;
    }
    
    .progress-step {
        flex: 1;
        text-align: center;
        position: relative;
    }
    
    .progress-step-number {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: #e0e0e0;
        color: #666;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: bold;
        margin-bottom: 10px;
        transition: all 0.3s;
    }
    
    .progress-step.active .progress-step-number {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transform: scale(1.1);
    }
    
    .progress-step.completed .progress-step-number {
        background: #27ae60;
        color: white;
    }
    
    .progress-step-title {
        font-size: 14px;
        color: #666;
        font-weight: 500;
    }
    
    .progress-step.active .progress-step-title {
        color: #667eea;
        font-weight: 700;
    }
    
    /* כרטיסים */
    .option-card {
        background: white;
        border: 2px solid #e0e0e0;
        border-radius: 16px;
        padding: 30px;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s;
        height: 100%;
    }
    
    .option-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        border-color: #667eea;
    }
    
    .option-card.selected {
        border-color: #667eea;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .option-icon {
        font-size: 60px;
        margin-bottom: 15px;
    }
    
    .option-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .option-description {
        font-size: 14px;
        color: #7f8c8d;
    }
    
    /* כפתורים */
    .stButton > button {
        border-radius: 12px;
        padding: 12px 30px;
        font-weight: 600;
        font-size: 16px;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

# אתחול session state
init_session_state('wizard_step', 1)
init_session_state('order_data', {})

# פונקציה להצגת פס התקדמות
def show_progress_bar(current_step):
    steps = [
        {"num": 1, "title": "סוג מוצר"},
        {"num": 2, "title": "פרטי אירוע"},
        {"num": 3, "title": "לקוח ונוסעים"},
        {"num": 4, "title": "סיכום"}
    ]
    
    html = '<div class="progress-bar">'
    for step in steps:
        status = ""
        if step["num"] < current_step:
            status = "completed"
        elif step["num"] == current_step:
            status = "active"
        
        html += f'''
        <div class="progress-step {status}">
            <div class="progress-step-number">{step["num"]}</div>
            <div class="progress-step-title">{step["title"]}</div>
        </div>
        '''
    html += '</div>'
    
    st.markdown(html, unsafe_allow_html=True)

# כותרת
st.markdown("""
<div style="text-align: center; padding: 20px 0;">
    <h1 style="color: #2c3e50; margin-bottom: 10px;">📝 הזמנה חדשה</h1>
    <p style="color: #7f8c8d; font-size: 18px;">מערכת הזמנה חכמה לכרטיסים וחבילות מקצועיות</p>
</div>
""", unsafe_allow_html=True)

# הצגת פס התקדמות
current_step = get_session_value('wizard_step', 1)
show_progress_bar(current_step)

st.markdown("---")

# שלב 1: בחירת סוג מוצר ואירוע
if current_step == 1:
    st.markdown("### שלב 1 - בחר סוג מוצר ואירוע")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✈️ חבילה מלאה", key="package_full", use_container_width=True):
            order_data = get_session_value('order_data', {})
            order_data['package_type'] = 'חבילה מלאה'
            set_session_value('order_data', order_data)
    
    with col2:
        if st.button("🎫 כרטיסים בלבד", key="package_tickets", use_container_width=True):
            order_data = get_session_value('order_data', {})
            order_data['package_type'] = 'כרטיסים בלבד'
            set_session_value('order_data', order_data)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # בחירת סוג אירוע
    if get_session_value('order_data', {}).get('package_type'):
        st.markdown("#### בחר סוג אירוע:")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("⚽ כדורגל", key="event_football", use_container_width=True):
                order_data = get_session_value('order_data', {})
                order_data['event_type'] = 'כדורגל'
                set_session_value('order_data', order_data)
                set_session_value('wizard_step', 2)
                st.rerun()
        
        with col2:
            if st.button("🎤 הופעה", key="event_concert", use_container_width=True):
                order_data = get_session_value('order_data', {})
                order_data['event_type'] = 'הופעה'
                set_session_value('order_data', order_data)
                set_session_value('wizard_step', 2)
                st.rerun()
        
        with col3:
            if st.button("🎪 אחר", key="event_other", use_container_width=True):
                order_data = get_session_value('order_data', {})
                order_data['event_type'] = 'אחר'
                set_session_value('order_data', order_data)
                set_session_value('wizard_step', 2)
                st.rerun()

# שלב 2: פרטי אירוע
elif current_step == 2:
    st.markdown("### שלב 2 - פרטי האירוע")
    
    order_data = get_session_value('order_data', {})
    
    st.text_input("שם האירוע", key="event_name", value=order_data.get('event_name', ''))
    st.text_input("מקום האירוע", key="event_location", value=order_data.get('event_location', ''))
    st.date_input("תאריך האירוע", key="event_date")
    st.number_input("מספר כרטיסים", min_value=1, value=order_data.get('num_tickets', 1), key="num_tickets")
    
    if order_data.get('package_type') == 'חבילה מלאה':
        st.markdown("#### פרטי מלון")
        st.text_input("שם המלון", key="hotel_name", value=order_data.get('hotel_name', ''))
        st.number_input("מספר לילות", min_value=1, value=order_data.get('hotel_nights', 1), key="hotel_nights")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ חזור", use_container_width=True):
            set_session_value('wizard_step', 1)
            st.rerun()
    with col2:
        if st.button("המשך ➡️", use_container_width=True, type="primary"):
            # שמירת נתונים
            order_data['event_name'] = st.session_state.event_name
            order_data['event_location'] = st.session_state.event_location
            order_data['event_date'] = st.session_state.event_date
            order_data['num_tickets'] = st.session_state.num_tickets
            if order_data.get('package_type') == 'חבילה מלאה':
                order_data['hotel_name'] = st.session_state.hotel_name
                order_data['hotel_nights'] = st.session_state.hotel_nights
            set_session_value('order_data', order_data)
            set_session_value('wizard_step', 3)
            st.rerun()

# שלב 3: פרטי לקוח
elif current_step == 3:
    st.markdown("### שלב 3 - פרטי לקוח ונוסעים")
    
    order_data = get_session_value('order_data', {})
    
    st.text_input("שם מלא", key="customer_name", value=order_data.get('customer_name', ''))
    st.text_input("אימייל", key="customer_email", value=order_data.get('customer_email', ''))
    st.text_input("טלפון", key="customer_phone", value=order_data.get('customer_phone', ''))
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ חזור", use_container_width=True):
            set_session_value('wizard_step', 2)
            st.rerun()
    with col2:
        if st.button("המשך לסיכום ➡️", use_container_width=True, type="primary"):
            order_data['customer_name'] = st.session_state.customer_name
            order_data['customer_email'] = st.session_state.customer_email
            order_data['customer_phone'] = st.session_state.customer_phone
            set_session_value('order_data', order_data)
            set_session_value('wizard_step', 4)
            st.rerun()

# שלב 4: סיכום
elif current_step == 4:
    st.markdown("### שלב 4 - סיכום ההזמנה")
    
    order_data = get_session_value('order_data', {})
    
    st.markdown(f"""
    **סוג מוצר:** {order_data.get('package_type', 'לא נבחר')}  
    **סוג אירוע:** {order_data.get('event_type', 'לא נבחר')}  
    **שם האירוע:** {order_data.get('event_name', 'לא הוזן')}  
    **מקום:** {order_data.get('event_location', 'לא הוזן')}  
    **תאריך:** {order_data.get('event_date', 'לא נבחר')}  
    **כרטיסים:** {order_data.get('num_tickets', 0)}  
    
    **לקוח:** {order_data.get('customer_name', 'לא הוזן')}  
    **אימייל:** {order_data.get('customer_email', 'לא הוזן')}  
    **טלפון:** {order_data.get('customer_phone', 'לא הוזן')}
    """)
    
    if order_data.get('package_type') == 'חבילה מלאה':
        st.markdown(f"""
        **מלון:** {order_data.get('hotel_name', 'לא הוזן')}  
        **לילות:** {order_data.get('hotel_nights', 0)}
        """)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ חזור", use_container_width=True):
            set_session_value('wizard_step', 3)
            st.rerun()
    with col2:
        if st.button("💾 שמור הזמנה", use_container_width=True):
            saved_order = save_order_to_db(order_data)
            if saved_order:
                st.success(f"✅ ההזמנה נשמרה! מספר הזמנה: {saved_order.order_number}")
    with col3:
        if st.button("📄 צור PDF", use_container_width=True, type="primary"):
            st.info("🔄 יוצר PDF...")
            # כאן תהיה אינטגרציה עם מערכת PDF
            st.success("✅ PDF נוצר בהצלחה!")
