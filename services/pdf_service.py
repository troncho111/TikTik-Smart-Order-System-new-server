"""
PDF Service - TikTik Smart Order System
שירות יצירת PDFים
"""

import os
import sys
import io
import base64
import tempfile
import subprocess
from PIL import Image
from jinja2 import Environment, FileSystemLoader


# Project root directory
_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def generate_pdf(order_data, stadium_image=None, hotel_image=None, hotel_image_2=None, stadium_photo=None, template_version=1):
    """Generate professional PDF using subprocess to avoid blocking Streamlit"""
    import subprocess
    import json
    
    stadium_image_path = None
    hotel_image_path = None
    hotel_image_2_path = None
    stadium_photo_path = None
    
    def save_image_safely(img, prefix="img"):
        """Safely save an image to temp file, handling various formats"""
        try:
            if img is None:
                return None
            
            # If it's bytes, try to load as PIL Image first
            if isinstance(img, bytes):
                try:
                    img = Image.open(io.BytesIO(img))
                except Exception:
                    return None
            
            # Convert to RGB if needed (for PNG with transparency, RGBA, etc.)
            if not isinstance(img, Image.Image):
                return None
            
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode != 'RGB':
                img = img.convert('RGB')
            
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False, prefix=prefix) as tmp:
                img.save(tmp.name, 'PNG', optimize=True)
                return tmp.name
        except Exception as e:
            print(f"Error saving image: {e}")
            return None
    
    if stadium_image:
        stadium_image_path = save_image_safely(stadium_image, "stadium_")
    
    if stadium_photo:
        stadium_photo_path = save_image_safely(stadium_photo, "atmosphere_")
    
    if hotel_image:
        hotel_image_path = save_image_safely(hotel_image, "hotel_")
    
    if hotel_image_2:
        hotel_image_2_path = save_image_safely(hotel_image_2, "hotel2_")
    
    # Build serializable saved_games with stadium_map_path for each; track temp files for cleanup
    saved_games_temp_paths = []
    saved_games_serializable = []
    for sg in order_data.get('saved_games', []):
        copy = {k: v for k, v in sg.items() if k not in ('saved_stadium_map_bytes', 'pasted_stadium_map')}
        map_path = None
        if sg.get('worldcup_stadium_map') and os.path.exists(sg.get('worldcup_stadium_map', '')):
            map_path = sg['worldcup_stadium_map']
        elif sg.get('league_stadium_map_path') and os.path.exists(sg.get('league_stadium_map_path', '')):
            map_path = sg['league_stadium_map_path']
        elif sg.get('saved_stadium_map_bytes'):
            map_path = save_image_safely(sg['saved_stadium_map_bytes'], "saved_map_")
            if map_path:
                saved_games_temp_paths.append(map_path)
        elif sg.get('pasted_stadium_map'):
            map_path = save_image_safely(sg['pasted_stadium_map'], "saved_map_")
            if map_path:
                saved_games_temp_paths.append(map_path)
        if map_path:
            copy['stadium_map_path'] = map_path
        saved_games_serializable.append(copy)
    
    # If no main stadium image but we have saved_games with a map, use first event's map for main page
    if not stadium_image_path and saved_games_serializable:
        first_path = saved_games_serializable[0].get('stadium_map_path')
        if first_path and os.path.exists(first_path):
            stadium_image_path = first_path
    
    # Safe get for PDF payload (avoid KeyError if a field is missing)
    event_date_val = order_data.get('event_date')
    if hasattr(event_date_val, 'strftime'):
        event_date_val = event_date_val.strftime('%d/%m/%Y %H:%M') if event_date_val else ''
    elif not isinstance(event_date_val, str):
        event_date_val = str(event_date_val or '')

    pdf_data = {
        'product_type': order_data.get('product_type', 'tickets'),
        'event_name': order_data.get('event_name', ''),
        'event_date': event_date_val,
        'venue': order_data.get('venue', ''),
        'venue_name': order_data.get('venue_name', order_data.get('venue', '')),
        'event_city': order_data.get('event_city', ''),
        'event_type': order_data.get('event_type', ''),
        'category': order_data.get('category', ''),
        'ticket_description': order_data.get('ticket_description', ''),
        'passengers': order_data.get('passengers', []),
        'price_per_ticket': order_data.get('price_per_ticket', 0),
        'price_nis': order_data.get('price_nis', 0),
        'total_euro': order_data.get('total_euro', 0),
        'total_foreign': order_data.get('total_foreign') or order_data.get('total_euro', 0),
        'total_nis': order_data.get('total_nis', 0),
        'currency_symbol': order_data.get('currency_symbol', '€'),
        'num_tickets': order_data.get('num_tickets', 1),
        'exchange_rate': order_data.get('exchange_rate', 4.0),
        'order_number': order_data.get('order_number', ''),
        'customer_name': (order_data.get('customer_name') or '').strip() or 'לקוח',
        'creation_date': order_data.get('creation_date') or order_data.get('created_at', ''),
        'customer_id': order_data.get('customer_id', ''),
        'customer_phone': order_data.get('customer_phone', ''),
        'customer_email': order_data.get('customer_email', ''),
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
        'template_version': template_version,
        'stadium_image_path': stadium_image_path,
        'stadium_photo_path': stadium_photo_path,
        'hotel_image_path': order_data.get('hotel_image_path') or hotel_image_path,
        'hotel_image_2_path': order_data.get('hotel_image_path_2') or hotel_image_2_path,
        'saved_games': saved_games_serializable,
    }
    
    json_file = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as jf:
            json.dump(pdf_data, jf, ensure_ascii=False)
            json_file = jf.name

        pdf_generator_path = os.path.join(_APP_DIR, 'pdf_generator.py')
        result = subprocess.run(
            [sys.executable, pdf_generator_path, json_file],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=_APP_DIR
        )

        if result.returncode != 0:
            err_msg = result.stderr or result.stdout or "Unknown error"
            raise Exception(f"PDF generation failed: {err_msg}")

        raw_stdout = result.stdout.strip()
        if not raw_stdout:
            raise Exception("PDF generator returned empty output")
        try:
            pdf_bytes = base64.b64decode(raw_stdout)
        except Exception as e:
            raise Exception(f"Invalid PDF output (decode error): {e}")
        if not pdf_bytes.startswith(b'%PDF-'):
            raise Exception("PDF generator did not produce a valid PDF file")
        return pdf_bytes
        
    finally:
        if json_file and os.path.exists(json_file):
            try:
                os.unlink(json_file)
            except Exception:
                pass
        if stadium_image_path and os.path.exists(stadium_image_path):
            try:
                os.unlink(stadium_image_path)
            except Exception:
                pass
        if stadium_photo_path and os.path.exists(stadium_photo_path):
            try:
                os.unlink(stadium_photo_path)
            except Exception:
                pass
        if hotel_image_path and os.path.exists(hotel_image_path):
            try:
                os.unlink(hotel_image_path)
            except Exception:
                pass
        if hotel_image_2_path and os.path.exists(hotel_image_2_path):
            try:
                os.unlink(hotel_image_2_path)
            except Exception:
                pass
        for p in saved_games_temp_paths:
            if p and os.path.exists(p):
                try:
                    os.unlink(p)
                except Exception:
                    pass


