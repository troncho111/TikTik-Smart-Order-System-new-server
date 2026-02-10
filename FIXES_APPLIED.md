# תיקונים שבוצעו - TikTik Smart Order System

## תאריך: 2026-02-07

### 1. סריקת דרכונים (Passport OCR)
**בעיה:** לא היה תמיכה ב-`AI_INTEGRATIONS_GEMINI_BASE_URL` (מפתחות/פרוקסי).

**תיקון:**
- הוספת תמיכה ב-`AI_INTEGRATIONS_GEMINI_BASE_URL` ב-`passport_ocr.py`
- מבנה URL מתוקן: `{base_url}/models/gemini-2.5-flash:generateContent`

### 2. סריקת טיסות (Flight OCR)
**בעיה:** כפילות ב-URL כאשר משתמשים ב-base_url – נוסף `v1beta` פעמיים.

**תיקון:**
- תיקון ב-`flight_ocr.py`: `{base_url}/models/...` במקום `{base_url}/v1beta/models/...`
- ה-base_url כבר כולל v1beta

### 3. חיפוש מלון (Hotel Resolver)
**בעיה:** `NameError` – משתנה `venue` לא הוגדר כשמגיעים לעמוד המלון (למשל בלי לשמור אירועים קודם).

**תיקון:**
- חישוב `venue` מתוך `saved_games` בתוך בלוק חיפוש המלון
- הוספת fallback בטוח כשאין אירועים שמורים

### 4. אזהרת סריקת טיסות
**תיקון:** הודעת אזהרה עודכנה – כוללת גם "הדבק" ולא רק "העלה".

### 5. משתני סביבה נדרשים
ודא ש-.env מכיל:
```
AI_INTEGRATIONS_GEMINI_API_KEY=...
AI_INTEGRATIONS_GEMINI_API_KEY_2=...  # אופציונלי
AI_INTEGRATIONS_GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta  # אופציונלי
GOOGLE_PLACES_API_KEY=...  # לחיפוש מלונות
```

### 6. בדיקה ידנית מומלצת
1. **דרכון:** העלה תמונת דרכון → לחץ "🔍 סרוק דרכונים והוסף נוסעים"
2. **טיסות:** העלה צילום מסך טיסות → לחץ "🔍 סרוק פרטי טיסות"
3. **מלון:** הזן שם מלון (למשל "Hilton Madrid") → לחץ "🔍 חפש מלון"

### TestSprite / Playwright
- האפליקציה נבדקה עם Playwright – עמוד ההתחברות ונווט עובדים
- להרצת TestSprite: הפעל את ה-MCP עם `localPort: 8505` (או 5000 בפרודקשן)
