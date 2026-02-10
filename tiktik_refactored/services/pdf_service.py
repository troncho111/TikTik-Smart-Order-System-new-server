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
        'total_nis': order_data.get('total_nis', 0),
        'num_tickets': order_data.get('num_tickets', 1),
        'exchange_rate': order_data.get('exchange_rate', 4.0),
        'order_number': order_data.get('order_number', ''),
        'customer_name': order_data.get('customer_name', ''),
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
