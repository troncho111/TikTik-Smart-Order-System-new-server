"""
User Management Page - TikTik Smart Order System
עמוד ניהול משתמשים
"""

import streamlit as st
from datetime import datetime
from models import User, get_db


def page_user_management():
    """Admin page for user management"""
    st.markdown("""
    <div class="header-container">
        <h1>👥 ניהול משתמשים</h1>
        <p>צור וערוך משתמשים במערכת</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לתפריט"):
        st.session_state.admin_page = None
        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### ➕ הוספת משתמש חדש")
        
        new_username = st.text_input("שם משתמש", key="new_user_username")
        new_fullname = st.text_input("שם מלא", key="new_user_fullname")
        new_email = st.text_input("אימייל", key="new_user_email")
        new_password = st.text_input("סיסמה", type="password", key="new_user_password")
        new_is_admin = st.checkbox("מנהל מערכת", key="new_user_admin")
        
        if st.button("✅ צור משתמש", use_container_width=True):
            if new_username and new_fullname and new_email and new_password:
                db = get_db()
                if db:
                    try:
                        existing = db.query(User).filter(
                            (User.username == new_username) | (User.email == new_email)
                        ).first()
                        if existing:
                            st.error("❌ שם משתמש או אימייל כבר קיימים")
                        else:
                            user = User(
                                username=new_username,
                                email=new_email,
                                full_name=new_fullname,
                                is_admin=new_is_admin,
                                is_active=True
                            )
                            user.set_password(new_password)
                            db.add(user)
                            db.commit()
                            st.success(f"✅ המשתמש {new_fullname} נוצר בהצלחה!")
                            st.rerun()
                    except Exception as e:
                        db.rollback()
                        st.error(f"❌ שגיאה: {str(e)}")
                    finally:
                        db.close()
            else:
                st.warning("⚠️ נא למלא את כל השדות")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown("### 📋 משתמשים קיימים")
        
        db = get_db()
        if db:
            users = db.query(User).order_by(User.created_at.desc()).all()
            for user in users:
                status = "🟢" if user.is_active else "🔴"
                admin_badge = " 👑" if user.is_admin else ""
                st.markdown(f"""
                <div class="passenger-item">
                    <strong>{status} {user.full_name}{admin_badge}</strong><br>
                    <small>@{user.username} | {user.email}</small>
                </div>
                """, unsafe_allow_html=True)
                
                if user.username != "admin":
                    with st.expander("🔧 פעולות"):
                        new_pass = st.text_input("סיסמה חדשה", type="password", key=f"new_pass_{user.id}", placeholder="השאר ריק לאיפוס ל-123456")
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            if st.button("🔄 שנה סיסמה", key=f"reset_{user.id}"):
                                password_to_set = new_pass if new_pass else "123456"
                                user.set_password(password_to_set)
                                db.commit()
                                if new_pass:
                                    st.success(f"✅ הסיסמה שונתה!")
                                else:
                                    st.success(f"✅ סיסמה אופסה ל-123456")
                        with col_b:
                            if user.is_active:
                                if st.button("🚫 השבת", key=f"disable_{user.id}"):
                                    user.is_active = False
                                    db.commit()
                                    st.rerun()
                            else:
                                if st.button("✅ הפעל", key=f"enable_{user.id}"):
                                    user.is_active = True
                                    db.commit()
                                    st.rerun()
                        with col_c:
                            if user.is_admin:
                                if st.button("👤 הסר מנהל", key=f"demote_{user.id}"):
                                    user.is_admin = False
                                    db.commit()
                                    st.rerun()
                            else:
                                if st.button("👑 הפוך למנהל", key=f"promote_{user.id}"):
                                    user.is_admin = True
                                    db.commit()
                                    st.rerun()
                        
                        st.markdown("---")
                        delete_key = f"delete_confirm_{user.id}"
                        if delete_key not in st.session_state:
                            st.session_state[delete_key] = False
                        
                        if not st.session_state[delete_key]:
                            if st.button("🗑️ מחק משתמש", key=f"delete_{user.id}", type="secondary"):
                                st.session_state[delete_key] = True
                                st.rerun()
                        else:
                            st.warning(f"⚠️ האם אתה בטוח שברצונך למחוק את {user.full_name}?")
                            col_yes, col_no = st.columns(2)
                            with col_yes:
                                if st.button("✅ כן, מחק", key=f"confirm_delete_{user.id}", type="primary"):
                                    try:
                                        db.delete(user)
                                        db.commit()
                                        st.success(f"✅ המשתמש {user.full_name} נמחק!")
                                        st.session_state[delete_key] = False
                                        st.rerun()
                                    except Exception as e:
                                        db.rollback()
                                        st.error(f"❌ שגיאה במחיקה: {str(e)}")
                            with col_no:
                                if st.button("❌ ביטול", key=f"cancel_delete_{user.id}"):
                                    st.session_state[delete_key] = False
                                    st.rerun()
            db.close()
        
        st.markdown('</div>', unsafe_allow_html=True)

