# TikTik Smart Order System - Full Documentation

## Table of Contents
1. [Overview](#overview)
2. [File Structure](#file-structure)
3. [Database Models](#database-models)
4. [Main Application (app.py)](#main-application-apppy)
5. [PDF Generator](#pdf-generator)
6. [HTML Template](#html-template)
7. [Passport OCR](#passport-ocr)
8. [Terms & Conditions](#terms--conditions)
9. [Assets](#assets)
10. [Environment Variables](#environment-variables)
11. [Dependencies](#dependencies)

---

## Overview

**TikTik Smart Order System** is an automated order management system for TikTik, a sports events and concerts ticketing agency. The system replaces manual PowerPoint editing by generating professional PDF order confirmations through a Hebrew RTL (Right-to-Left) form interface.

### Key Features
- **Two Product Types**: 
  - Full Package (flight + hotel + tickets)
  - Tickets Only
- **Passport OCR**: Automatic extraction of passenger data from passport images using Google Gemini AI
- **Professional PDF Generation**: Magazine-style design with Hebrew RTL support using WeasyPrint
- **Email Integration**: Send PDFs directly to customers via Resend API
- **Order History**: Track all orders with status management
- **Excel Export**: Export orders to Excel reports

---

## File Structure

```
/
├── app.py                    # Main Streamlit application (1116 lines)
├── pdf_generator.py          # PDF generation using WeasyPrint (147 lines)
├── models.py                 # SQLAlchemy database models (129 lines)
├── passport_ocr.py           # Gemini AI passport scanning (103 lines)
├── terms.txt                 # Legal terms & conditions (Hebrew, 142 lines)
├── replit.md                 # Project documentation
├── DOCUMENTATION.md          # This file
├── templates/
│   └── order_template.html   # Jinja2 HTML template for PDF (657 lines)
├── assets/
│   ├── header_banner.png     # TikTik banner image
│   ├── header_banner.jpg     # TikTik banner (alternate)
│   ├── cover_page.jpg        # Cover page image
│   └── concert_bg.jpg        # Concert background
├── attached_assets/
│   └── stock_images/         # Sample images for testing
└── .streamlit/
    └── config.toml           # Streamlit configuration
```

---

## Database Models

### File: `models.py`

#### OrderStatus Enum
```python
class OrderStatus(enum.Enum):
    DRAFT = "draft"        # טיוטה - Order created but not sent
    SENT = "sent"          # נשלח - Order sent to customer
    VIEWED = "viewed"      # נצפה - Customer viewed the order
    SIGNED = "signed"      # נחתם - Customer signed the order
    CANCELLED = "cancelled" # בוטל - Order cancelled
```

#### EventType Enum
```python
class EventType(enum.Enum):
    FOOTBALL = "football"  # כדורגל
    CONCERT = "concert"    # קונצרט
    OTHER = "other"        # אחר
```

#### Order Model
```python
class Order(Base):
    __tablename__ = "orders"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)  # Format: TT-YYYYMMDD-XXXXXXXX
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Event Details
    event_name = Column(String(255), nullable=False)
    event_date = Column(String(100))
    event_time = Column(String(50))
    venue = Column(String(255))
    event_type = Column(SQLEnum(EventType), default=EventType.FOOTBALL)
    
    # Customer Details
    customer_name = Column(String(255), nullable=False)
    customer_id = Column(String(50))          # Israeli ID
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    
    # Ticket Details
    ticket_description = Column(Text)
    block = Column(String(50))                # Category (CAT 1, VIP, etc.)
    row = Column(String(50))
    seats = Column(String(100))
    num_tickets = Column(Integer, default=1)
    price_per_ticket_euro = Column(Float, default=0)
    exchange_rate = Column(Float, default=3.78)
    total_euro = Column(Float, default=0)
    total_nis = Column(Float, default=0)
    
    # Passengers (JSON string)
    passengers = Column(Text)  # JSON: [{"first_name": "", "last_name": "", "passport": "", ...}]
    
    # Status Tracking
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.DRAFT)
    sent_at = Column(DateTime, nullable=True)
    viewed_at = Column(DateTime, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    
    # Signature
    signature_token = Column(String(100), unique=True, nullable=True)
    signature_image = Column(Text, nullable=True)  # Base64 encoded image
    
    # PDF Storage
    pdf_path = Column(String(500), nullable=True)
    
    # Notes
    notes = Column(Text, nullable=True)
```

#### EventTemplate Model (Future Use)
```python
class EventTemplate(Base):
    __tablename__ = "event_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    event_type = Column(SQLEnum(EventType), default=EventType.FOOTBALL)
    default_venue = Column(String(255))
    default_notes = Column(Text)
    stadium_image_path = Column(String(500))
    map_image_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
```

#### Helper Functions
```python
def init_db():
    """Initialize database tables - creates all tables if they don't exist"""
    if engine:
        Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session with timeout handling"""
    if SessionLocal:
        try:
            db = SessionLocal()
            db.execute("SELECT 1")  # Test connection
            return db
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
    return None

def generate_order_number():
    """Generate unique order number: TT-YYYYMMDD-XXXXXXXX"""
    import uuid
    now = datetime.now()
    short_uuid = str(uuid.uuid4())[:8].upper()
    return f"TT-{now.strftime('%Y%m%d')}-{short_uuid}"
```

---

## Main Application (app.py)

The main Streamlit application with three pages and sidebar navigation.

### Application Structure

```python
# Initialize database
init_db()

# Configure Streamlit
st.set_page_config(
    page_title="TikTik Smart Order System",
    page_icon="🎟️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply RTL CSS
st.markdown(RTL_CSS, unsafe_allow_html=True)

# Sidebar navigation
page = st.sidebar.radio("ניווט", ["הזמנה חדשה", "היסטוריית הזמנות", "ייצוא דוחות"])

if page == "הזמנה חדשה":
    page_new_order()
elif page == "היסטוריית הזמנות":
    page_order_history()
else:
    page_export()
```

### Page 1: New Order (`page_new_order()`)

**Form Sections:**

1. **Product Type Selection**
```python
product_type = st.radio(
    "בחר סוג מוצר",
    options=["tickets", "package"],
    format_func=lambda x: "🎫 כרטיסים בלבד" if x == "tickets" else "✈️ חבילה מלאה"
)
```

2. **Event Details**
- Event type (כדורגל/קונצרט/אחר)
- Event name
- Date and time
- Venue
- Stadium image upload

3. **Hotel Details (Package only)**
- Hotel name
- Number of nights
- Star rating (3/4/5)
- Meals (none/breakfast/half-board/full-board)
- Flight details textarea
- Transfers checkbox
- Hotel images (2)

4. **Customer Details**
- Full name
- Israeli ID
- Phone
- Email

5. **Ticket Details**
- Description
- Category (CAT 1/VIP/Premium)
- Price per ticket (EUR)
- Quantity
- Exchange rate

6. **Passengers Section**
- Passport OCR upload (multiple files)
- Dynamic passenger list with:
  - First name, Last name
  - Ticket type
  - Passport number
  - Birth date
  - Passport expiry

**Key Functions:**

```python
def generate_pdf(order_data, stadium_image=None, hotel_image=None, hotel_image_2=None):
    """Generate PDF using subprocess to avoid blocking Streamlit"""
    import subprocess
    
    # Save images to temp files
    if stadium_image:
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            stadium_image.save(tmp.name)
            stadium_image_path = tmp.name
    
    # Prepare JSON data
    pdf_data = {
        'product_type': order_data.get('product_type', 'tickets'),
        'event_name': order_data['event_name'],
        # ... all other fields
    }
    
    # Write to temp JSON file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as jf:
        json.dump(pdf_data, jf)
        json_file = jf.name
    
    # Run pdf_generator.py as subprocess
    result = subprocess.run(
        ['python3', 'pdf_generator.py', json_file],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    # Decode base64 result
    pdf_bytes = base64.b64decode(result.stdout.strip())
    return pdf_bytes

def save_order_to_db(order_data, pdf_bytes=None):
    """Save order to PostgreSQL database"""
    db = get_db()
    order = Order(
        order_number=order_data.get('order_number') or generate_order_number(),
        event_name=order_data['event_name'],
        # ... all fields
        passengers=json.dumps(order_data.get('passengers', []), ensure_ascii=False),
        status=OrderStatus.DRAFT
    )
    db.add(order)
    db.commit()
    return order

def update_order_status(order_id, new_status):
    """Update order status with timestamp"""
    order = db.query(Order).filter(Order.id == order_id).first()
    order.status = new_status
    if new_status == OrderStatus.SENT:
        order.sent_at = datetime.utcnow()
    # ...
```

### Page 2: Order History (`page_order_history()`)

```python
def page_order_history():
    # Search and filter
    search_query = st.text_input("🔍 חיפוש")
    status_filter = st.selectbox("סינון לפי סטטוס", 
        ["הכל", "טיוטה", "נשלח", "נצפה", "נחתם", "בוטל"])
    
    # Get filtered orders
    orders = get_all_orders(search_query, status_filter)
    
    # Display order cards
    for order in orders:
        st.markdown(f"""
        <div class="order-card">
            <h4>{order.order_number}</h4>
            <p>{order.event_name}</p>
            <p>{order.customer_name}</p>
            {get_status_badge(order.status)}
            <p>{order.total_euro}€ = {order.total_nis}₪</p>
        </div>
        """)
```

### Page 3: Export (`page_export()`)

```python
def page_export():
    # Date range
    start_date = st.date_input("מתאריך")
    end_date = st.date_input("עד תאריך")
    
    # Status filter
    status_filter = st.multiselect("סינון לפי סטטוס", [...])
    
    if st.button("📥 ייצא ל-Excel"):
        # Query orders
        orders = db.query(Order).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        ).all()
        
        # Create Excel with openpyxl
        wb = openpyxl.Workbook()
        ws = wb.active
        # ... add headers and data
        
        # Download
        st.download_button(data=excel_bytes, file_name="orders.xlsx")
```

### RTL CSS Styling

```css
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap');

* { font-family: 'Heebo', sans-serif !important; }

.main .block-container {
    direction: rtl;
    text-align: right;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 10px;
}

.form-section {
    background: #1e1e2e;
    padding: 1.5rem;
    border-radius: 15px;
    border: 1px solid #333;
}

.price-display {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    padding: 1.5rem;
    border-radius: 12px;
    text-align: center;
    color: white;
}

.status-badge {
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
}
.status-draft { background: #6c757d; }
.status-sent { background: #007bff; }
.status-viewed { background: #ffc107; }
.status-signed { background: #28a745; }
.status-cancelled { background: #dc3545; }
```

---

## PDF Generator

### File: `pdf_generator.py`

Uses **WeasyPrint** and **Jinja2** to generate professional PDFs.

```python
#!/usr/bin/env python3
"""
PDF Generator using WeasyPrint and Jinja2 templates.
Generates professional Hebrew RTL PDF documents for TikTik orders.
"""

from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML

def get_image_data_uri(image_path: str) -> str:
    """Convert image file to base64 data URI for embedding in HTML"""
    if not image_path or not os.path.exists(image_path):
        return ""
    
    ext = os.path.splitext(image_path)[1].lower()
    mime_types = {
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
        '.gif': 'image/gif',
    }
    mime_type = mime_types.get(ext, 'image/jpeg')
    
    with open(image_path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('utf-8')
    
    return f"data:{mime_type};base64,{data}"

def generate_pdf(order_data: dict, stadium_image_path: str = None, hotel_image_path: str = None) -> bytes:
    """
    Generate a professional PDF using HTML template and WeasyPrint.
    
    Args:
        order_data: Dictionary containing order details
        stadium_image_path: Optional path to stadium image
        hotel_image_path: Optional path to hotel image
    
    Returns:
        PDF file as bytes
    """
    # Load Jinja2 template
    template_dir = Path(__file__).parent / 'templates'
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template('order_template.html')
    
    # Load brand assets
    header_banner = get_image_data_uri(str(project_root / 'assets' / 'header_banner.png'))
    
    # Convert images to data URIs
    stadium_image_uri = get_image_data_uri(stadium_image_path) if stadium_image_path else None
    hotel_image_uri = get_image_data_uri(hotel_image_path) if hotel_image_path else None
    
    # Load terms
    terms_path = project_root / 'terms.txt'
    if terms_path.exists():
        with open(terms_path, 'r', encoding='utf-8') as f:
            terms_text = f.read().replace('\n', '<br>')
    
    # Prepare template data
    template_data = {
        'product_type': order_data.get('product_type', 'tickets'),
        'event_name': order_data.get('event_name', ''),
        'event_date': order_data.get('event_date', ''),
        # ... all fields
        'stadium_image': stadium_image_uri,
        'hotel_image': hotel_image_uri,
        'header_banner': header_banner,
        'terms_text': terms_text,
    }
    
    # Render HTML
    html_content = template.render(**template_data)
    
    # Convert to PDF
    html_doc = HTML(string=html_content, base_url=str(Path(__file__).parent))
    pdf_bytes = html_doc.write_pdf()
    
    return pdf_bytes

# CLI entry point
if __name__ == '__main__':
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        order_data = json.load(f)
    
    pdf_bytes = generate_pdf(
        order_data, 
        order_data.get('stadium_image_path'),
        order_data.get('hotel_image_path')
    )
    print(base64.b64encode(pdf_bytes).decode('utf-8'))
```

---

## HTML Template

### File: `templates/order_template.html`

A 3-page PDF template with professional magazine-style design.

### Page Structure

```html
<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <meta charset="UTF-8">
    <style>
        @page { size: A4; margin: 0; }
        body { font-family: 'Arial', sans-serif; }
        .page { width: 210mm; min-height: 297mm; }
        .page-break { page-break-before: always; }
        /* ... all styles */
    </style>
</head>
<body>
    <!-- PAGE 1: Order Summary -->
    <div class="page">
        <div class="header-bar">...</div>
        <div class="order-title">...</div>
        <div class="content">
            <div class="event-card">...</div>
            <div class="hotel-card">...</div>
            <div class="summary-card">...</div>
            <div class="signatures">...</div>
        </div>
    </div>
    
    <!-- PAGE 2: Passenger Details -->
    <div class="page page-break">...</div>
    
    <!-- PAGE 3: Terms -->
    <div class="page page-break">...</div>
</body>
</html>
```

### Event Card - Two Column Layout

```html
<div class="event-card">
    <div class="event-content">
        <!-- RIGHT: Event Info -->
        <div class="event-info">
            <div class="event-logos">
                <div class="team-logo">📱</div>
                <div class="vs-text">VS</div>
                <div class="team-logo">📱</div>
            </div>
            <div class="event-name">{{ event_name }}</div>
            <div class="event-details">
                <div class="detail-row">
                    <span>{{ event_date }}</span>
                    <span class="detail-icon">📅</span>
                </div>
                <div class="detail-row">
                    <span>20:00</span>
                    <span class="detail-icon">🕐</span>
                </div>
                <div class="detail-row">
                    <span>{{ venue }}</span>
                    <span class="detail-icon">📍</span>
                </div>
                <div class="detail-row">
                    <span>{{ num_tickets }} כרטיסים - {{ category }}</span>
                    <span class="detail-icon">🎫</span>
                </div>
            </div>
            <div class="final-date">התאריך הינו סופי</div>
        </div>
        
        <!-- LEFT: Stadium Map -->
        <div class="event-map">
            {% if stadium_image %}
            <img src="{{ stadium_image }}" alt="מפת האצטדיון">
            {% else %}
            <div style="font-size: 60pt; color: #ccc;">🏟️</div>
            {% endif %}
        </div>
    </div>
</div>
```

### Key CSS Classes

```css
/* Two-column parallel alignment */
.event-content {
    display: flex;
    align-items: stretch;  /* Makes both columns same height */
}

.event-info {
    flex: 1;
    padding: 25px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    border-left: 1px solid #eee;
}

.event-map {
    flex: 1;
    background: #fafafa;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 280px;
}

/* Image handling - no cropping */
.event-map img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    padding: 10px;
}

/* Header bar */
.header-bar {
    background: #0047AB;
    color: white;
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
}

/* Section titles with red border */
.section-title {
    font-size: 14pt;
    font-weight: bold;
    color: #0047AB;
    border-right: 4px solid #c41e3a;
    padding-right: 12px;
}

/* Total bar */
.total-bar {
    background: #0047AB;
    color: white;
    padding: 12px 20px;
    text-align: center;
    font-size: 14pt;
    font-weight: bold;
}

/* Terms - 3 columns */
.terms-content {
    column-count: 3;
    column-gap: 20px;
    font-size: 7pt;
}
```

### Jinja2 Conditionals

```html
<!-- Product type conditional -->
{% if product_type == 'package' %}
    <div class="hotel-card">...</div>
    <div class="flights-card">...</div>
{% endif %}

<!-- Passenger handling (dict or string) -->
{% for passenger in passengers %}
    {% if passenger is mapping %}
        <td>{{ passenger.get('first_name', '') }} {{ passenger.get('last_name', '') }}</td>
        <td>{{ passenger.get('passport', '—') }}</td>
    {% else %}
        <td>{{ passenger }}</td>
    {% endif %}
{% endfor %}

<!-- Transfers conditional -->
<span>{% if transfers %}העברות כלול{% else %}ללא העברות{% endif %}</span>

<!-- Flight icon conditional -->
<span class="flight-icon">{% if 'הלוך' in line %}🛫{% else %}🛬{% endif %}</span>
```

---

## Passport OCR

### File: `passport_ocr.py`

Uses **Google Gemini AI** (via Replit AI Integrations) to extract passport data from images.

```python
"""
Passport OCR using Gemini AI
Extracts passenger details from passport images
"""

from google import genai
from google.genai import types

# Replit AI Integrations - auto-configured
AI_INTEGRATIONS_GEMINI_API_KEY = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY")
AI_INTEGRATIONS_GEMINI_BASE_URL = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")

client = genai.Client(
    api_key=AI_INTEGRATIONS_GEMINI_API_KEY,
    http_options={
        'api_version': '',
        'base_url': AI_INTEGRATIONS_GEMINI_BASE_URL   
    }
)

def extract_passport_data(image_bytes: bytes) -> dict:
    """
    Extract passport information from an image using Gemini Vision.
    
    Args:
        image_bytes: The passport image as bytes
        
    Returns:
        Dictionary with extracted fields:
        - first_name: First/given name
        - last_name: Surname/family name
        - passport_number: Passport number
        - birth_date: Date of birth (DD/MM/YYYY)
        - passport_expiry: Passport expiry date (DD/MM/YYYY)
        - success: Boolean indicating success
        - error: Error message if failed
    """
    try:
        prompt = """Analyze this passport image and extract the following information.
Return ONLY a valid JSON object with these exact keys (no markdown, no explanation):
{
    "first_name": "the given/first name exactly as shown",
    "last_name": "the surname/family name exactly as shown", 
    "passport_number": "the passport number",
    "birth_date": "date of birth in DD/MM/YYYY format",
    "passport_expiry": "passport expiry date in DD/MM/YYYY format"
}

If any field cannot be found, use an empty string for that field.
Return ONLY the JSON object, nothing else."""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                prompt,
                types.Part(
                    inline_data=types.Blob(
                        mime_type="image/jpeg",
                        data=image_bytes
                    )
                )
            ]
        )
        
        result_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if result_text.startswith("```"):
            lines = result_text.split('\n')
            result_text = '\n'.join(lines[1:-1])
        
        data = json.loads(result_text)
        
        return {
            "first_name": data.get("first_name", ""),
            "last_name": data.get("last_name", ""),
            "passport_number": data.get("passport_number", ""),
            "birth_date": data.get("birth_date", ""),
            "passport_expiry": data.get("passport_expiry", ""),
            "success": True,
            "error": None
        }
        
    except json.JSONDecodeError as e:
        return {"success": False, "error": f"Could not parse response: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
```

**Usage in app.py:**

```python
# User uploads passport images
passport_uploads = st.file_uploader(
    "📷 העלה תמונות דרכונים",
    type=['png', 'jpg', 'jpeg'],
    accept_multiple_files=True
)

if st.button("🔍 סרוק דרכונים") and passport_uploads:
    for passport_file in passport_uploads:
        image_bytes = passport_file.read()
        result = extract_passport_data(image_bytes)
        
        if result.get('success'):
            st.session_state.passenger_list.append({
                'first_name': result['first_name'],
                'last_name': result['last_name'],
                'passport': result['passport_number'],
                'birth_date': result['birth_date'],
                'passport_expiry': result['passport_expiry'],
                'ticket_type': 'כרטיס רגיל'
            })
```

---

## Terms & Conditions

### File: `terms.txt`

Full Hebrew legal text (142 lines) including:

1. **תנאי הרכישה** - Purchase conditions
2. **זמני אספקת הכרטיסים** - Ticket delivery policy
3. **שימוש בכרטיס** - Stadium behavior rules
4. **אופן ההושבה** - Seating arrangements
5. **סידורי לינה** - Hotel accommodations
6. **אחריות טיקטיק** - TikTik responsibilities
7. **נהלי ביטול** - Cancellation policy (100% non-refundable)
8. **אמצעי תשלום** - Payment methods
9. **הגנת פרטיות** - Privacy policy
10. **הדין וסמכות השיפוט** - Jurisdiction (Israeli law, Tel Aviv courts)

---

## Assets

### Directory: `assets/`

| File | Dimensions | Usage |
|------|------------|-------|
| `header_banner.png` | Wide banner | Gallery section, PDF header |
| `header_banner.jpg` | Alternate | Fallback format |
| `cover_page.jpg` | A4 | Cover page (optional) |
| `concert_bg.jpg` | Landscape | Concert events background |

---

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `RESEND_API_KEY` | Resend.com API key for emails | Optional |
| `AI_INTEGRATIONS_GEMINI_API_KEY` | Gemini AI key (auto-provided by Replit) | Auto |
| `AI_INTEGRATIONS_GEMINI_BASE_URL` | Gemini API base URL (auto-provided) | Auto |
| `SESSION_SECRET` | Session encryption key | Yes |

---

## Dependencies

### Python Packages

```
streamlit              # Web UI framework
weasyprint             # HTML to PDF conversion
jinja2                 # HTML templating
google-genai           # Google Gemini AI SDK
fpdf2                  # PDF generation (legacy)
arabic-reshaper        # Arabic/Hebrew text shaping
python-bidi            # Bidirectional text (RTL)
pillow                 # Image processing
resend                 # Email sending API
streamlit-drawable-canvas  # Digital signature
sqlalchemy             # Database ORM
psycopg2-binary        # PostgreSQL driver
openpyxl               # Excel file generation
```

---

## Passenger Data Structure

Passengers stored as JSON in database:

```json
[
    {
        "first_name": "Israel",
        "last_name": "Israeli",
        "passport": "12345678",
        "birth_date": "15/03/1985",
        "passport_expiry": "20/05/2030",
        "ticket_type": "כרטיס רגיל"
    }
]
```

**Ticket Types:**
- `כרטיס רגיל` (Regular)
- `כרטיס VIP`
- `כרטיס ילד` (Child)
- `כרטיס מלווה` (Companion)

---

## Order Number Format

```
TT-YYYYMMDD-XXXXXXXX

TT         = TikTik prefix
YYYYMMDD   = Date (e.g., 20241212)
XXXXXXXX   = 8-character UUID suffix (uppercase)

Example: TT-20241212-AB4C1096
```

---

## Email Integration (Resend)

```python
import resend

resend.api_key = os.environ.get('RESEND_API_KEY')

resend.Emails.send({
    "from": "TikTik <orders@tiktik.co.il>",
    "to": [customer_email],
    "subject": f"הצעת מחיר - {event_name}",
    "text": email_body,
    "attachments": [{
        "filename": f"הזמנה_{customer_name}_{date}.pdf",
        "content": base64.b64encode(pdf_bytes).decode()
    }]
})
```

---

## Running the Application

```bash
streamlit run app.py --server.port 5000
```

Application available at `http://localhost:5000`

---

## Session State Keys

| Key | Type | Description |
|-----|------|-------------|
| `passenger_list` | list[dict] | List of passenger dictionaries |
| `pdf_bytes` | bytes | Generated PDF bytes |
| `order_generated` | bool | PDF generation flag |
| `current_order_number` | str | Current order number |
| `current_order_id` | int | Database order ID |
| `random_data` | dict | Test data for random fill |
| `first_name_{i}` | str | Passenger first name |
| `last_name_{i}` | str | Passenger last name |
| `passport_{i}` | str | Passport number |
| `birth_date_{i}` | str | Birth date |
| `passport_expiry_{i}` | str | Passport expiry |

---

## Contact

**TikTik Sports & Events**
- Phone: 073-272-6000
- Emergency: 972-732726000
- Email: infogroup@tiktik.co.il
- Website: www.tiktik.co.il
- Address: Bar Ilan University, Building 107, Ramat Gan

---

*Documentation generated: December 2024*
