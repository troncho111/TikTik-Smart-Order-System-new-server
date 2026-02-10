"""
Login Page - TikTik Smart Order System
עמוד התחברות
"""

import streamlit as st
from auth_helpers import login_user, set_session_token, reset_user_password
from models import get_db, User


def page_login():
    """Login page with quick user selection"""
    st.markdown("""
    <div class="header-container">
        <h1>🎟️ TikTik Smart Order System</h1>
        <p>מערכת חכמה ליצירת הצעות מחיר והזמנות מקצועיות</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 🔐 התחברות למערכת")
        
        saved_users_display = []
        db = get_db()
        if db:
            try:
                users = db.query(User).filter(User.is_active == True).all()
                saved_users_display = [(u.username, u.full_name) for u in users]
            except:
                pass
            finally:
                db.close()
        
        if saved_users_display:
            st.markdown("##### ⚡ כניסה מהירה")
            user_options = ["-- בחר משתמש --"] + [f"{u[1]} ({u[0]})" for u in saved_users_display]
            selected_quick = st.selectbox("בחר משתמש", user_options, key="quick_user", label_visibility="collapsed")
            
            if selected_quick and selected_quick != "-- בחר משתמש --":
                quick_username = selected_quick.split("(")[-1].replace(")", "").strip()
                quick_password = st.text_input("סיסמה", type="password", key="quick_password")
                
                if st.button("🚀 התחבר", use_container_width=True, key="quick_login_btn"):
                    if quick_password:
                        user = login_user(quick_username, quick_password)
                        if user:
                            st.session_state.user = user
                            st.session_state.logged_in = True
                            set_session_token(user)
                            st.success(f"👋 שלום {user['full_name']}!")
                            st.rerun()
                        else:
                            st.error("❌ סיסמה שגויה")
                    else:
                        st.warning("⚠️ נא להזין סיסמה")
            
            st.markdown("---")
            with st.expander("📝 התחברות ידנית"):
                username = st.text_input("שם משתמש", key="login_username")
                password = st.text_input("סיסמה", type="password", key="login_password")
                
                if st.button("🚀 התחבר", use_container_width=True, key="manual_login_btn"):
                    if username and password:
                        user = login_user(username, password)
                        if user:
                            st.session_state.user = user
                            st.session_state.logged_in = True
                            set_session_token(user)
                            st.success(f"👋 שלום {user['full_name']}!")
                            st.rerun()
                        else:
                            st.error("❌ שם משתמש או סיסמה שגויים")
                    else:
                        st.warning("⚠️ נא למלא שם משתמש וסיסמה")
        else:
            username = st.text_input("שם משתמש", key="login_username")
            password = st.text_input("סיסמה", type="password", key="login_password")
            
            if st.button("🚀 התחבר", use_container_width=True):
                if username and password:
                    user = login_user(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.logged_in = True
                        set_session_token(user)
                        st.success(f"👋 שלום {user['full_name']}!")
                        st.rerun()
                    else:
                        st.error("❌ שם משתמש או סיסמה שגויים")
                else:
                    st.warning("⚠️ נא למלא שם משתמש וסיסמה")
        
        st.markdown("---")
        with st.expander("🔑 שכחתי סיסמה"):
            st.markdown("הזן את שם המשתמש או האימייל שלך ונשלח לך סיסמה זמנית:")
            reset_identifier = st.text_input("שם משתמש / אימייל", key="reset_identifier")
            
            if st.button("📧 שלח סיסמה זמנית", use_container_width=True, key="reset_password_btn"):
                if reset_identifier:
                    with st.spinner("מאפס סיסמה..."):
                        success, message = reset_user_password(reset_identifier)
                        if success:
                            st.success(f"✅ {message}")
                        else:
                            st.error(f"❌ {message}")
                else:
                    st.warning("⚠️ נא להזין שם משתמש או אימייל")
        
        st.markdown('</div>', unsafe_allow_html=True)

