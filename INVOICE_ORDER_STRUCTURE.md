# מבנה הזמנה (Invoice) – ל־React / v0

מסמך זה מתאר את מבנה ה-JSON של ההזמנה, ה-DB, והתבניות – כדי לחבר קומפוננטת React 1:1 למערכת.

---

## 1. מבנה ה-JSON המלא של הזמנה (מה שנשלח ל־PDF/תצוגה)

האובייקט נבנה ב־`app.py` (סביב שורות 4426–4470) ונשלח ל־`generate_pdf()` יחד עם קבצי תמונה (paths או PIL). ה-PDF ממיר paths ל־data URIs (base64) לפני ה־template.

### 1.1 שדות תמונות – מקור ושם שדה

| שימוש | שם שדה ב־order_data | מקור | הערות |
|--------|----------------------|------|--------|
| תמונות מלון (תמונה ראשית) | `hotel_image_path` | `hotel_data.hotel_image_path` (מ־HotelCache / חיפוש מלון) | נתיב קובץ בשרת. ב־PDF מומר ל־data URI ומועבר כ־`hotel_image` / `hotel_image_path`. |
| תמונות מלון (תמונה שנייה) | `hotel_image_2_path` | `hotel_data.hotel_image_path_2` | כמו למעלה. ב־template: `hotel_image_2`. |
| מפת אצטדיון (כללי / משחק בודד) | `stadium_image_path` | מפת ליגה/קבוצה או מפת מונדיאל | נתיב קובץ. ב־PDF מומר ל־data URI. |
| תמונת אווירה/רקע (עמוד כיסוי או ליד משחק) | `stadium_photo_path` | אקראי מ־AtmosphereImage או מהמשתמש | נתיב קובץ. ב־template: `stadium_photo_path` (כ־data URI). |
| מפת אצטדיון **לכל משחק** | בתוך כל איבר ב־`saved_games`: `stadium_map_path` או `league_stadium_map_path` או `worldcup_stadium_map` | לכל אירוע: מפת ליגה/מונדיאל/הופעה/הדבקה | ב־PDF: לכל game נוסף `seatmap_image` (data URI). ב־template: `game.seatmap_image`. |
| באנר עליון (header) | **לא** ב־order_data | קבוע בשרת: `assets/header_banner.png` או `header_banner.jpg` | ה־PDF ממיר לקובץ ל־data URI ומעביר ל־template כ־`header_banner`. ב־React: URL קבוע, למשל `/assets/header_banner.png`. |
| באנר תחתון (footer / payment) | **לא** ב־order_data | **קבוע** בתבנית: `assets/payment_banner.png` | לא דינמי. ב־HTML: `<img src="assets/payment_banner.png">`. ב־React: URL קבוע. |

### 1.2 רשימת כל השדות ב־order_data (לפני המרה ל־template)

