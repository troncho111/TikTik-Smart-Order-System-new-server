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
import json
from pathlib import Path
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

# שורש הפרויקט (לנכסים ותנאים)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent


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
# הכנת נתונים לתבנית (תאימות לתבנית order_template.html)
# ============================================================================

def _build_cover_lines_and_games(order_data: dict, stadium_image_uri: str) -> tuple:
    """בונה cover_line1/2/3 ורשימת games כמו ב-pdf_generator."""
    saved_raw = order_data.get('saved_games', [])
    saved_with_maps = []
    for g in saved_raw:
        game = dict(g)
        map_path = (
            game.get('stadium_map_path') or
            game.get('worldcup_stadium_map') or
            game.get('league_stadium_map_path') or
            ''
        )
        if map_path and os.path.exists(map_path):
            game['seatmap_image'] = get_image_data_uri(map_path)
        else:
            game['seatmap_image'] = game.get('seatmap_image', '')
        saved_with_maps.append(game)

    event_name = (order_data.get('event_name') or '').strip()
    games = []
    if saved_with_maps:
        games = saved_with_maps
    elif event_name:
        venue = order_data.get('venue', '') or order_data.get('venue_name', '')
        event_city = order_data.get('event_city', '') or venue
        main = {
            'display_text': event_name,
            'details': f"{venue}, {event_city}" if venue else (order_data.get('event_date') or ''),
            'event_date': order_data.get('event_date', ''),
            'event_city': event_city,
            'venue': venue,
            'category': order_data.get('category', ''),
            'num_tickets': order_data.get('num_tickets', 0),
            'seatmap_image': stadium_image_uri or '',
        }
        games.append(main)

    total_games = len(games)
    customer_name = (order_data.get('customer_name') or '').strip() or 'הזמנה רשמית'
    event_type = order_data.get('event_type', 'ספורט')

    cover_line1 = customer_name
    if total_games == 0:
        games_text = "הזמנה"
    elif total_games == 1:
        games_text = "משחק אחד"
    else:
        games_text = f"חבילת {total_games} משחקים"
    cover_line2 = f"{games_text} | {event_type}" if (event_type and event_type != 'ספורט') else games_text

    cities, event_dates = [], []
    for game in games:
        city = game.get('event_city') or (game.get('fixture_data') or {}).get('city', '') or game.get('venue', '')
        if not city and game.get('worldcup_venue'):
            parts = (game.get('worldcup_venue') or '').split(',')
            if len(parts) >= 2:
                city = parts[-1].strip()
        if city and city not in cities:
            cities.append(city)
        date = game.get('event_date') or (game.get('fixture_data') or {}).get('date', '')
        if date and date not in event_dates:
            event_dates.append(date)

    if len(cities) == 1:
        cities_text = f"📍 {cities[0]}"
    elif len(cities) == 2:
        cities_text = f"📍 {cities[0]} & {cities[1]}"
    elif len(cities) > 2:
        cities_text = f"📍 {cities[0]}, {cities[1]} ועוד"
    else:
        cities_text = ""

    date_text = ""
    if event_dates:
        try:
            date_str = str(event_dates[0])
            month_num, year = 0, ""
            if '/' in date_str:
                parts = date_str.split('/')
                if len(parts) >= 3:
                    month_num, year = int(parts[1]), parts[2]
            elif '-' in date_str:
                parts = date_str.split('-')
                if len(parts) >= 3:
                    month_num, year = int(parts[1]), parts[0]
            months_he = {
                1: "ינואר", 2: "פברואר", 3: "מרץ", 4: "אפריל", 5: "מאי", 6: "יוני",
                7: "יולי", 8: "אוגוסט", 9: "ספטמבר", 10: "אוקטובר", 11: "נובמבר", 12: "דצמבר"
            }
            date_text = f"📅 {months_he.get(month_num, '')} {year}".strip() if month_num else (f"📅 {year}" if year else "")
        except Exception:
            pass
    cover_line3 = f"{cities_text} | {date_text}".strip(' |') if (cities_text or date_text) else ""

    return (cover_line1, cover_line2, cover_line3, games, total_games)


