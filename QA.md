# TikTik – QA ובודקים

## בודקים אוטומטיים (להריץ לפני דחיפה)

### 1. בדיקת ייבואים (מונע NameError)
```bash
cd /root/TikTik-Smart-Order-System-new-server
./venv/bin/python3 -m tests.qa_app_imports
# או
./venv/bin/python3 -c "from tests.qa_app_imports import test_critical_names_exist; test_critical_names_exist(); print('OK')"
```

### 2. TestSprite (Frontend / Backend)
- **Bootstrap:** להריץ את כלי ה-TestSprite עם `localPort`, `type` (frontend/backend), `projectPath`, `testScope`.
- **תוכנית בדיקות:** ליצור test plan (frontend עם/בלי login, backend).
- **הרצה:** להריץ את ה-tests עם `testsprite_generate_code_and_execute` (projectName, projectPath, testIds, additionalInstruction).
- **דשבורד:** לפתוח את הדשבורד עם `testsprite_open_dashboard` לצפייה בתוצאות ועריכה.

### 3. Playwright (E2E בדפדפן)
- שימוש ב-MCP **cursor-ide-browser** או **playwright**: ניווט, snapshot, click, type, וכו'.
- להריץ תרחישים: התחברות, הזמנה חדשה, הדבקת תמונה (טיסות/דרכון), שמירה.

---

## רשימת בדיקה ידנית (QA)

- [ ] **התחברות** – לוגין, התנתקות, token
- [ ] **הזמנה חדשה – תרשים מושבים** – הדבק מהלוח, העלאת קובץ
- [ ] **הזמנה חדשה – טיסות** – הדבק צילום מסך, סריקת טיסות (OCR)
- [ ] **הזמנה חדשה – דרכונים** – הדבק דרכון, סריקה (OCR)
- [ ] **הזמנה חדשה – מלון** – חיפוש, בחירה
- [ ] **שמירת הזמנה** – כפתור שמירה, יצירת PDF
- [ ] **היסטוריית הזמנות** – רשימה, סינון
- [ ] **ייצוא** – Excel/PDF
- [ ] **RTL** – כיוון עברית תקין בכל המסכים

---

## ארכיטקטורה – מקורות אמת

- **נקודת כניסה:** `app.py` → `main()` → `page_new_order()` (ו-pages אחרים).
- **ייבואים:** כל השמות שבשימוש ב-`page_new_order` (טיסות, דרכונים, מלון, שדות תעופה, הדבק תמונה) חייבים להיות מיובאים בראש `app.py` או מוגדרים בתוך הקובץ.
- **מודולים:** `flight_ocr`, `passport_ocr`, `hotel_resolver`, `airports`, `airline_codes`, `stadium_api`, `streamlit_paste_button` – כולם מיובאים בראש `app.py`.
- **ספריות סטנדרטיות:** `io`, `json`, `random`, `requests` – מיובאות בראש `app.py` (למניעת NameError בהדבקות טיסות/דרכונים).
