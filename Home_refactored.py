"""
TikTik Smart Order System - עמוד ראשי (עיצוב מקורי משוחזר)
"""
import streamlit as st
import os

st.set_page_config(
    page_title="TikTik Smart Order System",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# שחזור ה-CSS המקורי של המשתמש אחד-לאחד
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

.header-container {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.header-container h1 {
    color: #fff;
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    text-align: center;
}

.header-container p {
    color: #a0a0a0;
    font-size: 1.1rem;
    text-align: center;
}

.order-card {
    background: #1e1e2e;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border: 1px solid #333;
    transition: all 0.3s ease;
    color: white;
}

.order-card:hover {
    border-color: #667eea;
    transform: translateY(-2px);
}

/* Sidebar fix */
[data-testid="stSidebar"] {
    direction: rtl !important;
}
</style>
"""

st.markdown(RTL_CSS, unsafe_allow_html=True)

# שחזור ה-Header המקורי
st.markdown("""
<div class="header-container">
    <h1>🎟️ TikTik Smart Order System</h1>
    <p>מערכת ניהול הזמנות חכמה - כרטיסים וחבילות</p>
</div>
""", unsafe_allow_html=True)

# הצגת כרטיסי ניווט בסגנון המקורי
st.markdown("### 🚀 פעולות מהירות")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="order-card">
        <h2 style='text-align: center;'>📝</h2>
        <h3 style='text-align: center; color: #667eea;'>הזמנה חדשה</h3>
        <p style='text-align: center; color: #a0a0a0;'>יצירת הזמנה חדשה ללקוח בממשק אשף נוח</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("התחל הזמנה", key="btn_new_order"):
        st.switch_page("pages/1_New_Order_Wizard.py")

with col2:
    st.markdown("""
    <div class="order-card">
        <h2 style='text-align: center;'>📋</h2>
        <h3 style='text-align: center; color: #667eea;'>ניהול הזמנות</h3>
        <p style='text-align: center; color: #a0a0a0;'>צפייה, עריכה ומעקב אחר הזמנות קיימות</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("לניהול הזמנות", key="btn_manage"):
        # st.switch_page("pages/2_Order_Management.py")
        st.info("בקרוב...")

with col3:
    st.markdown("""
    <div class="order-card">
        <h2 style='text-align: center;'>📊</h2>
        <h3 style='text-align: center; color: #667eea;'>דוחות ונתונים</h3>
        <p style='text-align: center; color: #a0a0a0;'>ניתוח נתונים וייצוא דוחות למערכת</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("לצפייה בדוחות", key="btn_reports"):
        st.info("בקרוב...")