def _image_to_data_uri(img):
    """Convert a PIL Image to a base64 data URI string."""
    if img is None:
        return ''
    try:
        if isinstance(img, bytes):
            try:
                img = Image.open(io.BytesIO(img))
            except Exception:
                return ''
        if not isinstance(img, Image.Image):
            return ''
        # Convert RGBA/P to RGB
        if img.mode in ('RGBA', 'LA', 'P'):
            bg = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            bg.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = bg
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        buf = io.BytesIO()
        img.save(buf, format='PNG', optimize=True)
        encoded = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f'data:image/png;base64,{encoded}'
    except Exception:
        return ''


def _file_to_data_uri(file_path):
    """Convert a file path to a base64 data URI string."""
    if not file_path or not os.path.exists(file_path):
        return ''
    try:
        with open(file_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
        ext = os.path.splitext(file_path)[1].lower()
        mime = 'image/png' if ext == '.png' else 'image/jpeg'
        return f'data:{mime};base64,{data}'
    except Exception:
        return ''


def generate_html(order_data, stadium_image=None, hotel_image=None, hotel_image_2=None, stadium_photo=None):
    """Generate a standalone HTML order document (rendered in-process, no subprocess)."""

    # Convert PIL images to data URIs
    stadium_uri = _image_to_data_uri(stadium_image) if stadium_image else ''
    stadium_photo_uri = _image_to_data_uri(stadium_photo) if stadium_photo else ''
    hotel_uri = _image_to_data_uri(hotel_image) if hotel_image else ''
    hotel_2_uri = _image_to_data_uri(hotel_image_2) if hotel_image_2 else ''

    # Handle file-path based hotel images
    if not hotel_uri and order_data.get('hotel_image_path'):
        hotel_uri = _file_to_data_uri(order_data['hotel_image_path'])
    if not hotel_2_uri and order_data.get('hotel_image_path_2'):
        hotel_2_uri = _file_to_data_uri(order_data['hotel_image_path_2'])

    # Process saved_games stadium maps
    saved_games = []
    main_event_name = (order_data.get('event_name') or '').strip()
    for sg in order_data.get('saved_games', []):
        copy = {k: v for k, v in sg.items() if k not in ('saved_stadium_map_bytes', 'pasted_stadium_map')}
        game_name = (copy.get('event_name') or copy.get('display_text') or '').strip()
        if game_name and game_name == main_event_name:
            continue  # deduplicate
        # Resolve stadium map
        map_uri = ''
        if sg.get('worldcup_stadium_map') and os.path.exists(sg.get('worldcup_stadium_map', '')):
            map_uri = _file_to_data_uri(sg['worldcup_stadium_map'])
        elif sg.get('league_stadium_map_path') and os.path.exists(sg.get('league_stadium_map_path', '')):
            map_uri = _file_to_data_uri(sg['league_stadium_map_path'])
        elif sg.get('saved_stadium_map_bytes'):
            map_uri = _image_to_data_uri(sg['saved_stadium_map_bytes'])
        elif sg.get('pasted_stadium_map'):
            map_uri = _image_to_data_uri(sg['pasted_stadium_map'])
        if map_uri:
            copy['seatmap_image'] = map_uri
        saved_games.append(copy)

    # Use first saved game map for main if no main stadium image
    if not stadium_uri and saved_games:
        stadium_uri = saved_games[0].get('seatmap_image', '')

    # Logo
    logo_path = os.path.join(_APP_DIR, 'assets', 'logo_tiktik_pdf.png')
    if not os.path.exists(logo_path):
        logo_path = os.path.join(_APP_DIR, 'assets', 'logo_tiktik.png')
    logo_uri = _file_to_data_uri(logo_path)

    # Normalize fields
    event_date_val = order_data.get('event_date')
    if hasattr(event_date_val, 'strftime'):
        event_date_val = event_date_val.strftime('%d/%m/%Y %H:%M') if event_date_val else ''
    elif not isinstance(event_date_val, str):
        event_date_val = str(event_date_val or '')

    bag_checked_raw = order_data.get('bag_checked', '')
    has_bag_checked = bool(bag_checked_raw)
    bag_checked_text = str(bag_checked_raw) if bag_checked_raw and bag_checked_raw is not True else ''

    total_nis = order_data.get('total_nis', 0)
    total_euro = order_data.get('total_euro', 0)
    exchange_rate = order_data.get('exchange_rate', 1.0)

    # Load terms
    terms_text = ""
    try:
        terms_path = os.path.join(_APP_DIR, 'terms.txt')
        if os.path.exists(terms_path):
            with open(terms_path, 'r', encoding='utf-8') as f:
                terms_text = f.read()
    except Exception:
        pass

    context = {
        'product_type': order_data.get('product_type', 'tickets'),
        'event_name': order_data.get('event_name', ''),
        'event_date': event_date_val,
        'venue': order_data.get('venue', ''),
        'event_city': order_data.get('event_city', ''),
        'category': order_data.get('category', ''),
        'num_tickets': order_data.get('num_tickets', 1),
        'passengers': order_data.get('passengers', []),
        'total_nis': float(str(total_nis).replace(',', '') or 0),
        'total_euro': float(str(total_euro).replace(',', '') or 0),
        'exchange_rate': float(exchange_rate or 1.0),
        'order_number': order_data.get('order_number', ''),
        'customer_name': (order_data.get('customer_name') or '').strip() or 'לקוח',
        'hotel_name': order_data.get('hotel_name', ''),
        'hotel_nights': order_data.get('hotel_nights', 0),
        'hotel_stars': order_data.get('hotel_stars', ''),
        'hotel_meals': order_data.get('hotel_meals', ''),
        'hotel_address': order_data.get('hotel_address', ''),
        'flights': order_data.get('flights', []),
        'transfers': order_data.get('transfers', False),
        'bag_trolley': order_data.get('bag_trolley', False),
        'bag_checked': has_bag_checked,
        'bag_checked_text': bag_checked_text,
        'is_date_final': order_data.get('is_date_final', False),
        'saved_games': saved_games,
        'created_at': order_data.get('created_at') or order_data.get('creation_date', ''),
        'terms_text': terms_text,
        'logo_path': logo_uri,
        'stadium_image_path': stadium_uri,
        'stadium_photo_path': stadium_photo_uri,
        'hotel_image_path': hotel_uri,
        'hotel_image_path_2': hotel_2_uri,
    }

    # Render template
    templates_dir = os.path.join(_APP_DIR, 'templates')
    env = Environment(loader=FileSystemLoader(templates_dir))
    template = env.get_template('order_html_export.html')
    html_string = template.render(**context)
    return html_string.encode('utf-8')
