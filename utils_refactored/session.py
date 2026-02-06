"""
Session Utils - פונקציות עזר לניהול session ב-Streamlit
"""
import streamlit as st


def init_session_state(key, default_value):
    """
    אתחול ערך ב-session_state אם לא קיים
    
    Args:
        key: מפתח
        default_value: ערך ברירת מחדל
    """
    if key not in st.session_state:
        st.session_state[key] = default_value


def get_session_value(key, default=None):
    """
    קבלת ערך מ-session_state
    
    Args:
        key: מפתח
        default: ערך ברירת מחדל אם לא קיים
        
    Returns:
        הערך או default
    """
    return st.session_state.get(key, default)


def set_session_value(key, value):
    """
    הגדרת ערך ב-session_state
    
    Args:
        key: מפתח
        value: ערך
    """
    st.session_state[key] = value


def clear_session_key(key):
    """
    מחיקת מפתח מ-session_state
    
    Args:
        key: מפתח למחיקה
    """
    if key in st.session_state:
        del st.session_state[key]


def clear_all_session():
    """מחיקת כל ה-session_state"""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