```ts
// זה ה־payload שנבנה ב-app.py ונשלח ל-generate_pdf (כ־order_data)
// תמונות: מועברות כפרמטרים נפרדים (paths או PIL) ומומרות ל־data URI בתוך generate_pdf
interface OrderDataPayload {
  product_type: 'tickets' | 'package';
  event_name: string;
  event_type: string;           // 'כדורגל' | 'הופעה' | 'אחר'
  event_date: string;           // "DD/MM/YYYY HH:MM"
  event_date_str: string;       // "DD/MM/YYYY"
  event_time_str: string;       // "HH:MM"
  venue: string;
  customer_name: string;
  customer_id: string;
  customer_phone: string;
  customer_email: string;
  ticket_description: string;
  category: string;
  currency: string;
  currency_symbol: string;
  price_per_ticket: number;
  price_nis: number;
  total_foreign: number;
  total_euro: number;
  total_nis: number;
  num_tickets: number;
  passengers: PassengerPayload[];
  exchange_rate: number;
  home_team_badge?: string;     // URL or data URI
  away_team_badge?: string;
  home_team_name?: string;
  away_team_name?: string;
  hotel_name: string;
  hotel_nights: number;
  hotel_stars: string;
  hotel_meals: string;
  hotel_address: string;
  hotel_website: string;
  hotel_rating: string;
  hotel_image_path: string;     // file path on server → becomes data URI in template
  hotel_image_path_2: string;
  flight_details: string;       // formatted text
  flights: FlightLegPayload[];
  transfers: boolean;
  bag_trolley: boolean;
  bag_checked: string;
  is_date_final: boolean;
  seats_together: boolean;
  saved_games: SavedGamePayload[];
  order_number?: string;        // set right before calling generate_pdf
}

interface PassengerPayload {
  first_name?: string;
  last_name?: string;
  name?: string;
  full_name?: string;
  passport?: string;
  passport_number?: string;
  birth_date?: string;
  dob?: string;
  passport_expiry?: string;
  ticket_type?: string;
}

interface FlightLegPayload {
  direction: 'הלוך' | 'חזור';
  from: string;   // IATA
  to: string;
  date: string;
  time: string;
  flight_no: string;
  airline: string;
}

interface SavedGamePayload {
  display_text: string;
  details?: string;
  event_date?: string;
  event_time?: string;
  venue?: string;
  event_city?: string;
  category?: string;
  concert_selected_category?: string;
  worldcup_category?: string;
  num_tickets?: number;
  fixture_data?: { date?: string; time?: string; venue?: string; city?: string; round?: string };
  worldcup_venue?: string;
  concert_venue_name?: string;
  concert_venue_city?: string;
  stadium_map_path?: string;      // path → PDF adds seatmap_image (data URI)
  league_stadium_map_path?: string;
  worldcup_stadium_map?: string;
  seatmap_image?: string;         // added by PDF generator (data URI)
}
```

---

## 2. מבנה ה-DB (Schema/Models)

### 2.1 Order (טבלת orders)

```ts
interface OrderRecord {
  id: number;
  order_number: string;
  created_at: string;  // datetime
  updated_at: string;
  user_id: number | null;
  event_name: string;
  event_date: string;
  event_time: string;
  venue: string;
  event_type: 'football' | 'concert' | 'other';
  customer_name: string;
  customer_id: string;
  customer_email: string;
  customer_phone: string;
  ticket_description: string | null;
  block: string;       // category stored here
  row: string;
  seats: string;
  num_tickets: number;
  price_per_ticket_euro: number;
  exchange_rate: number;
  total_euro: number;
  total_nis: number;
  passengers: string;  // JSON string
  games_data: string | null;  // JSON string (optional, not always filled on save)
  status: 'draft' | 'sent' | 'viewed' | 'signed' | 'cancelled';
  sent_at: string | null;
  viewed_at: string | null;
  signed_at: string | null;
  signature_token: string | null;
  signature_image: string | null;
  pdf_path: string | null;
  notes: string | null;
}
```

הערה: ב־`save_order_to_db()` לא נשמרים `games_data`, `hotel_*`, `flights` – רק השדות הבסיסיים של ההזמנה ו־`passengers` כ־JSON. ה־payload המלא (כולל saved_games, hotel, flights) משמש ל־PDF ויכול להישמר כ־JSON במקום אחר או ב־API.

### 2.2 Games/Events

אין טבלת `games` נפרדת. אירועים מגיעים כ־**רשימה בתוך ה־payload**:

- בטופס: `st.session_state.saved_games` – כל איבר הוא אובייקט משחק (כמו `SavedGamePayload`).
- ב־DB: ב־`Order` יש רק `games_data` (Text/JSON) ואפשרות שלא למלא אותו.

מבנה כל “משחק” (כמו ב־saved_games) – ראה `SavedGamePayload` למעלה. שדה תרשים אצטדיון: `stadium_map_path` (או `league_stadium_map_path` / `worldcup_stadium_map`). ב־template כל game מקבל גם `seatmap_image` (data URI).

### 2.3 Hotels

אין טבלת `hotels` עם פרטי הזמנה. יש **HotelCache** (חיפוש מלונות):

```ts
interface HotelCacheRecord {
  id: number;
  search_query: string;
  hotel_name: string;
  hotel_address: string;
  hotel_website: string;
  hotel_rating: number;
  hotel_image_path: string;   // path to image 1
  hotel_image_path_2: string; // path to image 2
  place_id: string;
  created_at: string;
}
```

בהזמנה: פרטי המלון ונתיבי התמונות מגיעים מ־`hotel_data` (למשל מ־HotelCache) ונכנסים ל־order_data כ־`hotel_name`, `hotel_image_path`, `hotel_image_path_2` וכו'.

