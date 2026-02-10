#!/usr/bin/env python3
"""Extract page_new_order and helper functions"""

with open('/mnt/user-data/uploads/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract show_product_selection (1312-1371)
product_sel = ''.join(lines[1311:1371])

# Extract show_event_selection (1372-1463)
event_sel = ''.join(lines[1371:1463])

# Extract show_selection_summary (1464-1494)
summary = ''.join(lines[1463:1494])

# Extract page_new_order (1495-4721) - This is HUGE!
new_order = ''.join(lines[1494:4721])

# Write to new_order module
import os
os.makedirs('/home/claude/tiktik_refactored/pages/new_order', exist_ok=True)

# Create __init__.py
with open('/home/claude/tiktik_refactored/pages/new_order/__init__.py', 'w') as f:
    f.write('"""New Order Module - TikTik Smart Order System"""\n')
    f.write('from .main import page_new_order\n')
    f.write('from .helpers import show_product_selection, show_event_selection, show_selection_summary\n')

# Write helpers.py
header_helpers = '''"""
New Order Helpers - TikTik Smart Order System
פונקציות עזר ליצירת הזמנה חדשה
"""

import streamlit as st
'''

with open('/home/claude/tiktik_refactored/pages/new_order/helpers.py', 'w') as f:
    f.write(header_helpers)
    f.write('\n')
    f.write(product_sel)
    f.write('\n')
    f.write(event_sel)
    f.write('\n')
    f.write(summary)

# Write main.py
header_main = '''"""
New Order Main Page - TikTik Smart Order System
עמוד יצירת הזמנה חדשה - פונקציה ראשית
"""

import streamlit as st
import os
import json
from datetime import datetime, timedelta
from PIL import Image
import io
import random
from models import get_db, PackageTemplate, EventType, generate_order_number
from services.pdf_service import generate_pdf
from services.order_service import save_order_to_db
from services.concert_service import (
    get_saved_concerts, save_concert_to_favorites,
    get_saved_artists, save_artist_to_favorites
)
from ui_helpers import get_random_atmosphere_image
from passport_ocr import extract_passport_data
from hotel_resolver import resolve_hotel_safe
from airports import get_airport_options, get_airport_code, format_airport_display
from flight_ocr import extract_flight_data
from airline_codes import get_airline_from_flight
from streamlit_paste_button import paste_image_button
from stadium_api import get_team_info, get_team_map_path, get_all_teams
from concerts_service import fetch_venue_map_from_ticketmaster, is_ticketmaster_url
from .helpers import show_product_selection, show_event_selection, show_selection_summary

# Project paths
_APP_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
WORLDCUP_JSON_PATH = os.path.join(_APP_DIR, "worldcup2026.json")
WORLDCUP_STADIUMS_JSON_PATH = os.path.join(_APP_DIR, "worldcup_stadiums_mapping.json")
'''

with open('/home/claude/tiktik_refactored/pages/new_order/main.py', 'w') as f:
    f.write(header_main)
    f.write('\n')
    f.write(new_order)

print("✓ Extracted page_new_order!")
print(f"  - helpers.py: {len(product_sel) + len(event_sel) + len(summary)} chars")
print(f"  - main.py: {len(new_order)} chars")
