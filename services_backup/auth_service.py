"""
Auth Service - ניהול אימות משתמשים וסשנים
"""
import os
import secrets
import hashlib
from datetime import datetime, timedelta
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
    except:
        db.rollback()
    finally:
        db.close()


def restore_session_from_token(query_params):
    """
    שחזור סשן משתמש מ-query params
    
    Args:
        query_params: פרמטרי URL
        
    Returns:
        dict: פרטי משתמש או None
    """
    token = query_params.get('token')
    
    # מערכת token חדשה מבוססת DB
    if token:
        user = validate_session_token(token)
        if user:
            return user
    
    # תמיכה לאחור במערכת hash ישנה
    old_token = query_params.get('session')
    user_id = query_params.get('uid')
    
    if old_token and user_id:
        db = get_db()
        if db:
            try:
                secret = os.environ.get('SESSION_SECRET', 'tiktik-secret-key')
                data = f"{user_id}-{secret}"
                expected_token = hashlib.sha256(data.encode()).hexdigest()[:32]
                
                user = db.query(User).filter(User.id == int(user_id), User.is_active == True).first()
                if user and old_token == expected_token:
                    # מעבר למערכת סשן חדשה
                    new_token = create_user_session(user.id)
                    if new_token:
                        query_params['token'] = new_token
                        # ניקוי פרמטרים ישנים
                        if 'session' in query_params:
                            del query_params['session']
                        if 'uid' in query_params:
                            del query_params['uid']
                    return {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_admin': user.is_admin
                    }
            except:
                pass
            finally:
                db.close()
    return None


def set_session_token(user, query_params):
    """
    הגדרת token סשן ב-URL query params
    
    Args:
        user: פרטי משתמש
        query_params: פרמטרי URL
    """
    token = create_user_session(user['id'])
    if token:
        query_params['token'] = token


def clear_session_token(query_params):
    """
    ניקוי token סשן מ-query params
    
    Args:
        query_params: פרמטרי URL
    """
    token = query_params.get('token')
    if token:
        delete_user_session(token)
        del query_params['token']
    if 'session' in query_params:
        del query_params['session']
    if 'uid' in query_params:
        del query_params['uid']
