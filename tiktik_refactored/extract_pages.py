#!/usr/bin/env python3
"""
Script to extract functions from app.py into separate files
"""

import os

# Read original app.py
with open('/mnt/user-data/uploads/app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

def extract_function(start_line, end_line):
    """Extract function lines"""
    return ''.join(lines[start_line-1:end_line])

def write_file(path, content, header=""):
    """Write content to file with optional header"""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        if header:
            f.write(header + "\n\n")
        f.write(content)
    print(f"✓ Created: {path}")

# Base directory
base_dir = "/home/claude/tiktik_refactored"

# Extract page_login
login_start = 5077
login_end = 5178
login_content = extract_function(login_start, login_end)
login_header = '''"""
Login Page - TikTik Smart Order System
עמוד התחברות
"""

import streamlit as st
from auth_helpers import login_user, set_session_token, reset_user_password
'''
write_file(f"{base_dir}/pages/login.py", login_content, login_header)

# Extract page_order_history  
history_start = 4722
history_end = 4801
history_content = extract_function(history_start, history_end)
history_header = '''"""
Order History Page - TikTik Smart Order System
עמוד היסטוריית הזמנות
"""

import streamlit as st
from datetime import datetime
from services.order_service import get_all_orders, delete_order
from ui_helpers import get_status_badge
from pdf_generator import generate_pdf
'''
write_file(f"{base_dir}/pages/order_history.py", history_content, history_header)

# Extract page_export
export_start = 4802
export_end = 4910
export_content = extract_function(export_start, export_end)
export_header = '''"""
Export Page - TikTik Smart Order System
עמוד ייצוא דוחות
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from services.order_service import get_all_orders
from models import OrderStatus
'''
write_file(f"{base_dir}/pages/export.py", export_content, export_header)

# Extract page_image_gallery
gallery_start = 4911
gallery_end = 5076
gallery_content = extract_function(gallery_start, gallery_end)
gallery_header = '''"""
Image Gallery Page - TikTik Smart Order System
עמוד ניהול גלריית תמונות
"""

import streamlit as st
from PIL import Image
import os
from models import AtmosphereImage, EventType, get_db
'''
write_file(f"{base_dir}/pages/admin/images.py", gallery_content, gallery_header)

# Extract page_user_management
users_start = 5179
users_end = 5322
users_content = extract_function(users_start, users_end)
users_header = '''"""
User Management Page - TikTik Smart Order System
עמוד ניהול משתמשים
"""

import streamlit as st
from datetime import datetime
from models import User, get_db
'''
write_file(f"{base_dir}/pages/admin/users.py", users_content, users_header)

# Extract page_change_password
password_start = 5323
password_end = 5383
password_content = extract_function(password_start, password_end)
password_header = '''"""
Change Password Page - TikTik Smart Order System
עמוד שינוי סיסמה
"""

import streamlit as st
from models import User, get_db
'''
write_file(f"{base_dir}/pages/change_password.py", password_content, password_header)

# Extract page_package_templates
packages_start = 5384
packages_end = 5519
packages_content = extract_function(packages_start, packages_end)
packages_header = '''"""
Package Templates Page - TikTik Smart Order System
עמוד תבניות חבילות
"""

import streamlit as st
import json
from models import PackageTemplate, get_db, EventType
'''
write_file(f"{base_dir}/pages/packages.py", packages_content, packages_header)

# Extract page_proposals
proposals_start = 5520
proposals_end = 5739
proposals_content = extract_function(proposals_start, proposals_end)
proposals_header = '''"""
Client Proposals Page - TikTik Smart Order System
עמוד הצעות מחיר ללקוחות
"""

import streamlit as st
from datetime import datetime
from models import ClientProposal, ProposalStatus, get_db
'''
write_file(f"{base_dir}/pages/proposals.py", proposals_content, proposals_header)

# Extract page_saved_concerts
concerts_start = 5740
concerts_end = 5825
concerts_content = extract_function(concerts_start, concerts_end)
concerts_header = '''"""
Saved Concerts Page - TikTik Smart Order System
עמוד הופעות שמורות
"""

import streamlit as st
from services.concert_service import get_saved_concerts, delete_saved_concert
'''
write_file(f"{base_dir}/pages/saved_concerts.py", concerts_content, concerts_header)

# Extract page_beginner_guide
guide_start = 5826
guide_end = 6016
guide_content = extract_function(guide_start, guide_end)
guide_header = '''"""
Beginner Guide Page - TikTik Smart Order System
עמוד מדריך למתחילים
"""

import streamlit as st
'''
write_file(f"{base_dir}/pages/help_beginner.py", guide_content, guide_header)

# Extract page_help
help_start = 6017
help_end = 6269
help_content = extract_function(help_start, help_end)
help_header = '''"""
Help Page - TikTik Smart Order System
עמוד עזרה
"""

import streamlit as st
'''
write_file(f"{base_dir}/pages/help.py", help_content, help_header)

# Extract page_stadium_map_scraper
maps_start = 6270
maps_end = 6487
maps_content = extract_function(maps_start, maps_end)
maps_header = '''"""
Stadium Map Scraper Page - TikTik Smart Order System
עמוד הורדת מפות אצטדיון
"""

import streamlit as st
from concerts_service import fetch_venue_map_from_ticketmaster, is_ticketmaster_url
from services.concert_service import save_concert_to_favorites
'''
write_file(f"{base_dir}/pages/admin/maps.py", maps_content, maps_header)

print("\n✓ All page files extracted!")