### 2.4 Passengers

אין טבלת `passengers` נפרדת. נוסעים נשמרים כ־**JSON** בשדה `Order.passengers` (מערך של אובייקטים עם first_name, last_name, passport, birth_date, passport_expiry, ticket_type וכו').

### 2.5 Flights

אין טבלת `flights` נפרדת. טיסות נשמרות כ־**רשימה בתוך order_data**: `flights: FlightLegPayload[]`, ובעת שמירת חבילה ב־PackageTemplate כ־`flight_data` (JSON string).

### 2.6 ClientProposal (הצעות ללקוח)

```ts
interface ClientProposalRecord {
  id: number;
  proposal_name: string;
  created_at: string;
  updated_at: string;
  user_id: number | null;
  customer_name: string;
  customer_email: string;
  customer_phone: string;
  proposal_data: string;  // JSON: like OrderDataPayload (without order_number)
  total_price_euro: number;
  total_price_nis: number;
  status: 'draft' | 'sent' | 'accepted' | 'rejected';
  is_active: boolean;
  pdf_path: string | null;
  sent_at: string | null;
  viewed_at: string | null;
}
```

### 2.7 PackageTemplate (חבילות קבועות)

```ts
interface PackageTemplateRecord {
  id: number;
  name: string;
  event_type: 'football' | 'concert' | 'other';
  product_type: string;
  event_name: string;
  event_date: string;
  event_time: string;
  venue: string;
  ticket_description: string;
  ticket_category: string;
  price_per_ticket_euro: number;
  hotel_data: string;   // JSON
  flight_data: string; // JSON
  package_price_euro: number;
  stadium_map_data: Buffer | null;
  stadium_map_mime: string | null;
  atmosphere_image_data: Buffer | null;
  atmosphere_image_mime: string | null;
  notes: string;
  created_at: string;
  updated_at: string;
  is_active: boolean;
}
```

---

## 3. הקוד שמרכיב את ה-PDF/HTML

- **פונקציה:** `generate_pdf()` ב־`pdf_generator.py`.
- **תבניות:** `templates/order_template.html` (גרסה 1), `templates/order_template_2.html` (גרסה 2).

### 3.1 מקור נתונים ל־template

- **order_data:** המילון שנבנה ב־app (כולל `hotel_image_path`, `hotel_image_path_2`, `saved_games` עם `stadium_map_path` וכו').
- **תמונות:** מועברות כ־paths (או PIL) ל־`generate_pdf(order_data, stadium_image, hotel_image, hotel_image_2, stadium_photo, template_version)`. בתוך הפונקציה:
  - כל path מומר ל־**data URI** (base64) דרך `get_image_data_uri()`.
  - לכל game ב־saved_games נוסף `seatmap_image` (data URI) לפי `stadium_map_path` (או fallback ל־order_data.stadium_image_path).

### 3.2 שדות עיקריים ב־template (template_data)

- `cover_line1`, `cover_line2`, `cover_line3` – כותרת דף כיסוי.
- `order_number`, `order_id`, `customer_name`, `event_name`, `event_date`, `venue`, `event_type`, `category`, `num_tickets`, `price_per_ticket`, `total_euro`, `total_nis`, `exchange_rate`, `created_at`.
- `passengers` – מערך (עם name, full_name, passport_number, dob, ticket_type).
- `games` – מערך עם `display_text`, `details`, `seatmap_image`, `event_date`, `category` וכו'.
- `logo_path` – data URI של לוגו.
- `header_banner` – data URI של באנר עליון (מקובץ קבוע).
- `stadium_image` / `seatmap_image` / `event_image_path` – data URI של מפת אצטדיון (כללי).
- `stadium_photo_path` – data URI של תמונת אווירה.
- `hotel_image`, `hotel_image_path`, `hotel_image_2` – data URIs של תמונות מלון.
- `hotel_name`, `hotel_nights`, `hotel_stars`, `hotel_meals`, `hotel_address`, `hotel_website`, `hotel_rating`.
- `flights`, `flight_details`, `transfers`, `bag_trolley`, `bag_checked`.
- `seats_together`, `seats_together_image`.

### 3.3 איך תמונות מוצגות

- **תמונות מלון:** עד 2 תמונות. ב־template_2: גלריה עם `hotel_image_path or hotel_image` ו־`hotel_image_2`. גודל: תלוי CSS (למשל תיבות בגלריה).
- **תרשים אצטדיון:** לכל משחק ב־`games`: `game.seatmap_image`. אם אין – מוצג "מפה לא זמינה". מקור: `stadium_map_path` (או league/worldcup map) שהומר ל־data URI.
- **באנר תחתון:** ב־order_template.html: `<img src="assets/payment_banner.png" class="payment-banner-img">` – **URL קבוע**, לא שדה דינמי. גודל: ברוחב מלא (width: 100%).

---

## 4. TypeScript Interface מלא (לשימוש ב־React/v0)

```typescript
// ========== Order / Invoice (מה שצריך לתצוגת טופס הזמנה) ==========

interface OrderData {
  order_number: string;
  created_at: string;

  product_type: 'tickets' | 'package';
  event_name: string;
  event_type: string;
  event_date: string;
  event_date_str?: string;
  event_time_str?: string;
  venue: string;
  event_city?: string;

  customer_name: string;
  customer_id?: string;
  customer_phone?: string;
  customer_email?: string;

  ticket_description?: string;
  category: string;
  currency?: string;
  currency_symbol?: string;
  price_per_ticket: number;
  price_nis?: number;
  total_foreign?: number;
  total_euro: number;
  total_nis: number | string;
  num_tickets: number;
  exchange_rate: number;

  passengers: Passenger[];

  home_team_badge?: string;
  away_team_badge?: string;
  home_team_name?: string;
  away_team_name?: string;

  hotel_name?: string;
  hotel_nights?: number;
  hotel_stars?: string;
  hotel_meals?: string;
  hotel_address?: string;
  hotel_website?: string;
  hotel_rating?: string;
  hotel_image_path?: string;   // URL or path → in PDF becomes data URI
  hotel_image_path_2?: string;

  flight_details?: string;
  flights?: FlightLeg[];
  transfers?: boolean;
  bag_trolley?: boolean;
  bag_checked?: string;

  is_date_final?: boolean;
  seats_together?: boolean;
  saved_games: Game[];

  template_version?: 1 | 2;

  stadium_image_path?: string;
  stadium_photo_path?: string;
}

interface Passenger {
  first_name?: string;
  last_name?: string;
  name?: string;
  full_name?: string;
  passport?: string;
  passport_number?: string;
  birth_date?: string;
  dob?: string;
  passport_expiry?: string;
  ticket_type?: string;
}

interface FlightLeg {
  direction: 'הלוך' | 'חזור';
  from: string;
  to: string;
  date: string;
  time: string;
  flight_no?: string;
  flight_number?: string;
  airline?: string;
}

interface Game {
  display_text: string;
  details?: string;
  event_date?: string;
  event_time?: string;
  venue?: string;
  event_city?: string;
  category?: string;
  concert_selected_category?: string;
  worldcup_category?: string;
  num_tickets?: number;
  fixture_data?: { date?: string; time?: string; venue?: string; city?: string; round?: string };
  worldcup_venue?: string;
  concert_venue_name?: string;
  concert_venue_city?: string;
  stadium_map_path?: string;
  league_stadium_map_path?: string;
  worldcup_stadium_map?: string;
  seatmap_image?: string;
}

// תמונות שמועברות ל־template כ־data URIs (או URLs אם אתם מגישים static)
interface OrderTemplateAssets {
  header_banner: string;
  logo_path: string;
  stadium_image?: string;
  stadium_photo_path?: string;
  hotel_image?: string;
  hotel_image_path?: string;
  hotel_image_2?: string;
  payment_banner_url?: string;
}
```

---

## 5. דוגמת JSON מלא (עם שדות תמונות – טשטוש)

ב־production התמונות מומרות ל־data URI; כאן מופיעים כ־URLs/מצייני מקום.

```json
{
  "order_number": "TT-20260205-1E2535C6",
  "created_at": "05/02/2026",
  "product_type": "package",
  "event_name": "דורטמונד נגד אטאלנטה",
  "event_type": "כדורגל",
  "event_date": "17/02/2026 21:00",
  "event_date_str": "17/02/2026",
  "event_time_str": "21:00",
  "venue": "Signal Iduna Park",
  "event_city": "Dortmund",
  "customer_name": "י*** מ***",
  "customer_id": "123***",
  "customer_phone": "050-***",
  "customer_email": "y***@example.com",
  "ticket_description": "",
  "category": "פלטיניום",
  "currency": "EUR",
  "currency_symbol": "€",
  "price_per_ticket": 330,
  "total_euro": 5000,
  "total_nis": "18,650",
  "num_tickets": 2,
  "exchange_rate": 3.73,
  "passengers": [
    { "first_name": "Y***", "last_name": "B***", "passport": "32***", "birth_date": "15/03/1951", "ticket_type": "כרטיס רגיל" },
    { "first_name": "S***", "last_name": "B***", "passport": "35***", "birth_date": "06/02/1958", "ticket_type": "כרטיס רגיל" }
  ],
  "hotel_name": "Hotel Riu Plaza España",
  "hotel_nights": 3,
  "hotel_stars": "4 כוכבים",
  "hotel_meals": "ארוחת בוקר",
  "hotel_address": "Gran Vía, 84, Madrid",
  "hotel_website": "https://...",
  "hotel_rating": "4.4",
  "hotel_image_path": "/path/to/hotel_main.jpg",
  "hotel_image_path_2": "/path/to/hotel_second.jpg",
  "flight_details": "הלוך: TLV → MAD 19/02 16:05 | חזור: MAD → TLV 24/02 08:35",
  "flights": [
    { "direction": "הלוך", "from": "TLV", "to": "MAD", "date": "19/02", "time": "16:05", "flight_no": "UX1302", "airline": "Air Europa" },
    { "direction": "חזור", "from": "MAD", "to": "TLV", "date": "24/02", "time": "08:35", "flight_no": "UX1301", "airline": "Air Europa" }
  ],
  "transfers": true,
  "bag_trolley": true,
  "bag_checked": "ללא כבודה רשומה",
  "is_date_final": false,
  "seats_together": false,
  "saved_games": [
    {
      "display_text": "דורטמונד נגד אטאלנטה",
      "details": "Signal Iduna Park, Dortmund",
      "event_date": "17/02/2026",
      "event_time": "21:00",
      "venue": "Signal Iduna Park",
      "event_city": "Dortmund",
      "category": "פלטיניום",
      "num_tickets": 2,
      "stadium_map_path": "stadium_maps/dortmund.svg",
      "seatmap_image": "data:image/svg+xml;base64,..."
    },
    {
      "display_text": "Barcelona FC נגד ריאל מדריד",
      "event_date": "08/02/2026",
      "event_time": "16:15",
      "venue": "Camp Nou",
      "event_city": "Barcelona",
      "category": "VIP",
      "num_tickets": 2,
      "stadium_map_path": "stadium_maps/barcelona.jpg",
      "seatmap_image": "data:image/jpeg;base64,..."
    }
  ],
  "stadium_image_path": "stadium_maps/dortmund.svg",
  "stadium_photo_path": "attached_assets/atmosphere_xyz.jpg",
  "template_version": 2
}
```

- **header_banner:** לא חלק מה־JSON; בשרת נטען מ־`assets/header_banner.png` (או .jpg) ומועבר כ־data URI. ב־React: URL קבוע.
- **payment_banner:** לא דינמי; בתבנית: `assets/payment_banner.png`. ב־React: URL קבוע.

---

סיכום קצר ל־v0:

1. **תמונות מלון:** `hotel_image_path`, `hotel_image_path_2` – ב־backend מומרות ל־data URI; ב־React אפשר לקבל URLs או data URIs.
2. **תרשים אצטדיון לכל משחק:** בכל איבר ב־`saved_games`: `stadium_map_path` (מקור), ו־`seatmap_image` (data URI אחרי עיבוד). ב־React: להשתמש ב־`seatmap_image` אם קיים, אחרת ב־`stadium_map_path` כ־URL.
3. **באנר תחתון:** תמיד `assets/payment_banner.png` (או URL מלא לאותו קובץ) – לא שדה ב־order_data.

אם תרצה, אפשר להפוך את `INVOICE_ORDER_STRUCTURE.md` גם ל־JSON schema או ל־Zod/Yup מול ה־TypeScript ש־v0 ייצר.
