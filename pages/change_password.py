"""
Change Password Page - TikTik Smart Order System
עמוד שינוי סיסמה
"""

import streamlit as st
from models import User, get_db


def page_change_password():
    """Page for users to change their own password"""
    st.markdown("""
    <div class="header-container">
        <h1>🔑 שינוי סיסמה</h1>
        <p>שנה את הסיסמה שלך</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לתפריט"):
        st.session_state.admin_page = None
        st.rerun()
    
    st.markdown("---")
    
    user = st.session_state.get('user', {})
    user_id = user.get('id')
    
    if not user_id:
        st.error("❌ לא נמצא משתמש מחובר")
        return
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown(f"### 👤 {user.get('full_name', 'משתמש')}")
        st.markdown(f"📧 {user.get('email', '')}")
        
        st.markdown("---")
        st.markdown("##### 🔐 הזן סיסמה חדשה")
        
        current_password = st.text_input("סיסמה נוכחית", type="password", key="current_pass")
        new_password = st.text_input("סיסמה חדשה", type="password", key="new_pass")
        confirm_password = st.text_input("אימות סיסמה חדשה", type="password", key="confirm_pass")
        
        if st.button("✅ שנה סיסמה", use_container_width=True):
            if not current_password or not new_password or not confirm_password:
                st.warning("⚠️ נא למלא את כל השדות")
            elif new_password != confirm_password:
                st.error("❌ הסיסמאות החדשות לא תואמות")
            elif len(new_password) < 4:
                st.error("❌ הסיסמה חייבת להכיל לפחות 4 תווים")
            else:
                db = get_db()
                if db:
                    try:
                        db_user = db.query(User).filter(User.id == user_id).first()
                        if db_user and db_user.check_password(current_password):
                            db_user.set_password(new_password)
                            db.commit()
                            st.success("✅ הסיסמה שונתה בהצלחה!")
                        else:
                            st.error("❌ הסיסמה הנוכחית שגויה")
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ שגיאה: {str(e)}")
                    finally:
                        db.close()
        
        st.markdown('</div>', unsafe_allow_html=True)

