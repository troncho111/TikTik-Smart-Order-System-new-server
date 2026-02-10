"""
Package Templates Page - TikTik Smart Order System
עמוד תבניות חבילות
"""

import streamlit as st
import json
from models import PackageTemplate, get_db, EventType


def page_package_templates():
    """Page for managing package templates"""
    st.markdown("""
    <div class="header-container">
        <h1>📦 חבילות קבועות</h1>
        <p>ניהול חבילות קבועות לשימוש חוזר</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("⬅️ חזרה לתפריט"):
        st.session_state.admin_page = None
        st.rerun()
    
    st.markdown("---")
    
    st.info("💡 **ליצור חבילה חדשה:** מלא את טופס ההזמנה הרגיל ולחץ על '📦 שמור כחבילה קבועה' בסוף.")
    
    st.markdown("### 📋 חבילות שמורות")
    
    db = get_db()
    packages = []
    if db:
        try:
            packages = db.query(PackageTemplate).filter(PackageTemplate.is_active == True).order_by(PackageTemplate.created_at.desc()).all()
        except:
            pass
        finally:
            db.close()
    
    if not packages:
        st.info("📦 אין חבילות שמורות. לך להזמנה חדשה ושמור חבילה משם.")
    else:
        st.markdown(f"**סה\"כ: {len(packages)} חבילות**")
        
        for pkg in packages:
            pkg_data = pkg.to_dict()
            with st.container():
                st.markdown('<div class="form-section">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([4, 2, 2])
                
                with col1:
                    event_emoji = "🎤" if pkg_data.get('event_type') == 'concert' else "⚽" if pkg_data.get('event_type') == 'football' else "🎭"
                    st.markdown(f"### {event_emoji} {pkg_data.get('name', 'ללא שם')}")
                    if pkg_data.get('event_name'):
                        st.markdown(f"🎫 {pkg_data.get('event_name')}")
                    if pkg_data.get('venue'):
                        st.markdown(f"📍 {pkg_data.get('venue')}")
                
                with col2:
                    if pkg_data.get('event_date'):
                        st.markdown(f"📅 {pkg_data.get('event_date')}")
                    if pkg_data.get('ticket_category'):
                        st.markdown(f"🎟️ {pkg_data.get('ticket_category')}")
                    if pkg_data.get('package_price_euro'):
                        st.markdown(f"💶 {pkg_data.get('package_price_euro'):.0f}€ לאדם")
                
                with col3:
                    btn_col1, btn_col2 = st.columns(2)
                    with btn_col1:
                        if st.button("📋 שכפל", key=f"dup_pkg_{pkg.id}", use_container_width=True):
                            dup_db = get_db()
                            if dup_db:
                                try:
                                    new_pkg = PackageTemplate(
                                        name=f"{pkg.name} (עותק)",
                                        event_type=pkg.event_type,
                                        product_type=pkg.product_type,
                                        event_name=pkg.event_name,
                                        event_date=pkg.event_date,
                                        event_time=pkg.event_time,
                                        venue=pkg.venue,
                                        ticket_description=pkg.ticket_description,
                                        ticket_category=pkg.ticket_category,
                                        price_per_ticket_euro=pkg.price_per_ticket_euro,
                                        hotel_data=pkg.hotel_data,
                                        flight_data=pkg.flight_data,
                                        package_price_euro=pkg.package_price_euro,
                                        stadium_map_data=pkg.stadium_map_data,
                                        stadium_map_mime=pkg.stadium_map_mime,
                                        notes=pkg.notes
                                    )
                                    dup_db.add(new_pkg)
                                    dup_db.commit()
                                    st.success("✅ החבילה שוכפלה!")
                                    st.rerun()
                                except:
                                    dup_db.rollback()
                                finally:
                                    dup_db.close()
                    with btn_col2:
                        if st.button("🗑️", key=f"del_pkg_{pkg.id}", use_container_width=True):
                            del_db = get_db()
                            if del_db:
                                try:
                                    del_db.query(PackageTemplate).filter(PackageTemplate.id == pkg.id).update({'is_active': False})
                                    del_db.commit()
                                    st.success("✅ החבילה נמחקה!")
                                    st.rerun()
                                except:
                                    del_db.rollback()
                                finally:
                                    del_db.close()
                
                with st.expander("📄 פרטים מלאים"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**פרטי אירוע:**")
                        st.write(f"- סוג: {pkg_data.get('event_type')}")
                        st.write(f"- תאריך: {pkg_data.get('event_date')} {pkg_data.get('event_time')}")
                        st.write(f"- מקום: {pkg_data.get('venue')}")
                        st.write(f"- קטגוריה: {pkg_data.get('ticket_category')}")
                        if pkg_data.get('ticket_description'):
                            st.write(f"- תיאור: {pkg_data.get('ticket_description')}")
                    
                    with col2:
                        hotel = pkg_data.get('hotel', {})
                        if hotel:
                            st.markdown("**פרטי מלון:**")
                            st.write(f"- שם: {hotel.get('name', 'לא הוגדר')}")
                            st.write(f"- צ'ק-אין: {hotel.get('check_in', '')}")
                            st.write(f"- צ'ק-אאוט: {hotel.get('check_out', '')}")
                        
                        flights = pkg_data.get('flights', {})
                        if flights:
                            st.markdown("**טיסות:**")
                            outbound = flights.get('outbound', {})
                            if outbound:
                                st.write(f"- הלוך: {outbound.get('date')} {outbound.get('time')} | {outbound.get('flight_number')}")
                            ret = flights.get('return', {})
                            if ret:
                                st.write(f"- חזור: {ret.get('date')} {ret.get('time')} | {ret.get('flight_number')}")
                
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown("")

