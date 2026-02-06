"""
TikTik PDF Service - מערכת יצירת PDF מקצועית

מטרה:
------
קובץ זה אחראי על יצירת PDF מטופס ההזמנה.
הוא מפריד לחלוטין בין לוגיקה לעיצוב.

מבנה:
-----
1. פונקציות עזר (המרת תמונות, חישובי גובה)
2. הכנת נתונים לתבנית
3. יצירת PDF

שימוש:
------
from services_new.pdf_service import generate_order_pdf

pdf_bytes = generate_order_pdf(order_data, images_dict)
"""

import os
import base64
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML


# ============================================================================
# פונקציות עזר
# ============================================================================

def get_image_data_uri(image_path: str) -> str:
    """
    המרת תמונה ל-Data URI (base64)
    
    Args:
        image_path: נתיב לקובץ תמונה
        
    Returns:
        str: Data URI או מחרוזת ריקה אם הקובץ לא קיים
        
    דוגמה:
        >>> get_image_data_uri('/path/to/logo.png')
        'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...'
    """
    if not image_path or not os.path.exists(image_path):
        return ""
    
    # זיהוי סוג התמונה
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
        '.webp': 'image/webp',
    }
    mime_type = mime_types.get(ext, 'image/jpeg')
    
    # קריאה והמרה ל-base64
    try:
        with open(image_path, 'rb') as f:
            data = base64.b64encode(f.read()).decode('utf-8')
        return f"data:{mime_type};base64,{data}"
    except Exception as e:
        print(f"שגיאה בהמרת תמונה {image_path}: {e}")
        return ""


def calculate_seatmap_height(order_data: dict, has_stadium_photo: bool) -> tuple:
    """
    חישוב גובה אופטימלי למפת מקומות ותמונת אצטדיון
    
    Args:
        order_data: נתוני ההזמנה
        has_stadium_photo: האם יש תמונת אצטדיון
        
    Returns:
        tuple: (גובה_מפה, גובה_תמונה) בפיקסלים
        
    הסבר:
        הפונקציה מחשבת כמה מקום פנוי יש בעמוד ומחלקת אותו
        בין מפת המקומות לתמונת האצטדיון בצורה אופטימלית.
    """
    # קבועים
    PAGE_HEIGHT = 1020  # גובה תוכן העמוד
    HEADER_HEIGHT = 210  # כותרת + מטא
    FOOTER_HEIGHT = 190  # מחיר + חתימות
    GAP = 10  # מרווח בין תמונות
    
    # גבהים מועדפים
    PHOTO_PREFERRED = 320
    PHOTO_MIN = 220
    SEATMAP_MIN = 420
    
    # חישוב גובה תפוס
    used_height = HEADER_HEIGHT + FOOTER_HEIGHT
    
    # הוספת גובה מלון (אם יש)
    if order_data.get('hotel_name'):
        used_height += 260
    
    # הוספת גובה טיסות (אם יש)
    flights = order_data.get('flights', [])
    if flights:
        used_height += 90 + (18 * len(flights))
    
    # הוספת גובה נוסעים (אם יש)
    passengers = order_data.get('passengers', [])
    if passengers:
        used_height += 80 + (22 * len(passengers))
    
    # חישוב מקום פנוי
    available = PAGE_HEIGHT - used_height
    
    # אם אין תמונת אצטדיון - כל המקום למפה
    if not has_stadium_photo:
        return (available - 20, 0)
    
    # יש תמונת אצטדיון - חלוקה חכמה
    photo_h = min(PHOTO_PREFERRED, available - SEATMAP_MIN - GAP)
    photo_h = max(PHOTO_MIN, photo_h)
    
    seatmap_h = available - photo_h - GAP
    
    # וידוא שהמפה לא קטנה מדי
    if seatmap_h < SEATMAP_MIN:
        seatmap_h = SEATMAP_MIN
        photo_h = max(PHOTO_MIN, available - seatmap_h - GAP)
    
    return (int(seatmap_h), int(photo_h))


# ============================================================================
# הכנת נתונים לתבנית
# ============================================================================

def prepare_template_data(order_data: dict, images: dict) -> dict:
    """
    הכנת נתונים לתבנית HTML
    
    Args:
        order_data: נתוני ההזמנה מבסיס הנתונים
        images: מילון עם נתיבי תמונות
        
    Returns:
        dict: נתונים מוכנים לתבנית
        
    הסבר:
        הפונקציה לוקחת את הנתונים הגולמיים ומכינה אותם
        לשימוש בתבנית - ממירה תמונות, מחשבת גבהים, וכו'.
    """
    # העתקת הנתונים (כדי לא לשנות את המקור)
    data = order_data.copy()
    
    # המרת תמונות ל-Data URI
    if images.get('logo_path'):
        data['logo_path'] = get_image_data_uri(images['logo_path'])
    
    if images.get('stadium_image'):
        data['seatmap_image'] = get_image_data_uri(images['stadium_image'])
    
    if images.get('stadium_photo'):
        data['stadium_photo_path'] = get_image_data_uri(images['stadium_photo'])
    
    if images.get('hotel_image'):
        data['hotel_image_path'] = get_image_data_uri(images['hotel_image'])
    
    if images.get('hotel_image_2'):
        data['hotel_image_2'] = get_image_data_uri(images['hotel_image_2'])
    
    if images.get('home_team_badge'):
        data['home_team_badge'] = get_image_data_uri(images['home_team_badge'])
    
    if images.get('away_team_badge'):
        data['away_team_badge'] = get_image_data_uri(images['away_team_badge'])
    
    if images.get('cover_image'):
        data['cover_image'] = get_image_data_uri(images['cover_image'])
    
    # חישוב גבהים למפת מקומות ותמונת אצטדיון
    has_stadium_photo = bool(images.get('stadium_photo'))
    seatmap_h, photo_h = calculate_seatmap_height(order_data, has_stadium_photo)
    
    data['seatmap_height_px'] = seatmap_h
    data['stadium_photo_height_px'] = photo_h
    
    # טיפול בנוסעים (אם זה JSON string)
    if isinstance(data.get('passengers'), str):
        try:
            import json
            data['passengers'] = json.loads(data['passengers'])
        except:
            data['passengers'] = []
    
    # טיפול בטיסות (אם זה JSON string)
    if isinstance(data.get('flights'), str):
        try:
            import json
            data['flights'] = json.loads(data['flights'])
        except:
            data['flights'] = []
    
    return data


