"""
ממשק אשף להזמנה חדשה - עיצוב מקורי משוחזר
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
        col1, col2 = st.columns(2)
        with col1:
            event_name = st.text_input("שם האירוע", value=order_data.get('event_name', ''))
            event_date = st.date_input("תאריך האירוע")
        with col2:
            event_location = st.text_input("מקום האירוע", value=order_data.get('event_location', ''))
            num_tickets = st.number_input("מספר כרטיסים", min_value=1, value=order_data.get('num_tickets', 1))
            
        if order_data.get('package_type') == 'חבילה מלאה':
            st.markdown("#### פרטי מלון")
            col1, col2 = st.columns(2)
            with col1:
                hotel_name = st.text_input("שם המלון", value=order_data.get('hotel_name', ''))
            with col2:
                hotel_nights = st.number_input("מספר לילות", min_value=1, value=order_data.get('hotel_nights', 1))
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
        st.markdown("<div class='form-section'><h3>שלב 3: פרטי לקוח</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            customer_name = st.text_input("שם הלקוח", value=order_data.get('customer_name', ''))
        with col2:
            customer_email = st.text_input("אימייל", value=order_data.get('customer_email', ''))
        with col3:
            customer_phone = st.text_input("טלפון", value=order_data.get('customer_phone', ''))
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

    c1, c2 = st.columns(2)
    with c1:
        if st.button("⬅️ חזור"):
            set_session_value('wizard_step', 3)
            st.rerun()
    with c2:
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
