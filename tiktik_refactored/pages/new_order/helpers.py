"""
New Order Helpers - TikTik Smart Order System
פונקציות עזר ליצירת הזמנה חדשה
"""

import streamlit as st

def show_product_selection():
    """Step 1: Product type selection"""
    st.markdown("## שלב 1 - בחר סוג מוצר")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            min-height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        " onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 15px 40px rgba(102, 126, 234, 0.5)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 30px rgba(102, 126, 234, 0.3)';">
            <div style="font-size: 5rem; margin-bottom: 1rem;">🎟️</div>
            <h2 style="color: white; font-size: 2rem; margin-bottom: 0.5rem; font-weight: 700;">כרטיסים בלבד</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0;">כרטיסים לאירוע בלבד</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("בחר כרטיסים בלבד", type="primary", use_container_width=True, key="btn_tickets"):
            st.session_state['product_type_selected'] = 'tickets_only'
            st.session_state['ui_step'] = 2
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
            padding: 3rem 2rem;
            border-radius: 20px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            min-height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(17, 153, 142, 0.3);
        " onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 15px 40px rgba(17, 153, 142, 0.5)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 30px rgba(17, 153, 142, 0.3)';">
            <div style="font-size: 5rem; margin-bottom: 1rem;">📦</div>
            <h2 style="color: white; font-size: 2rem; margin-bottom: 0.5rem; font-weight: 700;">חבילה מלאה</h2>
            <p style="color: rgba(255,255,255,0.9); font-size: 1.1rem; margin: 0;">טיסות + מלון + כרטיסים</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("בחר חבילה מלאה", type="primary", use_container_width=True, key="btn_package"):
            st.session_state['product_type_selected'] = 'full_package'
            st.session_state['ui_step'] = 2
            st.rerun()



def show_event_selection():
    """Step 2: Event type selection"""
    product = st.session_state.get('product_type_selected', 'tickets_only')
    label = "🎟️ כרטיסים" if product == 'tickets_only' else "📦 חבילה מלאה"
    
    st.markdown("## שלב 2 - בחר סוג אירוע")
    st.info(f"מוצר שנבחר: {label}")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3, gap="medium")
    
    with col1:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 2.5rem 1.5rem;
            border-radius: 20px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
        " onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 15px 40px rgba(240, 147, 251, 0.5)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 30px rgba(240, 147, 251, 0.3)';">
            <div style="font-size: 4.5rem; margin-bottom: 1rem;">🎤</div>
            <h2 style="color: white; font-size: 1.8rem; margin: 0; font-weight: 700;">הופעה</h2>
        </div>
        """, unsafe_allow_html=True)
        if st.button("בחר הופעה", type="primary", use_container_width=True, key="btn_concert"):
            st.session_state['event_type_selected'] = 'concert'
            st.session_state['ui_step'] = 3
            st.rerun()
    
    with col2:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            padding: 2.5rem 1.5rem;
            border-radius: 20px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(79, 172, 254, 0.3);
        " onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 15px 40px rgba(79, 172, 254, 0.5)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 30px rgba(79, 172, 254, 0.3)';">
            <div style="font-size: 4.5rem; margin-bottom: 1rem;">⚽</div>
            <h2 style="color: white; font-size: 1.8rem; margin: 0; font-weight: 700;">כדורגל</h2>
        </div>
        """, unsafe_allow_html=True)
        if st.button("בחר כדורגל", type="primary", use_container_width=True, key="btn_football"):
            st.session_state['event_type_selected'] = 'football'
            st.session_state['ui_step'] = 3
            st.rerun()
    
    with col3:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            padding: 2.5rem 1.5rem;
            border-radius: 20px;
            text-align: center;
            cursor: pointer;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            min-height: 250px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-shadow: 0 10px 30px rgba(250, 112, 154, 0.3);
        " onmouseover="this.style.transform='translateY(-8px)'; this.style.boxShadow='0 15px 40px rgba(250, 112, 154, 0.5)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 10px 30px rgba(250, 112, 154, 0.3)';">
            <div style="font-size: 4.5rem; margin-bottom: 1rem;">🏆</div>
            <h2 style="color: white; font-size: 1.8rem; margin: 0; font-weight: 700;">מונדיאל 2026</h2>
        </div>
        """, unsafe_allow_html=True)
        if st.button("בחר מונדיאל", type="primary", use_container_width=True, key="btn_worldcup"):
            st.session_state['event_type_selected'] = 'worldcup_2026'
            st.session_state['ui_step'] = 3
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔙 חזור לבחירת מוצר", key="btn_back", use_container_width=True):
        st.session_state['ui_step'] = 1
        st.rerun()



def show_selection_summary():
    """Display summary of selected product and event type with option to change"""
    product_type = st.session_state.get('product_type_selected')
    event_type = st.session_state.get('event_type_selected')
    
    # Product labels
    product_label = "🎟️ כרטיסים בלבד" if product_type == 'tickets_only' else "📦 חבילה מלאה"
    
    # Event labels
    event_labels = {
        'concert': '🎤 הופעה',
        'football': '⚽ כדורגל',
        'worldcup_2026': '🏆 מונדיאל 2026'
    }
    event_label = event_labels.get(event_type, '')
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info(f"📋 **בחירה:** {product_label}  |  {event_label}")
    
    with col2:
        if st.button("🔄 שנה בחירה", type="secondary", use_container_width=True, key="reset_selection"):
            st.session_state['ui_step'] = 1
            st.session_state['product_type_selected'] = None
            st.session_state['event_type_selected'] = None
            st.rerun()
    
    st.markdown("---")