# ============================================================================
# יצירת PDF
# ============================================================================

def generate_order_pdf(
    order_data: dict,
    images: dict = None,
    template_path: str = None,
    output_path: str = None
) -> bytes:
    """
    יצירת PDF מטופס הזמנה
    
    Args:
        order_data: נתוני ההזמנה (dict)
        images: מילון עם נתיבי תמונות (אופציונלי)
        template_path: נתיב לתבנית HTML (אופציונלי, ברירת מחדל: templates_new/order_template.html)
        output_path: נתיב לשמירת PDF (אופציונלי, אם לא מצוין - מחזיר bytes)
        
    Returns:
        bytes: תוכן ה-PDF
        
    דוגמה:
        >>> order_data = {
        ...     'order_id': '12345',
        ...     'customer_name': 'ישראל ישראלי',
        ...     'event_name': 'ריאל מדריד נגד ברצלונה',
        ...     # ... עוד שדות
        ... }
        >>> images = {
        ...     'logo_path': '/path/to/logo.png',
        ...     'stadium_image': '/path/to/stadium.jpg',
        ... }
        >>> pdf_bytes = generate_order_pdf(order_data, images)
        >>> with open('order.pdf', 'wb') as f:
        ...     f.write(pdf_bytes)
    """
    # ברירות מחדל
    if images is None:
        images = {}
    
    if template_path is None:
        # נתיב ברירת מחדל
        current_dir = Path(__file__).parent.parent
        template_path = current_dir / 'templates_new' / 'order_template.html'
    
    # הכנת הנתונים
    template_data = prepare_template_data(order_data, images)
    
    # טעינת התבנית
    template_dir = Path(template_path).parent
    template_name = Path(template_path).name
    
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template(template_name)
    
    # רינדור HTML
    html_content = template.render(**template_data)
    
    # יצירת PDF
    pdf_bytes = HTML(string=html_content, base_url=str(template_dir)).write_pdf()
    
    # שמירה לקובץ (אם נדרש)
    if output_path:
        with open(output_path, 'wb') as f:
            f.write(pdf_bytes)
        print(f"✅ PDF נשמר ב: {output_path}")
    
    return pdf_bytes


# ============================================================================
# פונקציה לתאימות לאחור (Backward Compatibility)
# ============================================================================

def generate_pdf(
    order_data: dict,
    stadium_image_path: str = None,
    hotel_image_path: str = None,
    hotel_image_2_path: str = None,
    stadium_photo_path: str = None,
    template_version: int = 1
) -> bytes:
    """
    פונקציה ישנה לתאימות לאחור
    
    ⚠️ מומלץ להשתמש ב-generate_order_pdf במקום!
    
    הפונקציה הזו קיימת רק כדי שהקוד הישן ימשיך לעבוד.
    """
    # המרה לפורמט החדש
    images = {}
    
    if stadium_image_path:
        images['stadium_image'] = stadium_image_path
    
    if hotel_image_path:
        images['hotel_image'] = hotel_image_path
    
    if hotel_image_2_path:
        images['hotel_image_2'] = hotel_image_2_path
    
    if stadium_photo_path:
        images['stadium_photo'] = stadium_photo_path
    
    # קריאה לפונקציה החדשה
    return generate_order_pdf(order_data, images)


# ============================================================================
# בדיקה (אם מריצים את הקובץ ישירות)
# ============================================================================

if __name__ == "__main__":
    print("🧪 בדיקת מערכת PDF...")
    
    # נתוני דוגמה
    test_order = {
        'order_id': 'TEST-12345',
        'customer_name': 'ישראל ישראלי',
        'created_at': '06/02/2026',
        'cover_line1': 'ישראל ישראלי',
        'cover_line2': 'חבילה מלאה - ריאל מדריד נגד ברצלונה',
        'cover_line3': 'מדריד, ספרד | 15-17 במרץ 2026',
        'event_name': 'ריאל מדריד נגד ברצלונה',
        'event_date': '15/03/2026',
        'event_city': 'מדריד',
        'venue_name': 'סנטיאגו ברנבאו',
        'category': 'VIP',
        'num_tickets': 2,
        'hotel_name': 'Hilton Madrid',
        'hotel_nights': 2,
        'hotel_stars': 5,
        'hotel_meals': 'ארוחת בוקר',
        'transfers': True,
        'final_price': '12,500',
        'total_euro': '3,000',
        'price_per_ticket': '1,500',
        'product_type': 'package',
    }
    
    print("✅ נתוני דוגמה הוכנו")
    print("📝 לייצר PDF אמיתי, הוסף נתיבי תמונות ל-images")
    print("💡 דוגמה:")
    print("""
    images = {
        'logo_path': '/path/to/logo.png',
        'stadium_image': '/path/to/stadium.jpg',
    }
    pdf = generate_order_pdf(test_order, images, output_path='test.pdf')
    """)
