"""
Saved Concerts Page - TikTik Smart Order System
עמוד הופעות שמורות
"""

import streamlit as st
from services.concert_service import get_saved_concerts, delete_saved_concert


def page_saved_concerts():
    """Page for managing saved concerts and artists"""
    st.markdown("""
    <div class="header-container">
        <h1>⭐ אמנים והופעות שמורים</h1>
        <p>ניהול אמנים והופעות שנשמרו לשימוש חוזר</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לתפריט"):
        st.session_state.admin_page = None
        st.rerun()
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🎤 אמנים שמורים", "🎵 הופעות שמורות"])
    
    with tab1:
        saved_artists = get_saved_artists()
        
        if not saved_artists:
            st.info("🎤 אין אמנים שמורים. חפש אמן והוסף אותו לרשימה שלך.")
        else:
            st.markdown(f"### 🎤 {len(saved_artists)} אמנים שמורים")
            
            for artist in saved_artists:
                with st.container():
                    st.markdown('<div class="form-section">', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns([4, 1])
                    
                    with col1:
                        st.markdown(f"**⭐ {artist.get('name_he', artist.get('name_en', 'לא ידוע'))}**")
                        if artist.get('genre'):
                            st.caption(f"🎸 {artist.get('genre')}")
                    
                    with col2:
                        if st.button("🗑️ מחק", key=f"delete_artist_{artist.get('db_id')}", use_container_width=True):
                            if delete_saved_artist(artist.get('db_id')):
                                st.success("✅ אמן הוסר!")
                                st.rerun()
                            else:
                                st.error("❌ שגיאה במחיקה")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")
    
    with tab2:
        saved_concerts = get_saved_concerts()
        
        if not saved_concerts:
            st.info("🎵 אין הופעות שמורות. הופעות שתשמור מההזמנה יופיעו כאן.")
        else:
            st.markdown(f"### 📋 {len(saved_concerts)} הופעות שמורות")
            
            for concert in saved_concerts:
                with st.container():
                    st.markdown('<div class="form-section">', unsafe_allow_html=True)
                    
                    col1, col2, col3 = st.columns([3, 2, 1])
                    
                    with col1:
                        st.markdown(f"**🎤 {concert.get('artist', 'לא ידוע')}**")
                        st.markdown(f"📍 {concert.get('venue', 'לא ידוע')}")
                        if concert.get('city') or concert.get('country'):
                            st.markdown(f"🌍 {concert.get('city', '')} {concert.get('country', '')}")
                    
                    with col2:
                        if concert.get('date'):
                            st.markdown(f"📅 {concert.get('date')}")
                        if concert.get('time'):
                            st.markdown(f"🕐 {concert.get('time')}")
                        if concert.get('category'):
                            st.markdown(f"🏷️ {concert.get('category')}")
                    
                    with col3:
                        if st.button("🗑️ מחק", key=f"delete_concert_{concert.get('id')}", use_container_width=True):
                            if delete_saved_concert(concert.get('id')):
                                st.success("✅ הופעה נמחקה!")
                                st.rerun()
                            else:
                                st.error("❌ שגיאה במחיקה")
                    
                    st.markdown('</div>', unsafe_allow_html=True)
                    st.markdown("")

