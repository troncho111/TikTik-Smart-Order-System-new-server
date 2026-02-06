# 🎯 TikTik Refactored - מבנה חדש

## 📦 מבנה הפרויקט

```
tiktik/
├── Home_refactored.py                    # עמוד ראשי
│
├── pages_refactored/                     # דפי Streamlit
│   └── 1_New_Order_Wizard.py            # ממשק אשף - 4 שלבים
│
├── services_refactored/                  # לוגיקה עסקית
│   ├── __init__.py
│   ├── auth_service.py                  # אימות משתמשים
│   ├── ai_service.py                    # Gemini AI
│   ├── order_service.py                 # ניהול הזמנות
│   ├── pdf_service.py                   # יצירת PDF
│   ├── static/                          # CSS + תמונות
│   └── templates/                       # תבניות HTML
│
└── utils_refactored/                     # פונקציות עזר
    ├── __init__.py
    ├── session.py                       # ניהול session
    └── formatters.py                    # עיצוב טקסט/מספרים
```

## 🚀 איך להריץ את המערכת החדשה?

### 1. העתקת הקבצים למיקום הנכון

```bash
# גיבוי הקבצים הישנים
mv Home.py Home_old.py
mv pages pages_old
mv app.py app_old.py

# העברת הקבצים החדשים
mv Home_refactored.py Home.py
mv pages_refactored pages
mv services_refactored services
mv utils_refactored utils
```

### 2. הרצת המערכת

```bash
streamlit run Home.py
```

## ✨ מה השתנה?

### לפני (הקוד הישן):
- ❌ `app.py` - 6,878 שורות
- ❌ 44 פונקציות במקום אחד
- ❌ קשה לתחזוקה
- ❌ קשה להוסיף תכונות

### אחרי (הקוד החדש):
- ✅ מבנה מודולרי - כל דבר במקום שלו
- ✅ `services/` - לוגיקה עסקית נפרדת
- ✅ `utils/` - פונקציות עזר
- ✅ `pages/` - ממשק אשף חדש
- ✅ קל לתחזוקה ולהרחבה

## 📝 ממשק האשף החדש

### 4 שלבים ברורים:

1. **שלב 1 - בחירת סוג מוצר ואירוע**
   - חבילה מלאה / כרטיסים בלבד
   - כדורגל / הופעה / אחר

2. **שלב 2 - פרטי האירוע**
   - שם האירוע, מקום, תאריך
   - מספר כרטיסים
   - פרטי מלון (אם חבילה מלאה)

3. **שלב 3 - פרטי לקוח ונוסעים**
   - שם, אימייל, טלפון
   - רשימת נוסעים

4. **שלב 4 - סיכום**
   - תצוגה מסודרת של כל הפרטים
   - שמירת הזמנה
   - יצירת PDF

## 🎨 עיצוב

- ✅ **RTL מלא** - כל הטקסט מימין לשמאל
- ✅ **פס התקדמות ויזואלי** - רואים בדיוק איפה אתם
- ✅ **כרטיסים מעוצבים** - עיצוב מודרני ונקי
- ✅ **צבעים עקביים** - גרדיאנטים כחול-סגול

## 🔧 Services (שירותים)

### auth_service.py
```python
from services import create_user_session, validate_session_token
```

### ai_service.py
```python
from services import ai_chat_response
```

### order_service.py
```python
from services import save_order_to_db, get_all_orders
```

### pdf_service.py
```python
from services import generate_pdf
```

## 🛠️ Utils (עזרים)

### session.py
```python
from utils import init_session_state, get_session_value
```

### formatters.py
```python
from utils import format_price, format_date
```

## 📊 השוואה

| תכונה | לפני | אחרי |
|-------|------|------|
| שורות קוד | 6,878 | ~1,500 |
| קבצים | 3 | 10+ |
| מבנה | מונוליתי | מודולרי |
| תחזוקה | קשה | קל |
| הרחבה | קשה | קל |
| בדיקות | קשה | קל |

## 🎯 מה הלאה?

1. ✅ **הושלם:** Refactoring + ממשק אשף
2. ⏳ **בהמשך:** העברת שאר הדפים (היסטוריה, ייצוא, וכו')
3. ⏳ **בהמשך:** בדיקות אוטומטיות
4. ⏳ **בהמשך:** תיעוד מלא

## 💡 טיפים

- השתמשו ב-`services/` לכל הלוגיקה העסקית
- השתמשו ב-`utils/` לפונקציות עזר
- כל דף ב-`pages/` צריך להיות עצמאי
- שמרו על העיצוב עקבי

## 🐛 בעיות נפוצות

### "ModuleNotFoundError: No module named 'services'"
**פתרון:** ודאו שהתיקיות `services/` ו-`utils/` נמצאות בשורש הפרויקט.

### "הדף לא מוצא את ה-services"
**פתרון:** הוסיפו בראש הקובץ:
```python
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
```

## 📞 תמיכה

יש בעיה? צריכים עזרה? פנו למפתח המערכת!

---

**TikTik Smart Order System - Refactored Edition** 🎉
