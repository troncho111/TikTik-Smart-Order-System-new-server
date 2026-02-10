import sys
import os
import json
from datetime import datetime

# Adjust path to find modules in current directory 
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from pdf_generator import generate_pdf
except ImportError as e:
    print(f'Import Error: {e}')
    try:
        import pdf_generator
        generate_pdf = pdf_generator.generate_pdf
    except Exception as e2:
        print(f'Failed to import pdf_generator: {e2}')
        sys.exit(1)

# Sample data with CORRECT TYPES and REAL IMAGES
order_data = {
    'order_number': 'ORD-123456',
    'customer_name': 'ישראל ישראלי',
    'customer_phone': '050-1234567',
    'customer_email': 'israel@example.com',
    'created_at': '07/02/2026',
    'status': 'confirmed',
    'total_nis': 12500,  # INTEGER
    'total_euro': 3000,  # INTEGER
    'exchange_rate': 4.0,
    'product_type': 'package',
    'event_name': 'ריאל מדריד נגד ברצלונה',
    'event_date': '14/03/2026 21:00',
    'venue': 'סנטיאגו ברנבאו',
    'event_city': 'מדריד',
    'category': 'VIP Category 1',
    'num_tickets': 2,
    
    # Game data
    'games': [{
        'event_name': 'ריאל מדריד נגד ברצלונה',
        'event_date': '14/03/2026 21:00',
        'venue': 'סנטיאגו ברנבאו',
        'city': 'מדריד',
        'category': 'VIP Category 1',
        'num_tickets': 2,
        'stadium_map_path': '/root/TikTik-Smart-Order-System-new-server/stadium_maps/real_madrid.jpg'
    }],
    
    # Flights
    'flights': [
        {
            'direction': 'outbound',
            'from': 'TLV',
            'to': 'MAD',
            'date': '14/03/2026',
            'departure_time': '06:00',
            'airline': 'El Al'
        },
        {
            'direction': 'return',
            'from': 'MAD',
            'to': 'TLV',
            'date': '17/03/2026',
            'departure_time': '23:00',
            'airline': 'El Al'
        }
    ],
    
    # Hotel
    'hotel_name': 'Hilton Madrid',
    'hotel_address': 'Castellana Av. 1',
    'hotel_nights': 3,
    'hotel_meals': 'ארוחת בוקר',
    'hotel_rating': '5 stars',
    'hotel_image_path': '/root/TikTik-Smart-Order-System-new-server/assets/cover_page.jpg',
    
    # Passengers
    'passengers': [
        {'name': 'Israel Israeli', 'first_name': 'Israel', 'last_name': 'Israeli', 'passport': '12345678', 'birth_date': '01/01/1980'},
        {'name': 'Sara Israeli', 'first_name': 'Sara', 'last_name': 'Israeli', 'passport': '87654321', 'birth_date': '01/01/1985'}
    ]
}

print('🧪 Generating Sample PDF...')
try:
    output_path = 'sample_order_template_v3.pdf'
    
    pdf_bytes = generate_pdf(order_data)
    
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
        
    print(f'✅ PDF created successfully: {output_path}')
    print(f'📊 Size: {len(pdf_bytes)} bytes')
    
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()
