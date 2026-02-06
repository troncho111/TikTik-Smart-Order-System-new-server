#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
סקריפט לבדיקת מערכת PDF החדשה
"""

import sys
sys.path.insert(0, '/home/ubuntu/tiktik-review')

from services_new.pdf_service import generate_order_pdf

# נתוני דוגמה מציאותיים
order_data = {
    # פרטי הזמנה בסיסיים
    'order_id': 'TT-2026-001',
    'customer_name': 'ישראל ישראלי',
    'created_at': '06/02/2026',
    
    # עמוד שער
    'cover_line1': 'ישראל ישראלי',
    'cover_line2': 'חבילה מלאה - ריאל מדריד נגד ברצלונה',
    'cover_line3': 'מדריד, ספרד | 15-17 במרץ 2026',
    
    # פרטי אירוע
    'event_name': 'ריאל מדריד נגד ברצלונה',
    'event_date': '15/03/2026 בשעה 21:00',
    'event_city': 'מדריד',
    'venue': 'מדריד, ספרד',
    'venue_name': 'סנטיאגו ברנבאו',
    'category': 'VIP - קטגוריה 1',
    'num_tickets': 2,
    
    # קבוצות (לכדורגל)
    'home_team_name': 'ריאל מדריד',
    'away_team_name': 'ברצלונה',
    
    # פרטי מלון
    'hotel_name': 'Hilton Madrid Castellana',
    'hotel_nights': 2,
    'hotel_stars': 5,
    'hotel_meals': 'ארוחת בוקר',
    'hotel_address': 'Paseo de la Castellana 57, 28046 Madrid',
    'hotel_website': 'www.hilton.com',
    'hotel_rating': '4.5/5',
    'transfers': True,
    
    # טיסות
    'flights': [
        {
            'direction': 'outbound',
            'from': 'תל אביב (TLV)',
            'to': 'מדריד (MAD)',
            'date': '14/03/2026',
            'departure_time': '06:30',
            'arrival_time': '11:45',
            'airline': 'אל על',
        },
        {
            'direction': 'return',
            'from': 'מדריד (MAD)',
            'to': 'תל אביב (TLV)',
            'date': '17/03/2026',
            'departure_time': '13:15',
            'arrival_time': '18:30',
            'airline': 'אל על',
        },
    ],
    
    # נוסעים
    'passengers': [
        {
            'name': 'ישראל ישראלי',
            'name_en': 'Israel Israeli',
            'passport': '12345678',
            'birth_date': '01/01/1980',
            'ticket_type': 'מבוגר',
        },
        {
            'name': 'שרה ישראלי',
            'name_en': 'Sara Israeli',
            'passport': '87654321',
            'birth_date': '15/05/1985',
            'ticket_type': 'מבוגר',
        },
    ],
    
    # מזוודות
    'bag_trolley': True,
    'bag_checked': '23 ק"ג',
    
    # מחירים
    'final_price': '12,500',
    'total_nis': '12,500',
    'total_euro': '3,000',
    'price_per_ticket': '1,500',
    
    # סוג מוצר
    'product_type': 'package',
    
    # מותג
    'brand_abbr': 'TT',
    'brand_website': 'www.tiktik-online.co.il',
    'brand_email': 'info@tiktik.co.il',
    
    # תקנון
    'legal_text': '''
<h3>תנאים כלליים</h3>
<p>1. ההזמנה תקפה רק לאחר אישור בכתב מחברת TikTik.</p>
<p>2. התשלום יבוצע בהתאם לתנאי התשלום שנקבעו בהזמנה.</p>
<p>3. ביטול הזמנה יהיה כפוף לדמי ביטול בהתאם למדיניות החברה.</p>

<h3>תנאי ביטול</h3>
<p>• עד 60 יום לפני האירוע - דמי ביטול 25%</p>
<p>• 30-60 יום לפני האירוע - דמי ביטול 50%</p>
<p>• 14-30 יום לפני האירוע - דמי ביטול 75%</p>
<p>• פחות מ-14 יום לפני האירוע - דמי ביטול 100%</p>

<h3>ביטוח נסיעות</h3>
<p>מומלץ בחום לרכוש ביטוח נסיעות מקיף המכסה ביטול, עיכובים, אובדן מטען ורפואה.</p>

<h3>אחריות</h3>
<p>החברה אינה אחראית לשינויים במועדי אירועים, ביטולים או כל נזק עקיף.</p>
    ''',
}

# תמונות (ריקות - רק לדוגמה)
images = {
    'logo_path': None,  # אין לוגו
    'stadium_image': None,
    'stadium_photo': None,
    'hotel_image': None,
    'hotel_image_2': None,
    'home_team_badge': None,
    'away_team_badge': None,
}

print("🧪 יוצר PDF לדוגמה...")
print("📝 נתונים: הזמנה מלאה עם אירוע, מלון, טיסות, ו-2 נוסעים")

try:
    # יצירת PDF
    pdf_bytes = generate_order_pdf(
        order_data,
        images,
        output_path='/home/ubuntu/sample_order.pdf'
    )
    
    print("✅ PDF נוצר בהצלחה!")
    print("📄 נתיב: /home/ubuntu/sample_order.pdf")
    print(f"📊 גודל: {len(pdf_bytes):,} bytes")
    
except Exception as e:
    print(f"❌ שגיאה: {e}")
    import traceback
    traceback.print_exc()