def prepare_template_data(order_data: dict, images: dict) -> dict:
    """
    הכנת נתונים לתבנית HTML (תאימות מלאה ל-order_template.html)
    """
    data = order_data.copy()

    # תמונות מהמשתמש או מנתיבים
    stadium_uri = None
    if images.get('stadium_image'):
        stadium_uri = get_image_data_uri(images['stadium_image'])
        data['seatmap_image'] = stadium_uri
    if images.get('stadium_photo'):
        data['stadium_photo_path'] = get_image_data_uri(images['stadium_photo'])
    if images.get('hotel_image'):
        data['hotel_image_path'] = get_image_data_uri(images['hotel_image'])
    if images.get('hotel_image_2'):
        data['hotel_image_2'] = get_image_data_uri(images['hotel_image_2'])
        data['hotel_image_path_2'] = data['hotel_image_2']
    if images.get('home_team_badge'):
        data['home_team_badge'] = get_image_data_uri(images['home_team_badge'])
    if images.get('away_team_badge'):
        data['away_team_badge'] = get_image_data_uri(images['away_team_badge'])

    # נכסים מהפרויקט (כריכה, לוגו, באנר)
    if not data.get('cover_image') and not images.get('cover_image'):
        cover_path = _PROJECT_ROOT / 'assets' / 'cover_page.jpg'
        if cover_path.exists():
            data['cover_image'] = get_image_data_uri(str(cover_path))
    elif images.get('cover_image'):
        data['cover_image'] = get_image_data_uri(images['cover_image'])

    if not data.get('logo_path') and not images.get('logo_path'):
        for name in ('assets/logo_red.png', 'static/logo_red.png'):
            p = _PROJECT_ROOT / name.replace('/', os.sep)
            if p.exists():
                data['logo_path'] = get_image_data_uri(str(p))
                break

    if not data.get('header_banner'):
        for name in ('assets/header_banner.png', 'assets/header_banner.jpg'):
            p = _PROJECT_ROOT / name.replace('/', os.sep)
            if p.exists():
                data['header_banner'] = get_image_data_uri(str(p))
                break

    # כותרת כריכה ו-games
    stadium_uri = data.get('seatmap_image') or stadium_uri
    cover_line1, cover_line2, cover_line3, games, total_games = _build_cover_lines_and_games(order_data, stadium_uri)
    data['cover_line1'] = cover_line1
    data['cover_line2'] = cover_line2
    data['cover_line3'] = cover_line3
    data['games'] = games
    data['total_games'] = total_games
    data['saved_games'] = data.get('saved_games', [])

    # terms
    terms_path = _PROJECT_ROOT / 'terms.txt'
    terms_text = ""
    legal_text_page1 = ""
    legal_text_page2 = ""
    if terms_path.exists():
        try:
            with open(terms_path, 'r', encoding='utf-8') as f:
                terms_lines = f.readlines()
            mid = len(terms_lines) // 2
            legal_text_page1 = ''.join(terms_lines[:mid]).replace('\n', '<br>')
            legal_text_page2 = ''.join(terms_lines[mid:]).replace('\n', '<br>')
            terms_text = legal_text_page1 + legal_text_page2
        except Exception:
            pass
    data['terms_text'] = terms_text
    data['legal_text'] = terms_text
    data['legal_text_page1'] = legal_text_page1
    data['legal_text_page2'] = legal_text_page2

    # תאימות שמות: התבנית משתמשת ב-seatmap_image / stadium_image / stadium_image_path
    if data.get('seatmap_image'):
        data['stadium_image'] = data['seatmap_image']
        data['stadium_image_path'] = data['seatmap_image']

    # חישוב גבהים
    has_stadium_photo = bool(images.get('stadium_photo') or data.get('stadium_photo_path'))
    seatmap_h, photo_h = calculate_seatmap_height(order_data, has_stadium_photo)
    data['seatmap_height_px'] = seatmap_h
    data['stadium_photo_height_px'] = photo_h

    # created_at / order_id / creation_date / event_date_str (לתבנית החדשה)
    if not data.get('created_at'):
        data['created_at'] = order_data.get('creation_date') or datetime.now().strftime('%d/%m/%Y')
    if not data.get('order_id'):
        data['order_id'] = data.get('order_number', '')
    data['creation_date'] = data.get('created_at', '')
    data['event_date_str'] = data.get('event_date') or data.get('created_at', '')
    data['currency_symbol'] = data.get('currency_symbol', '€')
    data['total_foreign'] = data.get('total_euro') if 'total_euro' in data else data.get('total_foreign')

    # passengers / flights
    if isinstance(data.get('passengers'), str):
        try:
            data['passengers'] = json.loads(data['passengers'])
        except Exception:
            data['passengers'] = []
    if isinstance(data.get('flights'), str):
        try:
            data['flights'] = json.loads(data['flights'])
        except Exception:
            data['flights'] = []

    # saved_games עם seatmap_image + stadium_map_path (Data URI) לתבנית החדשה
    saved = data.get('saved_games', [])
    if isinstance(saved, list):
        out = []
        for sg in saved:
            s = dict(sg)
            path = s.get('stadium_map_path') or s.get('worldcup_stadium_map') or s.get('league_stadium_map_path')
            if path and os.path.exists(path):
                uri = get_image_data_uri(path)
                s['seatmap_image'] = uri
                s['stadium_map_path'] = uri
            else:
                s['seatmap_image'] = s.get('seatmap_image', '')
                s['stadium_map_path'] = s.get('seatmap_image', '')
            if not s.get('event_name') and s.get('display_text'):
                s['event_name'] = s['display_text']
            if not s.get('venue') and s.get('venue_name'):
                s['venue'] = s['venue_name']
            out.append(s)
        data['saved_games'] = out

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
        template_path = current_dir / 'templates' / 'order_template.html'
    
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
