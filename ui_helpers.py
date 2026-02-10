"""
UI helpers - תמונות אווירה, badges, כותרת ועזרים לממשק
"""

import os
import random
import streamlit as st
from models import get_db, AtmosphereImage, EventType, OrderStatus


def render_header():
    """הצגת כותרת האפליקציה"""
    st.markdown("""
    <div class="header-container">
        <h1>🎟️ TikTik Smart Order System</h1>
        <p>מערכת חכמה ליצירת הצעות מחיר והזמנות מקצועיות</p>
    </div>
    """, unsafe_allow_html=True)


def _event_type_to_category(event_type):
    """ממיר סוג אירוע (עברית או אנגלית) ל-EventType."""
    if event_type is None:
        return EventType.FOOTBALL
    s = (event_type or "").strip().lower()
    if s in ("כדורגל", "football", "ספורט", "sport"):
        return EventType.FOOTBALL
    if s in ("הופעה", "concert"):
        return EventType.CONCERT
    if s in ("אחר", "other"):
        return EventType.OTHER
    return EventType.FOOTBALL


def get_event_type_from_hebrew(event_type):
    """ממיר סוג אירוע (עברית או אנגלית) ל-EventType. API לצורך שימוש ב-order_service."""
    return _event_type_to_category(event_type)


def get_status_badge(status):
    """
    קבלת badge HTML לסטטוס הזמנה.

    Args:
        status: סטטוס ההזמנה (OrderStatus או str)

    Returns:
        str: HTML של badge
    """
    status_map = {
        OrderStatus.DRAFT: ("🟡", "#FFA500", "טיוטה"),
        OrderStatus.SENT: ("🔵", "#3498db", "נשלח"),
        OrderStatus.VIEWED: ("👁️", "#9b59b6", "נצפה"),
        OrderStatus.SIGNED: ("✅", "#27ae60", "נחתם"),
        OrderStatus.CANCELLED: ("🔴", "#e74c3c", "בוטל"),
    }
    entry = status_map.get(status)
    if not entry and status is not None:
        val = getattr(status, "value", str(status))
        for s, e in status_map.items():
            if getattr(s, "value", s) == val:
                entry = e
                break
    if entry:
        emoji, color, label = entry
        return f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">{emoji} {label}</span>'
    label = getattr(status, "value", str(status)) if status else ""
    return f'<span style="background-color: #95a5a6; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">⚪ {label}</span>'


def get_random_atmosphere_image(event_type=None):
    """
    מחזיר נתיב לתמונת אווירה אחת (לעמוד השער ב-PDF).
    עדיפות: 1) רשומה ב-DB (AtmosphereImage) 2) קבצים בתיקיות 3) ברירת מחדל.
    """
    app_dir = os.path.dirname(os.path.abspath(__file__))
    category = _event_type_to_category(event_type)
    category_value = category.value  # 'football', 'concert', 'other'

    # 1) מהמאגר ב-DB
    try:
        db = get_db()
        if db:
            row = (
                db.query(AtmosphereImage)
                .filter(
                    AtmosphereImage.category == category,
                    AtmosphereImage.is_active == True,
                )
                .order_by(AtmosphereImage.id)
                .limit(50)
                .all()
            )
            if row:
                chosen = random.choice(row)
                path = getattr(chosen, "file_path", None) or getattr(chosen, "filename", None)
                if path:
                    if os.path.isabs(path) and os.path.isfile(path):
                        return path
                    full = os.path.join(app_dir, path) if not os.path.isabs(path) else path
                    if os.path.isfile(full):
                        return full
                    if os.path.isfile(path):
                        return path
    except Exception:
        pass

    # 2) מתיקיות attached_assets/atmosphere_images/{football,concert,other}
    folder = os.path.join(app_dir, "attached_assets", "atmosphere_images", category_value)
    if os.path.isdir(folder):
        exts = (".jpg", ".jpeg", ".png", ".webp")
        files = [
            os.path.join(folder, f)
            for f in os.listdir(folder)
            if f.lower().endswith(exts) and os.path.isfile(os.path.join(folder, f))
        ]
        if files:
            return random.choice(files)

    # 3) ברירת מחדל לפי סוג
    assets_dir = os.path.join(app_dir, "assets")
    if category == EventType.CONCERT:
        default = os.path.join(assets_dir, "concert_bg.jpg")
    else:
        default = os.path.join(assets_dir, "cover_page.jpg")
    if os.path.isfile(default):
        return default
    cover = os.path.join(app_dir, "cover_page.jpg")
    if os.path.isfile(cover):
        return cover
    concert = os.path.join(app_dir, "concert_bg.jpg")
    if os.path.isfile(concert):
        return concert
    return None
