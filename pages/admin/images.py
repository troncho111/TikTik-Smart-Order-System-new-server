"""
Image Gallery Page - TikTik Smart Order System
עמוד ניהול גלריית תמונות
"""

import streamlit as st
from ui_helpers import render_header
from PIL import Image
import os
from models import AtmosphereImage, EventType, get_db


def page_image_gallery():
    """Admin page for managing atmosphere images"""
    render_header()
    
    st.markdown("""
    <style>
    .image-card {
        background: white;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        padding: 10px;
        margin-bottom: 15px;
        transition: transform 0.2s, box-shadow 0.2s;
    }
    .image-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
    }
    .image-card img {
        border-radius: 8px;
        width: 100%;
        height: 150px;
        object-fit: cover;
    }
    .image-card-name {
        font-size: 12px;
        color: #666;
        margin-top: 8px;
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .gallery-stats {
        background: linear-gradient(135deg, #667eea22, #764ba222);
        border-radius: 10px;
        padding: 15px;
        margin: 15px 0;
    }
    .stat-item {
        display: inline-block;
        margin: 0 20px;
        text-align: center;
    }
    .stat-number {
        font-size: 24px;
        font-weight: bold;
        color: #667eea;
    }
    .stat-label {
        font-size: 12px;
        color: #666;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לתפריט הראשי"):
        st.session_state.admin_page = None
        st.rerun()
    
    st.markdown("### 🖼️ ניהול תמונות אווירה")
    st.markdown("העלה תמונות אווירה לפי קטגוריה. התמונות ישמשו באופן אוטומטי ביצירת הזמנות.")
    
    category_options = {
        "⚽ כדורגל": EventType.FOOTBALL,
        "🎵 הופעה": EventType.CONCERT,
        "🎭 אחר": EventType.OTHER
    }
    
    db = get_db()
    if db:
        stats_html = '<div class="gallery-stats" style="text-align: center;">'
        for cat_name, cat_enum in category_options.items():
            count = db.query(AtmosphereImage).filter(
                AtmosphereImage.category == cat_enum,
                AtmosphereImage.is_active == True
            ).count()
            stats_html += f'<div class="stat-item"><div class="stat-number">{count}</div><div class="stat-label">{cat_name}</div></div>'
        stats_html += '</div>'
        st.markdown(stats_html, unsafe_allow_html=True)
        db.close()
    
    st.markdown("---")
    
    selected_category = st.selectbox("בחר קטגוריה להעלאה/צפייה", list(category_options.keys()))
    category = category_options[selected_category]
    
    st.markdown("#### ➕ העלאת תמונות חדשות")
    uploaded_files = st.file_uploader(
        "גרור תמונות לכאן או לחץ לבחירה",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        key="atmosphere_uploader"
    )
    
    if uploaded_files:
        st.info(f"📎 נבחרו {len(uploaded_files)} תמונות - לחץ על 'שמור תמונות' לשמירה במערכת")
        
        # Show preview of uploaded images with error handling
        preview_cols = st.columns(min(len(uploaded_files), 4))
        for idx, f in enumerate(uploaded_files[:4]):
            with preview_cols[idx]:
                try:
                    st.image(f, caption=f.name[:15] + "..." if len(f.name) > 15 else f.name, use_container_width=True)
                except Exception:
                    st.warning(f"⚠️ {f.name[:10]}...")
        if len(uploaded_files) > 4:
            st.caption(f"...ועוד {len(uploaded_files) - 4} תמונות נוספות")
        
        if st.button("💾 שמור תמונות", type="primary", use_container_width=True):
            db = get_db()
            if db:
                saved_count = 0
                for uploaded_file in uploaded_files:
                    folder = f"attached_assets/atmosphere_images/{category.value}"
                    os.makedirs(folder, exist_ok=True)
                    
                    filename = f"{uuid.uuid4().hex[:8]}_{uploaded_file.name}"
                    file_path = os.path.join(folder, filename)
                    
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    new_image = AtmosphereImage(
                        filename=uploaded_file.name,
                        category=category,
                        file_path=file_path,
                        is_active=True
                    )
                    db.add(new_image)
                    saved_count += 1
                
                db.commit()
                db.close()
                st.success(f"✅ הועלו {saved_count} תמונות בהצלחה!")
                st.rerun()
    
    st.markdown("---")
    st.markdown("#### 🖼️ תמונות קיימות")
    
    db = get_db()
    if db:
        images = db.query(AtmosphereImage).filter(
            AtmosphereImage.category == category,
            AtmosphereImage.is_active == True
        ).order_by(AtmosphereImage.created_at.desc()).all()
        
        if images:
            cols = st.columns(4)
            for idx, img in enumerate(images):
                with cols[idx % 4]:
                    if os.path.exists(img.file_path):
                        st.markdown('<div class="image-card">', unsafe_allow_html=True)
                        st.image(img.file_path, use_container_width=True)
                        short_name = img.filename[:20] + "..." if len(img.filename) > 20 else img.filename
                        st.markdown(f'<div class="image-card-name">{short_name}</div>', unsafe_allow_html=True)
                        if st.button("🗑️ מחק", key=f"del_{img.id}", use_container_width=True):
                            img.is_active = False
                            db.commit()
                            st.rerun()
                        st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("🖼️ אין תמונות בקטגוריה זו. העלה תמונות חדשות למעלה.")
        
        db.close()

