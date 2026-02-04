"""
Product Selector - Feature 1
Select product type and category before showing the main form.
"""

import streamlit as st


def get_category_label(category):
    """Get Hebrew label for category"""
    labels = {
        'concert': 'הופעה',
        'football': 'כדורגל כללי',
        'worldcup': 'מונדיאל 2026',
        'other': 'אחר'
    }
    return labels.get(category, 'כדורגל')


def reset_product_config():
    """Reset product configuration"""
    if 'product_config' in st.session_state:
        del st.session_state['product_config']
    st.rerun()


def render_product_selector():
    """
    Render product selector UI - Step A + B
    Returns True if product is selected, False otherwise
    """
    # Check if already selected
    if 'product_config' in st.session_state:
        config = st.session_state.product_config
        if config.get('selected'):
            return True  # Already selected
    
    # Show selection UI
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🎟️</div>
        <h1 style="color: #667eea; margin-bottom: 0.5rem;">בחר סוג מוצר</h1>
        <p style="color: #888; font-size: 1.1rem;">שלב ראשון - בחר מה תרצה להזמין</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Step A: Product Type
    st.markdown("### 🎯 שלב א': סוג המוצר")
    
    product_type = st.radio(
        "מה תרצה להזמין?",
        options=['tickets', 'package'],
        format_func=lambda x: "🎫 כרטיסים בלבד" if x == 'tickets' else "✈️ חבילה מלאה (טיסה + מלון + כרטיס)",
        horizontal=True,
        key="product_type_selector"
    )
    
    st.markdown("---")
    
    # Step B: Category
    st.markdown("### 📂 שלב ב': קטגוריית האירוע")
    
    category = st.radio(
        "לאיזה סוג אירוע?",
        options=['concert', 'football', 'worldcup'],
        format_func=lambda x: {
            'concert': '🎤 הופעה',
            'football': '⚽ כדורגל כללי',
            'worldcup': '🏆 מונדיאל 2026'
        }[x],
        horizontal=True,
        key="category_selector"
    )
    
    st.markdown("---")
    
    # Continue button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("➡️ המשך לטופס", type="primary", use_container_width=True):
            # Save selection
            st.session_state.product_config = {
                'selected': True,
                'product_type': product_type,
                'category': category,
                'label': get_category_label(category),
                'timestamp': st.session_state.get('timestamp', None)
            }
            st.rerun()
    
    return False  # Not selected yet


def render_product_info():
    """Render selected product info with reset button"""
    if 'product_config' not in st.session_state:
        return
    
    config = st.session_state.product_config
    if not config.get('selected'):
        return
    
    # Product info badge
    product_icon = "🎫" if config['product_type'] == 'tickets' else "✈️"
    product_text = "כרטיסים בלבד" if config['product_type'] == 'tickets' else "חבילה מלאה"
    
    category_icon = {
        'concert': '🎤',
        'football': '⚽',
        'worldcup': '🏆'
    }.get(config['category'], '📦')
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info(f"{product_icon} **מוצר:** {product_text}  |  {category_icon} **קטגוריה:** {config['label']}")
    
    with col2:
        if st.button("🔄 שנה בחירה", type="secondary", use_container_width=True):
            reset_product_config()


def init_product_config():
    """Initialize product config if not exists"""
    if 'product_config' not in st.session_state:
        st.session_state.product_config = {
            'selected': False,
            'product_type': 'tickets',
            'category': 'football',
            'label': 'כדורגל כללי'
        }
