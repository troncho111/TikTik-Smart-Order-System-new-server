import os
import sys
import json
import base64
from datetime import datetime
from pathlib import Path
from weasyprint import HTML, CSS
from jinja2 import Environment, FileSystemLoader

def get_image_data_uri(image_path):
    if not image_path:
        return ''
    try:
        if image_path.startswith('http'):
            return image_path
        if os.path.exists(image_path):
            with open(image_path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                ext = os.path.splitext(image_path)[1].lower()
                mime_type = 'image/jpeg'
                if ext == '.png': mime_type = 'image/png'
                elif ext == '.svg': mime_type = 'image/svg+xml'
                elif ext == '.jpg' or ext == '.jpeg': mime_type = 'image/jpeg'
                return f'data:{mime_type};base64,{encoded_string}'
    except Exception:
        pass
    return ''

def generate_pdf(order_data, stadium_image_path=None, hotel_image_path=None, hotel_image_2_path=None, stadium_photo_path=None, template_version=1):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    templates_dir = os.path.join(base_dir, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    
    template_name = 'order_template.html'
    template = env.get_template(template_name)
    
    # Ensure numeric types
    total_nis = order_data.get('total_nis', 0)
    total_euro = order_data.get('total_euro', 0)
    exchange_rate = order_data.get('exchange_rate', 1.0)

    # Load terms
    terms_text = ""
    try:
        terms_path = os.path.join(base_dir, 'terms.txt')
        if os.path.exists(terms_path):
            with open(terms_path, 'r', encoding='utf-8') as f:
                terms_text = f.read()
    except:
        pass

    # Prepare context
    context = order_data.copy()

    # LOGO FIX: Use optimized PDF logo (smaller, RGB) with fallback to original
    base_dir = os.path.dirname(os.path.abspath(__file__))
    logo_file_path = os.path.join(base_dir, 'assets', 'logo_tiktik_pdf.png')
    if not os.path.exists(logo_file_path):
        logo_file_path = os.path.join(base_dir, 'assets', 'logo_tiktik.png')
    logo_data_uri = get_image_data_uri(logo_file_path)

    # Resolve image paths: prefer function params, fall back to order_data values
    _stadium = stadium_image_path or order_data.get('stadium_image_path', '')
    _hotel = hotel_image_path or order_data.get('hotel_image_path', '')
    _hotel_2 = hotel_image_2_path or order_data.get('hotel_image_2_path', '')
    _stadium_photo = stadium_photo_path or order_data.get('stadium_photo_path', '')

    # Convert saved_games stadium maps to data URIs and deduplicate against main event
    saved_games = order_data.get('saved_games', [])
    main_event_name = (order_data.get('event_name') or '').strip()
    deduped_games = []
    for game in saved_games:
        game_name = (game.get('event_name') or game.get('display_text') or '').strip()
        if game_name and game_name == main_event_name:
            continue
        map_path = game.get('stadium_map_path', '')
        if map_path and not map_path.startswith('data:'):
            game['seatmap_image'] = get_image_data_uri(map_path)
        elif map_path and map_path.startswith('data:'):
            game['seatmap_image'] = map_path
        deduped_games.append(game)
    saved_games = deduped_games

    # Normalize bag_checked: True -> show "מזוודה" without "True"; string like "20kg" shows as-is
    bag_checked_raw = order_data.get('bag_checked', '')
    has_bag_checked = bool(bag_checked_raw)
    bag_checked_text = str(bag_checked_raw) if bag_checked_raw and bag_checked_raw is not True else ''

    # Normalize created_at field
    created_at = order_data.get('created_at') or order_data.get('creation_date', '')

    context.update({
        'total_nis': float(str(total_nis).replace(',', '') or 0),
        'total_euro': float(str(total_euro).replace(',', '') or 0),
        'exchange_rate': float(exchange_rate or 1.0),
        'terms_text': terms_text,
        'logo_path': logo_data_uri,
        'stadium_image_path': get_image_data_uri(_stadium) if _stadium else '',
        'hotel_image_path': get_image_data_uri(_hotel) if _hotel else '',
        'hotel_image_path_2': get_image_data_uri(_hotel_2) if _hotel_2 else '',
        'stadium_photo_path': get_image_data_uri(_stadium_photo) if _stadium_photo else '',
        'saved_games': saved_games,
        'created_at': created_at,
        'bag_checked': has_bag_checked,
        'bag_checked_text': bag_checked_text,
    })

    html_content = template.render(**context)
    
    # Ensure PDF generation uses base_url for local assets
    html_doc = HTML(string=html_content, base_url=base_dir)
    return html_doc.write_pdf()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
        pdf_bytes = generate_pdf(data)
        print(base64.b64encode(pdf_bytes).decode('utf-8'))
