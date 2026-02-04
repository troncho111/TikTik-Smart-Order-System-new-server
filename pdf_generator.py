#!/usr/bin/env python3
"""
PDF Generator using WeasyPrint and Jinja2 templates.
Generates professional Hebrew RTL PDF documents for TikTik orders.
"""

import os
import sys
import json
import base64
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def get_image_data_uri(image_path: str) -> str:
    """Convert an image file to a base64 data URI."""
    if not image_path or not os.path.exists(image_path):
        return ""
    
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
    }
    mime_type = mime_types.get(ext, 'image/jpeg')
    
    with open(image_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    
    return f"data:{mime_type};base64,{data}"

def calculate_media_heights(order_data: dict) -> tuple:
    """
    Calculate optimal heights for seatmap and stadium photo based on available space.
    Returns (seatmap_height_px, stadium_photo_height_px)
    Deterministic: seatmap_h + photo_h + GAP = available (no white space)
    """
    PAGE_CONTENT_HEIGHT = 1020
    HEADER_META_HEIGHT = 210
    PRICE_SIGNATURES_HEIGHT = 190
    GAP = 10
    
    PHOTO_TARGET = 320
    PHOTO_MIN = 220
    SEATMAP_MIN = 420
    
    used_height = HEADER_META_HEIGHT + PRICE_SIGNATURES_HEIGHT
    
    product_type = order_data.get('product_type', 'tickets')
    if product_type == 'package':
        if order_data.get('hotel_name'):
            used_height += 260
        flights = order_data.get('flights', [])
        if flights:
            used_height += 90 + 18 * len(flights)
    
    passengers = order_data.get('passengers', [])
    if isinstance(passengers, str):
        try:
            import json
            passengers = json.loads(passengers)
        except:
            passengers = []
    if passengers:
        used_height += 80 + 22 * len(passengers)
    
    available = PAGE_CONTENT_HEIGHT - used_height
    
    has_stadium_photo = bool(order_data.get('stadium_photo_path'))
    
    if not has_stadium_photo:
        seatmap_h = available - 20
        return (seatmap_h, 0)
    
    # 1) Photo gets target height (only if room for large seatmap)
    photo_h = min(PHOTO_TARGET, available - SEATMAP_MIN - GAP)
    photo_h = max(PHOTO_MIN, photo_h)
    
    # 2) Seatmap gets ALL remaining space (no max cap)
    seatmap_h = available - photo_h - GAP
    
    # 3) If seatmap too small, shrink photo instead
    if seatmap_h < SEATMAP_MIN:
        seatmap_h = SEATMAP_MIN
        photo_h = max(PHOTO_MIN, available - seatmap_h - GAP)
    
    # 4) Ensure no overflow (rare edge case)
    if seatmap_h + photo_h + GAP > available:
        photo_h = max(PHOTO_MIN, available - seatmap_h - GAP)
    
    return (seatmap_h, photo_h)


def generate_pdf(order_data: dict, stadium_image_path: str = None, hotel_image_path: str = None, hotel_image_2_path: str = None, stadium_photo_path: str = None, template_version: int = 1) -> bytes:
    """
    Generate a professional PDF using HTML template and WeasyPrint.
    
    Args:
        order_data: Dictionary containing order details
        stadium_image_path: Optional path to stadium/seatmap image
        hotel_image_path: Optional path to hotel image
        hotel_image_2_path: Optional path to second hotel image
        stadium_photo_path: Optional path to atmosphere/background image
        template_version: Template version (1 or 2)
    
    Returns:
        PDF file as bytes
    """
    template_dir = Path(__file__).parent / 'templates'
    project_root = Path(__file__).parent
    
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    
    template_name = 'order_template_2.html' if template_version == 2 else 'order_template.html'
    template = env.get_template(template_name)
    
    order_data_with_photo = order_data.copy()
    if stadium_photo_path:
        order_data_with_photo['stadium_photo_path'] = stadium_photo_path
    seatmap_height_px, stadium_photo_height_px = calculate_media_heights(order_data_with_photo)
    
    cover_image = get_image_data_uri(str(project_root / 'assets' / 'cover_page.jpg'))
    
    header_banner_path = project_root / 'assets' / 'header_banner.png'
    if not header_banner_path.exists():
        header_banner_path = project_root / 'assets' / 'header_banner.jpg'
    header_banner = get_image_data_uri(str(header_banner_path))
    
    hotel_image_2_path_from_data = order_data.get('hotel_image_2_path')
    hotel_image_2_uri = get_image_data_uri(hotel_image_2_path or hotel_image_2_path_from_data) if (hotel_image_2_path or hotel_image_2_path_from_data) else None
    
    passengers = order_data.get('passengers', [])
    if isinstance(passengers, str):
        try:
            passengers = json.loads(passengers)
        except:
            passengers = []
    
    # Ensure passengers is a list and filter out empty entries
    if not isinstance(passengers, list):
        passengers = []
    passengers = [p for p in passengers if p]
    
    # Normalize passenger dicts for templates: form uses first_name/last_name, templates use name/full_name
    for p in passengers:
        if not isinstance(p, dict):
            continue
        full_name = (
            (p.get('first_name') or '').strip() + ' ' + (p.get('last_name') or '').strip()
        ).strip()
        if full_name and not p.get('name'):
            p['name'] = full_name
            p['full_name'] = full_name
            p['name_en'] = full_name
        if p.get('birth_date') and not p.get('dob'):
            p['dob'] = p.get('birth_date')
        if p.get('passport') and not p.get('passport_number'):
            p['passport_number'] = p.get('passport')
    
    total_nis = order_data.get('total_nis', 0)
    if isinstance(total_nis, (int, float)):
        total_nis_formatted = f"{total_nis:,.0f}"
    else:
        total_nis_formatted = str(total_nis)
    
    stadium_image_uri = get_image_data_uri(stadium_image_path) if stadium_image_path else None
    hotel_image_uri = get_image_data_uri(hotel_image_path) if hotel_image_path else None
    hotel_image_2_uri_param = get_image_data_uri(hotel_image_2_path) if hotel_image_2_path else None
    
    stadium_photo_uri = get_image_data_uri(stadium_photo_path) if stadium_photo_path else None
    
    terms_text = ""
    terms_text_page1 = ""
    terms_text_page2 = ""
    terms_path = project_root / 'terms.txt'
    if terms_path.exists():
        with open(terms_path, 'r', encoding='utf-8') as f:
            terms_lines = f.readlines()
            mid_point = len(terms_lines) // 2
            terms_text_page1 = ''.join(terms_lines[:mid_point]).replace('\n', '<br>')
            terms_text_page2 = ''.join(terms_lines[mid_point:]).replace('\n', '<br>')
            terms_text = (terms_text_page1 + terms_text_page2)
    
    from datetime import datetime
    created_at = order_data.get('created_at') or datetime.now().strftime('%d/%m/%Y')
    
    logo_path = get_image_data_uri(str(project_root / 'assets' / 'logo_red.png'))
    if not logo_path:
        logo_path = get_image_data_uri(str(project_root / 'static' / 'logo_red.png'))
    
    template_data = {
        'product_type': order_data.get('product_type', 'tickets'),
        'event_name': order_data.get('event_name', ''),
        'logo_path': logo_path,
        'event_date': order_data.get('event_date', ''),
        'venue': order_data.get('venue', ''),
        'venue_name': order_data.get('venue', ''),
        'event_city': order_data.get('event_city', order_data.get('venue', '')),
        'event_type': order_data.get('event_type', ''),
        'customer_name': order_data.get('customer_name', ''),
        'customer_id': order_data.get('customer_id', ''),
        'customer_phone': order_data.get('customer_phone', ''),
        'customer_email': order_data.get('customer_email', ''),
        'ticket_description': order_data.get('ticket_description', ''),
        'category': order_data.get('category', ''),
        'price_per_ticket': order_data.get('price_per_ticket', 0),
        'num_tickets': order_data.get('num_tickets', 0),
        'exchange_rate': order_data.get('exchange_rate', 4.0),
        'total_euro': order_data.get('total_euro', 0),
        'total_nis': total_nis_formatted,
        'final_price': total_nis_formatted,
        'order_number': order_data.get('order_number', ''),
        'order_id': order_data.get('order_number', ''),
        'created_at': created_at,
        'passengers': passengers,
        'cover_image': cover_image,
        'header_banner': header_banner,
        'stadium_image': stadium_image_uri,
        'event_image_path': stadium_image_uri,
        'seatmap_image': stadium_image_uri,
        'stadium_photo_path': stadium_photo_uri,
        'seatmap_height_px': seatmap_height_px,
        'stadium_photo_height_px': stadium_photo_height_px,
        'hotel_image': hotel_image_uri,
        'hotel_image_path': hotel_image_uri,
        'hotel_image_2': hotel_image_2_uri,
        'hotel_name': order_data.get('hotel_name', ''),
        'hotel_nights': order_data.get('hotel_nights', 0),
        'hotel_stars': order_data.get('hotel_stars', ''),
        'hotel_meals': order_data.get('hotel_meals', ''),
        'hotel_address': order_data.get('hotel_address', ''),
        'hotel_website': order_data.get('hotel_website', ''),
        'hotel_rating': order_data.get('hotel_rating', ''),
        'flight_details': order_data.get('flight_details', ''),
        'flights': order_data.get('flights', []),
        'transfers': order_data.get('transfers', False),
        'bag_trolley': order_data.get('bag_trolley', False),
        'bag_checked': order_data.get('bag_checked', ''),
        'is_date_final': order_data.get('is_date_final', False),
        'seats_together': order_data.get('seats_together', False),
        'seats_together_image': image_to_data_uri(str(Path(__file__).parent / 'assets' / 'seats_together.png')) if order_data.get('seats_together', False) else '',
        'terms_text': terms_text,
        'legal_text': terms_text,
        'legal_text_page1': terms_text_page1,
        'legal_text_page2': terms_text_page2,
    }
    
    html_content = template.render(**template_data)
    
    base_url = str(Path(__file__).parent)
    
    html_doc = HTML(string=html_content, base_url=base_url)
    pdf_bytes = html_doc.write_pdf()
    
    return pdf_bytes


if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            input_data = f.read()
    else:
        input_data = sys.stdin.read()
    
    order_data = json.loads(input_data)
    template_version = order_data.get('template_version', 1)
    pdf_bytes = generate_pdf(
        order_data, 
        order_data.get('stadium_image_path'),
        order_data.get('hotel_image_path'),
        order_data.get('hotel_image_2_path'),
        order_data.get('stadium_photo_path'),
        template_version
    )
    print(base64.b64encode(pdf_bytes).decode('utf-8'))
