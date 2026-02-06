"""
TikTik Smart Order System - עמוד ראשי
"""
import streamlit as st

st.set_page_config(
    page_title="TikTik Smart Order System",
    page_icon="🎫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS מותאם אישית
st.markdown("""
<style>
    .main {
        direction: rtl;
        text-align: right;
    }
    
    .hero {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 60px 40px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .hero h1 {
        font-size: 48px;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    .hero p {
        font-size: 20px;
        opacity: 0.9;
    }
    
    .feature-card {
        background: white;
        border-radius: 16px;
        padding: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: all 0.3s;
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    
    .feature-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    
    .feature-title {
        font-size: 24px;
        font-weight: 700;
        margin-bottom: 10px;
        color: #2c3e50;
    }
    
    .feature-description {
        font-size: 16px;
        color: #7f8c8d;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Hero Section
st.markdown("""
<div class="hero">
    <h1>🎫 TikTik Smart Order System</h1>
    <p>מערכת הזמנה חכמה לכרטיסים וחבילות מקצועיות</p>
</div>
""", unsafe_allow_html=True)

# תכונות
st.markdown("## 🌟 תכונות המערכת")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📝</div>
        <div class="feature-title">הזמנה חדשה</div>
        <div class="feature-description">
            ממשק אשף פשוט וידידותי ליצירת הזמנות חדשות עם 4 שלבים ברורים
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📋</div>
        <div class="feature-title">ניהול הזמנות</div>
        <div class="feature-description">
            מעקב אחר כל ההזמנות, עדכון סטטוס, וייצוא נתונים בקלות
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📄</div>
        <div class="feature-title">PDF מקצועי</div>
        <div class="feature-description">
            יצירת טפסי הזמנה מעוצבים ומקצועיים ללקוחות
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🔍</div>
        <div class="feature-title">חיפוש חכם</div>
        <div class="feature-description">
            חיפוש מלונות, טיסות, ואירועים עם אינטגרציות חיצוניות
        </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">🤖</div>
        <div class="feature-title">AI עוזר</div>
        <div class="feature-description">
            צ'אט AI לעזרה ותמיכה בזמן אמת
        </div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="feature-card">
        <div class="feature-icon">📊</div>
        <div class="feature-title">ייצוא נתונים</div>
        <div class="feature-description">
            ייצוא הזמנות ל-Excel, CSV ופורמטים נוספים
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# קריאה לפעולה
st.markdown("""
<div style="text-align: center; padding: 40px 0;">
    <h2 style="color: #2c3e50; margin-bottom: 20px;">מוכנים להתחיל?</h2>
    <p style="color: #7f8c8d; font-size: 18px; margin-bottom: 30px;">
        בחרו "הזמנה חדשה" מהתפריט הצדדי כדי ליצור את ההזמנה הראשונה שלכם!
    </p>
</div>
""", unsafe_allow_html=True)

# Footer
st.markdown("""
<div style="text-align: center; padding: 20px; color: #95a5a6; font-size: 14px;">
    <p>TikTik Smart Order System © 2026 | Powered by Streamlit</p>
</div>
""", unsafe_allow_html=True)
