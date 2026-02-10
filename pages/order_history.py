"""
Order History Page - TikTik Smart Order System
עמוד היסטוריית הזמנות
"""

import streamlit as st
from datetime import datetime
from services.order_service import get_all_orders, delete_order
from ui_helpers import get_status_badge, render_header
from pdf_generator import generate_pdf


def page_order_history():
    """Order history page"""
    render_header()
    
    st.markdown("### 📋 היסטוריית הזמנות")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        search_query = st.text_input("🔍 חיפוש", placeholder="חפש לפי שם לקוח, אירוע, מספר הזמנה...")
    with col2:
        status_filter = st.selectbox("סינון לפי סטטוס", ["הכל", "טיוטה", "נשלח", "נצפה", "נחתם", "בוטל"])
    
    user = st.session_state.get('user', {})
    user_id = user.get('id')
    is_admin = user.get('is_admin', False)
    orders = get_all_orders(search_query, status_filter, user_id, is_admin)
    
    if not orders:
        st.info("לא נמצאו הזמנות")
        return
    
    st.markdown(f"**נמצאו {len(orders)} הזמנות**")
    
    for order in orders:
        with st.container():
            st.markdown(f"""
            <div class="order-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <h4 style="margin: 0; color: #667eea;">{order.order_number}</h4>
                        <p style="margin: 0.5rem 0;">{order.event_name}</p>
                        <p style="margin: 0; color: #888;">{order.customer_name} | {order.customer_email}</p>
                    </div>
                    <div style="text-align: left;">
                        {get_status_badge(order.status)}
                        <p style="margin: 0.5rem 0; font-size: 0.9rem; color: #888;">
                            {order.created_at.strftime('%d/%m/%Y %H:%M') if order.created_at else ''}
                        </p>
                        <p style="margin: 0; font-weight: bold; color: #38ef7d;">
                            {order.total_euro:.0f}€ = {order.total_nis:.0f}₪
                        </p>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("📄 צפה בפרטים", key=f"view_{order.id}"):
                    st.session_state.selected_order = order.id
            with col2:
                if order.status == OrderStatus.DRAFT:
                    if st.button("📧 שלח ללקוח", key=f"send_{order.id}"):
                        update_order_status(order.id, OrderStatus.SENT)
                        st.rerun()
            with col3:
                if order.status != OrderStatus.CANCELLED:
                    if st.button("❌ בטל", key=f"cancel_{order.id}"):
                        update_order_status(order.id, OrderStatus.CANCELLED)
                        st.rerun()
            with col4:
                delete_key = f"delete_{order.id}"
                confirm_key = f"confirm_delete_{order.id}"
                if st.session_state.get(confirm_key):
                    st.warning("בטוח למחוק?")
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("✅ כן", key=f"yes_{order.id}"):
                            if delete_order(order.id):
                                st.session_state[confirm_key] = False
                                st.rerun()
                    with c2:
                        if st.button("❌ לא", key=f"no_{order.id}"):
                            st.session_state[confirm_key] = False
                            st.rerun()
                else:
                    if st.button("🗑️ מחק", key=delete_key):
                        st.session_state[confirm_key] = True
                        st.rerun()

