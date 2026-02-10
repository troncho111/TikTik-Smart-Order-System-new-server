# 🎨 Canva PDF Template Integration Guide
## מדריך לאינטגרציה של תבנית PDF מ-Canva למערכת TikTik

---

## 📋 **1. רשימת כל השדות שצריכים להופיע ב-PDF**

### **פרטי הזמנה בסיסיים:**
- `order_number` - מספר הזמנה (דוגמה: TT-20260205-3F8C464E)
- `created_at` - תאריך יצירה (דוגמה: 05/02/2026)
- `customer_name` - שם לקוח (דוגמה: Israel Israeli)
- `customer_id` - ת.ז. לקוח
- `customer_phone` - טלפון לקוח
- `customer_email` - אימייל לקוח

### **פרטי אירוע:**
- `event_name` - שם האירוע (דוגמה: מנצ'סטר יונייטד נגד ליברפול)
- `event_type` - סוג אירוע (כדורגל / הופעה / מונדיאל)
- `event_date` - תאריך האירוע (דוגמה: 08/02/2026 13:30)
- `venue` / `venue_name` - מקום האירוע (דוגמה: Old Trafford, Manchester)
- `event_city` - עיר (דוגמה: Manchester)
- `is_date_final` - האם התאריך סופי (true/false)

### **פרטי כרטיסים:**
- `category` - קטגוריה (דוגמה: CAT 3)
- `num_tickets` - מספר כרטיסים (דוגמה: 4)
- `ticket_description` - תיאור כרטיסים
- `seats_together` - ישיבה ביחד (true/false)

### **מחירים:**
- `price_per_ticket` - מחיר לכרטיס באירו
- `total_euro` - סה"כ באירו (דוגמה: €2200)
- `exchange_rate` - שער חליפין (דוגמה: 3.73)
- `total_nis` - סה"כ בשקלים (דוגמה: ₪8,206)
- `final_price` - מחיר סופי

### **תמונות:**
- `stadium_image_path` - מפת אצטדיון (base64 או URL)
- `stadium_photo_path` - תמונת אווירה של האצטדיון
- `cover_image` - תמונת רקע לעמוד שער
- `logo_path` - לוגו TikTik

### **מלון (אם יש חבילה):**
- `hotel_name` - שם מלון (דוגמה: The Lowry Hotel)
- `hotel_address` - כתובת מלון
- `hotel_stars` - דירוג (דוגמה: 4.5 כוכבים)
- `hotel_nights` - מספר לילות (דוגמה: 3)
- `hotel_meals` - ארוחות (דוגמה: ארוחת בוקר)
- `hotel_rating` - דירוג (דוגמה: 4.5)
- `hotel_website` - אתר מלון
- `hotel_image_path` - תמונה 1 של מלון
- `hotel_image_2_path` - תמונה 2 של מלון

### **טיסות (אם יש חבילה):**
```json
"flights": [
  {
    "direction": "הלוך",
    "from": "TLV",
    "to": "MAN",
    "date": "07/02/2026",
    "time": "06:00",
    "departure_time": "06:00",
    "arrival_time": "11:30",
    "flight_no": "LY123",
    "airline": "אל-על"
  },
  {
    "direction": "חזור",
    "from": "MAN",
    "to": "TLV",
    "date": "10/02/2026",
    "time": "14:00",
    "departure_time": "14:00",
    "arrival_time": "21:00",
    "flight_no": "LY124",
    "airline": "אל-על"
  }
]
```

### **נוסעים:**
```json
"passengers": [
  {
    "name": "Israel Israeli",
    "full_name": "Israel Israeli",
    "first_name": "Israel",
    "last_name": "Israeli",
    "passport_number": "12345678",
    "dob": "15/03/1985",
    "birth_date": "15/03/1985",
    "ticket_type": "כרטיס רגיל"
  }
]
```

### **תוספות לחבילה:**
- `transfers` - העברות (true/false)
- `bag_trolley` - טרולי (true/false)
- `bag_checked` - מזוודה (דוגמה: "23 ק״ג")

### **משחקים מרובים (multi-game):**
```json
"games": [
  {
    "display_text": "מנצ'סטר יונייטד נגד ליברפול",
    "event_name": "Manchester United vs Liverpool",
    "event_date": "08/02/2026",
    "event_city": "Manchester",
    "venue": "Old Trafford",
    "category": "CAT 3",
    "num_tickets": 4,
    "seatmap_image": "base64...",
    "is_date_final": false
  }
]
```

### **עמוד שער (Cover Page):**
- `cover_title` - כותרת ראשית
- `cover_line1` - שורה 1 (בדרך כלל שם לקוח)
- `cover_line2` - שורה 2 (סוג חבילה)
- `cover_line3` - שורה 3 (ערים ותאריך)

---

## 🎨 **2. דוגמת JSON מלאה - תעתיק את זה ל-AI:**

```json
{
  "order_number": "TT-20260205-3F8C464E",
  "created_at": "05/02/2026",
  "customer_name": "Israel Israeli",
  "customer_id": "123456789",
  "customer_phone": "050-1234567",
  "customer_email": "israel@example.com",

  "product_type": "package",

  "event_name": "מנצ'סטר יונייטד נגד ליברפול",
  "event_type": "כדורגל",
  "event_date": "08/02/2026 13:30",
  "venue": "Old Trafford",
  "venue_name": "Old Trafford, Manchester",
  "event_city": "Manchester",
  "is_date_final": false,

  "category": "CAT 3",
  "num_tickets": 4,
  "seats_together": true,

  "price_per_ticket": 550,
  "total_euro": 2200,
  "exchange_rate": 3.73,
  "total_nis": 8206,
  "final_price": "8,206",

  "hotel_name": "The Lowry Hotel",
  "hotel_address": "Dearmans Pl, Salford M3 5LH, UK",
  "hotel_stars": "4.5",
  "hotel_nights": 3,
  "hotel_meals": "ארוחת בוקר",
  "hotel_rating": "4.5",

  "flights": [
    {
      "direction": "הלוך",
      "from": "TLV",
      "to": "MAN",
      "date": "07/02/2026",
      "time": "06:00",
      "departure_time": "06:00",
      "arrival_time": "11:30",
      "flight_no": "LY123",
      "airline": "אל-על"
    },
    {
      "direction": "חזור",
      "from": "MAN",
      "to": "TLV",
      "date": "10/02/2026",
      "time": "14:00",
      "departure_time": "14:00",
      "arrival_time": "21:00",
      "flight_no": "LY124",
      "airline": "אל-על"
    }
  ],

  "passengers": [
    {
      "name": "Israel Israeli",
      "passport_number": "12345678",
      "birth_date": "15/03/1985",
      "ticket_type": "כרטיס רגיל"
    },
    {
      "name": "Sarah Israeli",
      "passport_number": "87654321",
      "birth_date": "22/07/1988",
      "ticket_type": "כרטיס רגיל"
    },
    {
      "name": "Noam Israeli",
      "passport_number": "11998877",
      "birth_date": "12/09/2010",
      "ticket_type": "כרטיס ילד"
    },
    {
      "name": "Tamar Israeli",
      "passport_number": "22334455",
      "birth_date": "20/11/2015",
      "ticket_type": "כרטיס ילד"
    }
  ],

  "transfers": false,
  "bag_trolley": true,
  "bag_checked": "23 ק״ג",

  "cover_title": "מנצ'סטר יונייטד נגד ליברפול",
  "cover_line1": "Israel Israeli",
  "cover_line2": "משחק אחד | כדורגל",
  "cover_line3": "📍 Manchester | 📅 פברואר 2026"
}
```

---

## 🤖 **3. הנחיות ל-AI ב-Canva (Copy-Paste):**

```
אני צריך לעצב תבנית PDF מקצועית עבור מערכת הזמנות ספורט.

מבנה ה-PDF:

עמוד 1 - COVER PAGE (עמוד שער):
- רקע מרשים עם תמונה של אצטדיון/אווירת משחק
- כותרת גדולה: {cover_line1} - שם הלקוח
- תת-כותרת: {cover_line2} - סוג חבילה
- פרטים: {cover_line3} - עיר ותאריך
- מספר הזמנה בתחתית: {order_number}
- לוגו TikTik

עמוד 2 - פרטי האירוע:
- כותרת: "פרטי האירוע והמושבים"
- כרטיס אירוע עם:
  * שם האירוע: {event_name}
  * תאריך: {event_date}
  * מקום: {venue_name}, {event_city}
  * קטגוריה: {category}
  * מספר כרטיסים: {num_tickets}
- מפת אצטדיון (מקום לתמונה)
- תמונת אווירה של האצטדיון

עמוד 3 - חבילת האירוח (אם יש):
- פרטי מלון:
  * שם: {hotel_name}
  * כתובת: {hotel_address}
  * דירוג: {hotel_stars} כוכבים
  * לילות: {hotel_nights}
  * ארוחות: {hotel_meals}
- 2 תמונות מלון
- טבלת נוסעים עם עמודות:
  * # (מספר)
  * שם מלא
  * מספר דרכון
  * תאריך לידה
  * סוג כרטיס

עמוד 4 - סיכום ותשלום:
- טבלת סיכום הזמנה
- סה"כ לתשלום (גדול ובולט): ₪{total_nis}
- פירוט באירו: €{total_euro}
- שדות חתימה:
  * שם הלקוח
  * חתימת הלקוח
  * תאריך

דרישות עיצוב:
✅ עברית RTL - הכל מימין לשמאל
✅ פונטים ברורים וקריאים (Arial / Helvetica)
✅ צבעים: כחול כהה (#1a2332), זהב (#d4a84b), לבן
✅ עיצוב מודרני ונקי (כמו Airbnb/Booking)
✅ תמונות ממורכזות תמיד
✅ רווחים נכונים בין אלמנטים
✅ גודל עמוד: A4
✅ נראה מקצועי ומותאם למותג ספורט יוקרתי

השתמש בצבעים:
- רקע לבן/אפור בהיר
- כותרות: כחול כהה
- הדגשות: זהב
- טקסט רגיל: שחור/אפור כהה
```

---

## 🔗 **4. אינטגרציה עם Python - קוד מוכן:**

לאחר שתעצב את התבנית ב-Canva, הנה הקוד לשילוב:

```python
# install: pip install canva-python reportlab
from canva import CanvaAPI
import json

def generate_pdf_with_canva(order_data):
    """
    Generate PDF using Canva template
    """
    # התחבר ל-Canva API
    canva = CanvaAPI(api_key="YOUR_CANVA_API_KEY")

    # מצא את התבנית שלך
    template_id = "YOUR_TEMPLATE_ID"

    # מילוי הנתונים בתבנית
    design = canva.get_design(template_id)
    design.autofill({
        "order_number": order_data.get("order_number"),
        "customer_name": order_data.get("customer_name"),
        "event_name": order_data.get("event_name"),
        "event_date": order_data.get("event_date"),
        "venue": order_data.get("venue"),
        "category": order_data.get("category"),
        "num_tickets": order_data.get("num_tickets"),
        "total_nis": order_data.get("total_nis"),
        "total_euro": order_data.get("total_euro"),
        # ... שאר השדות
    })

    # ייצוא ל-PDF
    pdf_bytes = design.export_pdf()

    return pdf_bytes
```

---

## 📦 **5. חלופות ל-Canva API:**

אם Canva API לא נגיש, אפשר:

### **אפשרות A: ייצוא כ-HTML מ-Canva**
1. עצב ב-Canva
2. ייצא כ-HTML
3. השתמש ב-WeasyPrint כמו עכשיו

### **אפשרות B: ReportLab (Python Pure)**
```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# תמיכה בעברית
pdfmetrics.registerFont(TTFont('Hebrew', 'Arial.ttf'))

def create_pdf(order_data):
    c = canvas.Canvas("order.pdf", pagesize=A4)
    c.setFont("Hebrew", 24)
    # ... בניית ה-PDF
```

### **אפשרות C: Puppeteer/Playwright**
```python
from playwright.sync_api import sync_playwright

def html_to_pdf(html_content):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.set_content(html_content)
        pdf_bytes = page.pdf(format='A4')
        browser.close()
    return pdf_bytes
```

---

## ✅ **6. Checklist - מה לעשות עכשיו:**

- [ ] העתק את ה-JSON לדוגמה
- [ ] העתק את ההנחיות ל-AI
- [ ] פתח Canva
- [ ] העלה את ההנחיות ל-AI ב-Canva
- [ ] תן ל-AI לעצב תבנית
- [ ] ייצא את התבנית
- [ ] שלב עם הקוד שלך

---

## 💡 **טיפים:**

1. **התחל פשוט** - עשה עמוד אחד קודם, אחר כך הוסף
2. **בדוק בדפוס** - ודא שהכל נראה טוב גם בהדפסה
3. **שמור עקביות** - צבעים, פונטים, רווחים
4. **בדוק עם נתונים אמיתיים** - לא רק דוגמאות

---

**בהצלחה! אני פה אם תצטרך עזרה! 🚀**
