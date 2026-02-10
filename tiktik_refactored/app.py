"""
TikTik Smart Order System - Main Application
מערכת TikTik לניהול הזמנות
"""

import streamlit as st
from models import init_db
from config import RTL_CSS
from services.ai_service import render_ai_chatbot
from auth_helpers import restore_session_from_token, clear_session_token

# Import all pages
from pages.login import page_login
from pages.new_order.main import page_new_order
from pages.order_history import page_order_history
from pages.export import page_export
from pages.packages import page_package_templates
from pages.proposals import page_proposals
from pages.saved_concerts import page_saved_concerts
from pages.help_beginner import page_beginner_guide
from pages.help import page_help
from pages.change_password import page_change_password
from pages.admin.images import page_image_gallery
from pages.admin.users import page_user_management
from pages.admin.maps import page_stadium_map_scraper


# Initialize database
init_db()

# Configure Streamlit page
st.set_page_config(
    page_title="TikTik Smart Order System",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply RTL CSS for Hebrew support
st.markdown(RTL_CSS, unsafe_allow_html=True)


def main():
    """Main application entry point with routing logic"""
    
    # Try to restore session from token if not logged in
    if not st.session_state.get('logged_in'):
        restored_user = restore_session_from_token()
        if restored_user:
            st.session_state.user = restored_user
            st.session_state.logged_in = True
    
    # Check if user is logged in
    if not st.session_state.get('logged_in'):
        page_login()
        st.stop()
    
    user = st.session_state.get('user', {})
    is_admin = user.get('is_admin', False)
    
    # Sidebar navigation
    st.sidebar.markdown(f"### 👤 {user.get('full_name', 'משתמש')}")
    if is_admin:
        st.sidebar.markdown("👑 מנהל מערכת")
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📌 תפריט")
    
    page = st.sidebar.radio(
        "בחר עמוד",
        ["🆕 הזמנה חדשה", "📋 היסטוריית הזמנות", "📊 ייצוא דוחות"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 🔧 כלים")
    if st.sidebar.button("📦 חבילות קבועות", use_container_width=True):
        st.session_state.admin_page = "packages"
        st.rerun()
    if st.sidebar.button("💼 הצעות ללקוח", use_container_width=True):
        st.session_state.admin_page = "proposals"
        st.rerun()
    if st.sidebar.button("📖 מדריך למתחיל", use_container_width=True):
        st.session_state.admin_page = "beginner_guide"
        st.rerun()
    if st.sidebar.button("❓ עזרה", use_container_width=True):
        st.session_state.admin_page = "help"
        st.rerun()
    if st.sidebar.button("⭐ הופעות שמורות", use_container_width=True):
        st.session_state.admin_page = "saved_concerts"
        st.rerun()
    if st.sidebar.button("🗺️ הורדת מפות", use_container_width=True):
        st.session_state.admin_page = "maps"
        st.rerun()
    if st.sidebar.button("🔑 שינוי סיסמה", use_container_width=True):
        st.session_state.admin_page = "change_password"
        st.rerun()
    
    if is_admin:
        st.sidebar.markdown("---")
        st.sidebar.markdown("##### 👑 ניהול")
        if st.sidebar.button("🖼️ ניהול תמונות", use_container_width=True):
            st.session_state.admin_page = "images"
            st.rerun()
        if st.sidebar.button("👥 ניהול משתמשים", use_container_width=True):
            st.session_state.admin_page = "users"
            st.rerun()
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 התנתק", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.user = None
        st.session_state.admin_page = None
        clear_session_token()
        st.rerun()
    
    # Render AI chatbot in sidebar
    render_ai_chatbot()
    
    # Route to appropriate page
    if st.session_state.get("admin_page") == "packages":
        page_package_templates()
    elif st.session_state.get("admin_page") == "proposals":
        page_proposals()
    elif st.session_state.get("admin_page") == "beginner_guide":
        page_beginner_guide()
    elif st.session_state.get("admin_page") == "help":
        page_help()
    elif st.session_state.get("admin_page") == "images":
        page_image_gallery()
    elif st.session_state.get("admin_page") == "maps":
        page_stadium_map_scraper()
    elif st.session_state.get("admin_page") == "saved_concerts":
        page_saved_concerts()
    elif st.session_state.get("admin_page") == "change_password":
        page_change_password()
    elif st.session_state.get("admin_page") == "users" and is_admin:
        page_user_management()
    elif page == "📋 היסטוריית הזמנות":
        page_order_history()
    elif page == "📊 ייצוא דוחות":
        page_export()
    else:
        page_new_order()


if __name__ == "__main__":
    main()
