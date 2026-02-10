"""
Configuration and Constants - TikTik Smart Order System
הגדרות וקבועים למערכת
"""

import os

# Project directories
APP_DIR = os.path.dirname(os.path.abspath(__file__))
WORLDCUP_JSON_PATH = os.path.join(APP_DIR, "worldcup2026.json")
WORLDCUP_STADIUMS_JSON_PATH = os.path.join(APP_DIR, "worldcup_stadiums_mapping.json")

# Assets directories
ASSETS_DIR = os.path.join(APP_DIR, "attached_assets")
ATMOSPHERE_IMAGES_DIR = os.path.join(ASSETS_DIR, "atmosphere_images")
CONCERT_VENUE_MAPS_DIR = os.path.join(ASSETS_DIR, "concert_venue_maps")
STOCK_IMAGES_DIR = os.path.join(ASSETS_DIR, "stock_images")
STADIUM_MAPS_DIR = os.path.join(APP_DIR, "stadium_maps")

# RTL CSS for Hebrew support
RTL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');

* {
    font-family: 'Heebo', sans-serif !important;
}

/* Fix icon text rendering issue - hide "ke" text from icon fonts */
[data-testid="stExpander"] summary span[data-testid="stMarkdownContainer"],
[data-testid="stExpander"] summary > span:first-child,
.stExpander summary,
details summary {
    font-size: inherit;
    unicode-bidi: isolate;
}

/* Hide any stray icon text before emojis */
[data-testid="stExpander"] summary::before,
[data-testid="stFileUploader"] label::before {
    content: none !important;
    display: none !important;
}

/* Ensure expander icon doesn't show fallback text */
[data-testid="stExpander"] svg + span,
[data-testid="stExpander"] details > summary > span:first-of-type {
    text-indent: 0;
}

/* Fix file uploader label */
[data-testid="stFileUploader"] > label {
    direction: rtl !important;
}

/* Hide stray icon-font characters that render as "ke" */
[class*="icon"]::before,
[class*="Icon"]::before {
    font-family: inherit !important;
}

.main .block-container {
    direction: rtl;
    text-align: right;
}

h1, h2, h3, h4, h5, h6, p, label, span, div {
    direction: rtl;
    text-align: right;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    direction: rtl;
    text-align: right;
}

.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 10px;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4);
}

.success-button > button {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%) !important;
}

.header-container {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 2rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
}

.header-container h1 {
    color: #fff;
    font-size: 2.5rem;
    margin-bottom: 0.5rem;
    text-align: center;
}

.header-container p {
    color: #a0a0a0;
    font-size: 1.1rem;
    text-align: center;
}

.form-section {
    background: #1e1e2e;
    padding: 1.5rem;
    border-radius: 15px;
    margin-bottom: 1.5rem;
    border: 1px solid #333;
}

.form-section h3 {
    color: #667eea;
    border-bottom: 2px solid #667eea;
    padding-bottom: 0.5rem;
    margin-bottom: 1rem;
}

.preview-box {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    padding: 2rem;
    border-radius: 15px;
    border: 2px solid #667eea;
    min-height: 400px;
}

.passenger-item {
    background: #2d2d3d;
    padding: 0.5rem 1rem;
    border-radius: 8px;
    margin: 0.3rem 0;
    border-right: 4px solid #667eea;
    color: #ffffff !important;
}

.price-display {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    color: white;
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 1rem;
}

.info-box {
    background: #2d2d3d;
    padding: 1rem;
    border-radius: 10px;
    border-right: 4px solid #ffc107;
    margin: 1rem 0;
}

.status-badge {
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 600;
    display: inline-block;
}

.status-draft { background: #6c757d; color: white; }
.status-sent { background: #007bff; color: white; }
.status-viewed { background: #ffc107; color: black; }
.status-signed { background: #28a745; color: white; }
.status-cancelled { background: #dc3545; color: white; }

.order-card {
    background: #1e1e2e;
    padding: 1.5rem;
    border-radius: 12px;
    margin-bottom: 1rem;
    border: 1px solid #333;
    transition: all 0.3s ease;
}

.order-card:hover {
    border-color: #667eea;
    transform: translateY(-2px);
}

/* MOBILE RESPONSIVE STYLES */
@media screen and (max-width: 768px) {
    [data-testid="stSidebar"],
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    header[data-testid="stHeader"] {
        display: none !important;
    }
    
    .main,
    .main > div,
    .block-container {
        width: 100% !important;
        max-width: 100% !important;
        margin: 0 !important;
        padding: 0.5rem !important;
    }
}
</style>
"""
