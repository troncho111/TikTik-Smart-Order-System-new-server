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
    # DOCKER FIX: Use absolute paths within the container
    base_dir = "/app"
    templates_dir = os.path.join(base_dir, 'templates')
    
    # Ensure templates directory exists, fallback to local if not
    if not os.path.exists(templates_dir):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        templates_dir = os.path.join(base_dir, 'templates')
        if not os.path.exists(templates_dir):
            # Try one level up (if we are in services_refactored)
            templates_dir = os.path.join(os.path.dirname(base_dir), 'templates')

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
        terms_path = os.path.join(os.path.dirname(templates_dir), 'terms.txt')
        if os.path.exists(terms_path):
            with open(terms_path, 'r', encoding='utf-8') as f:
                terms_text = f.read()
    except:
        pass

    # Prepare context
    context = order_data.copy()
    
    # LOGO FIX: Use absolute path and convert to Data URI
    logo_file_path = os.path.join(os.path.dirname(templates_dir), 'assets', 'logo_tiktik.png')
    logo_data_uri = get_image_data_uri(logo_file_path)

    context.update({
        'total_nis': float(str(total_nis).replace(',', '') or 0),
        'total_euro': float(str(total_euro).replace(',', '') or 0),
        'exchange_rate': float(exchange_rate or 1.0),
        'terms_text': terms_text,
        'logo_path': logo_data_uri,
        'stadium_image_path': get_image_data_uri(stadium_image_path) if stadium_image_path else '',
        'hotel_image_path': get_image_data_uri(hotel_image_path) if hotel_image_path else '',
        'hotel_image_path_2': get_image_data_uri(hotel_image_2_path) if hotel_image_2_path else '',
        'stadium_photo_path': get_image_data_uri(stadium_photo_path) if stadium_photo_path else ''
    })

    html_content = template.render(**context)
    
    # Ensure PDF generation uses base_url for local assets
    html_doc = HTML(string=html_content, base_url=os.path.dirname(templates_dir))
    return html_doc.write_pdf()

if __name__ == '__main__':
    if len(sys.argv) > 1:
        with open(sys.argv[1], 'r', encoding='utf-8') as f:
            data = json.load(f)
        pdf_bytes = generate_pdf(data)
        print(base64.b64encode(pdf_bytes).decode('utf-8'))
