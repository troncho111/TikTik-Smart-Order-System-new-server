"""
Auth Helpers - ניהול אימות משתמשים וסשנים
TikTik Smart Order System
"""

import os
import secrets
import hashlib
from datetime import datetime, timedelta

import streamlit as st
from models import User, UserSession, get_db


def generate_session_token():
    """יצירת token אקראי לסשן"""
    return secrets.token_hex(32)


def create_user_session(user_id):
    """
    יצירת סשן חדש במסד הנתונים

    Args:
        user_id: מזהה משתמש

    Returns:
        str: token של הסשן או None במקרה של שגיאה
    """
    db = get_db()
    if not db:
        return None
    try:
        token = generate_session_token()
        expires_at = datetime.utcnow() + timedelta(days=30)

        session = UserSession(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(session)
        db.commit()
        return token
    except Exception as e:
        db.rollback()
        print(f"Error creating session: {e}")
        return None
    finally:
        db.close()


def validate_session_token(token):
    """
    אימות token של סשן והחזרת פרטי משתמש

    Args:
        token: token לאימות

    Returns:
        dict: פרטי משתמש או None אם לא תקף
    """
    if not token:
        return None
    db = get_db()
    if not db:
        return None
    try:
        session = db.query(UserSession).filter(
            UserSession.token == token,
            UserSession.expires_at > datetime.utcnow()
        ).first()

        if session:
            user = db.query(User).filter(User.id == session.user_id, User.is_active == True).first()
            if user:
                session.last_seen = datetime.utcnow()
                db.commit()
                return {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_admin': user.is_admin
                }
        return None
    except Exception as e:
        print(f"Error validating session: {e}")
        return None
    finally:
        db.close()


def delete_user_session(token):
    """
    מחיקת סשן ממסד הנתונים

    Args:
        token: token של הסשן למחיקה
    """
    if not token:
        return
    db = get_db()
    if not db:
        return
    try:
        db.query(UserSession).filter(UserSession.token == token).delete()
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def restore_session_from_token():
    """
    שחזור סשן משתמש מ-Streamlit query params

    Returns:
        dict: פרטי משתמש או None
    """
    try:
        params = dict(st.query_params)
    except Exception:
        params = {}

    token = params.get('token')

    # מערכת token חדשה מבוססת DB
    if token:
        user = validate_session_token(token)
        if user:
            return user

    # תמיכה לאחור במערכת hash ישנה
    old_token = params.get('session')
    user_id = params.get('uid')

    if old_token and user_id:
        db = get_db()
        if db:
            try:
                secret = os.environ.get('SESSION_SECRET', 'tiktik-secret-key')
                data = f"{user_id}-{secret}"
                expected_token = hashlib.sha256(data.encode()).hexdigest()[:32]

                user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
                if user and old_token == expected_token:
                    new_token = create_user_session(user.id)
                    if new_token:
                        st.query_params['token'] = new_token
                        for k in ['session', 'uid']:
                            if k in st.query_params:
                                del st.query_params[k]
                    return {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_admin': user.is_admin
                    }
            except Exception:
                pass
            finally:
                db.close()
    return None


def set_session_token(user):
    """
    הגדרת token סשן ב-URL query params (Streamlit)
    """
    token = create_user_session(user['id'])
    if token:
        st.query_params['token'] = token


def clear_session_token():
    """
    ניקוי token סשן מ-query params
    """
    try:
        token = st.query_params.get('token')
        if token:
            delete_user_session(token)
        keys_to_remove = [k for k in st.query_params.keys() if k in ('token', 'session', 'uid')]
        for key in keys_to_remove:
            del st.query_params[key]
    except Exception:
        pass


def login_user(username: str, password: str):
    """
    התחברות משתמש

    Args:
        username: שם משתמש
        password: סיסמה

    Returns:
        dict: פרטי משתמש או None
    """
    if not username or not password:
        return None
    db = get_db()
    if not db:
        return None
    try:
        user = db.query(User).filter(
            (User.username == username) | (User.email == username),
            User.is_active == True
        ).first()
        if user and user.check_password(password):
            user.last_login = datetime.utcnow()
            db.commit()
            return {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name,
                'is_admin': user.is_admin
            }
        return None
    except Exception as e:
        print(f"Login error: {e}")
        return None
    finally:
        db.close()


def reset_user_password(identifier: str):
    """
    איפוס סיסמה - מייצר סיסמה זמנית ומעדכן במסד הנתונים.

    Args:
        identifier: שם משתמש או אימייל

    Returns:
        tuple: (success: bool, message: str)
    """
    if not identifier or not identifier.strip():
        return False, "נא להזין שם משתמש או אימייל"

    db = get_db()
    if not db:
        return False, "חיבור למסד הנתונים נכשל"

    try:
        user = db.query(User).filter(
            (User.username == identifier.strip()) | (User.email == identifier.strip()),
            User.is_active == True
        ).first()

        if not user:
            return False, "לא נמצא משתמש עם הפרטים שהזנת"

        temp_password = secrets.token_hex(4)
        user.set_password(temp_password)
        db.commit()

        # בהעדר שירות אימייל - מציגים את הסיסמה למשתמש
        return True, f"הסיסמה הזמנית שלך: {temp_password} (נא לשנותה בהתחברות)"
    except Exception as e:
        db.rollback()
        print(f"Reset password error: {e}")
        return False, "אירעה שגיאה בעת איפוס הסיסמה"
    finally:
        db.close()
