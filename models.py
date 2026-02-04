import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum, text, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import enum
import bcrypt

DATABASE_URL = os.environ.get('DATABASE_URL')

# Add connection timeout to prevent hanging
engine = None
SessionLocal = None
if DATABASE_URL:
    try:
        engine = create_engine(
            DATABASE_URL, 
            connect_args={'connect_timeout': 5},
            pool_pre_ping=True,
            pool_recycle=300
        )
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    except Exception as e:
        print(f"Database connection error: {e}")
        engine = None
        SessionLocal = None

Base = declarative_base()

class OrderStatus(enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    SIGNED = "signed"
    CANCELLED = "cancelled"

class EventType(enum.Enum):
    FOOTBALL = "football"
    CONCERT = "concert"
    OTHER = "other"

class UserSession(Base):
    __tablename__ = "user_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    token = Column(String(64), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    last_seen = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    orders = relationship("Order", back_populates="user")
    sessions = relationship("UserSession", back_populates="user")
    
    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def __repr__(self):
        return f"<User {self.username}>"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user = relationship("User", back_populates="orders")
    
    event_name = Column(String(255), nullable=False)
    event_date = Column(String(100))
    event_time = Column(String(50))
    venue = Column(String(255))
    event_type = Column(SQLEnum(EventType), default=EventType.FOOTBALL)
    
    customer_name = Column(String(255), nullable=False)
    customer_id = Column(String(50))
    customer_email = Column(String(255))
    customer_phone = Column(String(50))
    
    ticket_description = Column(Text)
    block = Column(String(500))
    row = Column(String(500))
    seats = Column(String(500))
    num_tickets = Column(Integer, default=1)
    price_per_ticket_euro = Column(Float, default=0)
    exchange_rate = Column(Float, default=3.78)
    total_euro = Column(Float, default=0)
    total_nis = Column(Float, default=0)
    
    passengers = Column(Text)
    
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.DRAFT)
    sent_at = Column(DateTime, nullable=True)
    viewed_at = Column(DateTime, nullable=True)
    signed_at = Column(DateTime, nullable=True)
    
    signature_token = Column(String(100), unique=True, nullable=True)
    signature_image = Column(Text, nullable=True)
    
    pdf_path = Column(String(500), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    def __repr__(self):
        return f"<Order {self.order_number}: {self.customer_name}>"

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
    
    def __repr__(self):
        return f"<Template {self.name}>"

class AtmosphereImage(Base):
    __tablename__ = "atmosphere_images"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    category = Column(SQLEnum(EventType), default=EventType.FOOTBALL)
    file_path = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<AtmosphereImage {self.filename} ({self.category.value})>"

class HotelCache(Base):
    """Cache for hotel search results to avoid repeated API calls"""
    __tablename__ = "hotel_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    search_query = Column(String(500), unique=True, index=True)
    hotel_name = Column(String(255))
    hotel_address = Column(String(500))
    hotel_website = Column(String(500))
    hotel_rating = Column(Float)
    hotel_image_path = Column(String(500))
    hotel_image_path_2 = Column(String(500))
    place_id = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<HotelCache {self.hotel_name}>"
    
    def to_dict(self):
        return {
            'hotel_name': self.hotel_name,
            'hotel_address': self.hotel_address,
            'hotel_website': self.hotel_website,
            'hotel_rating': self.hotel_rating,
            'hotel_image_path': self.hotel_image_path,
            'hotel_image_path_2': self.hotel_image_path_2
        }

class ConcertCache(Base):
    """Cache for concert search results to avoid repeated API calls - shared across all users"""
    __tablename__ = "concert_cache"
    
    id = Column(Integer, primary_key=True, index=True)
    cache_key = Column(String(500), unique=True, index=True)
    artist_id = Column(String(100), index=True)
    artist_name = Column(String(255))
    concerts_json = Column(Text)
    total_results = Column(Integer, default=0)
    source = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    
    def __repr__(self):
        return f"<ConcertCache {self.artist_name} ({self.total_results} concerts)>"

class SavedConcert(Base):
    """User-saved concerts for quick reuse - manually entered events saved as favorites"""
    __tablename__ = "saved_concerts"
    
    id = Column(Integer, primary_key=True, index=True)
    artist_name = Column(String(255), nullable=False)
    artist_name_he = Column(String(255))
    event_name = Column(String(500))
    venue_name = Column(String(255), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    event_date = Column(String(50))
    event_time = Column(String(20))
    event_url = Column(String(1000))
    category = Column(String(100))
    source = Column(String(100))
    stadium_map_path = Column(String(500))
    stadium_map_data = Column(LargeBinary, nullable=True)
    stadium_map_mime = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<SavedConcert {self.artist_name} @ {self.venue_name}>"
    
    def to_dict(self):
        import base64
        map_data_b64 = None
        if self.stadium_map_data:
            map_data_b64 = base64.b64encode(self.stadium_map_data).decode('utf-8')
        return {
            'id': self.id,
            'artist': self.artist_name,
            'artist_he': self.artist_name_he,
            'name': self.event_name,
            'venue': self.venue_name,
            'city': self.city,
            'country': self.country,
            'date': self.event_date,
            'time': self.event_time,
            'url': self.event_url,
            'category': self.category,
            'source': self.source or 'saved',
            'stadium_map_path': getattr(self, 'stadium_map_path', None),
            'stadium_map_data': map_data_b64,
            'stadium_map_mime': getattr(self, 'stadium_map_mime', None)
        }

class SavedArtist(Base):
    """User-saved artists for quick access in the main dropdown"""
    __tablename__ = "saved_artists"
    
    id = Column(Integer, primary_key=True, index=True)
    name_en = Column(String(255), nullable=False, unique=True)
    name_he = Column(String(255))
    ticketmaster_id = Column(String(100))
    genre = Column(String(100))
    image_url = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<SavedArtist {self.name_en}>"
    
    def to_dict(self):
        return {
            'id': self.ticketmaster_id or str(self.id),
            'name_en': self.name_en,
            'name_he': self.name_he or self.name_en,
            'genre': self.genre,
            'image_url': self.image_url,
            'db_id': self.id
        }

class PackageTemplate(Base):
    """Saved package templates for recurring events with same flights/hotels"""
    __tablename__ = "package_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    event_type = Column(SQLEnum(EventType), default=EventType.CONCERT)
    product_type = Column(String(50), default="full_package")
    
    event_name = Column(String(255))
    event_date = Column(String(100))
    event_time = Column(String(50))
    venue = Column(String(255))
    
    ticket_description = Column(Text)
    ticket_category = Column(String(100))
    price_per_ticket_euro = Column(Float, default=0)
    
    hotel_data = Column(Text)
    flight_data = Column(Text)
    
    package_price_euro = Column(Float, default=0)
    
    stadium_map_data = Column(LargeBinary, nullable=True)
    stadium_map_mime = Column(String(50), nullable=True)
    atmosphere_image_data = Column(LargeBinary, nullable=True)
    atmosphere_image_mime = Column(String(50), nullable=True)
    
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    def __repr__(self):
        return f"<PackageTemplate {self.name}>"
    
    def to_dict(self):
        import base64
        import json
        
        map_data_b64 = None
        if self.stadium_map_data:
            map_data_b64 = base64.b64encode(self.stadium_map_data).decode('utf-8')
        
        atmo_data_b64 = None
        if self.atmosphere_image_data:
            atmo_data_b64 = base64.b64encode(self.atmosphere_image_data).decode('utf-8')
        
        hotel = {}
        if self.hotel_data:
            try:
                hotel = json.loads(self.hotel_data)
            except:
                pass
        
        flights = {}
        if self.flight_data:
            try:
                flights = json.loads(self.flight_data)
            except:
                pass
        
        return {
            'id': self.id,
            'name': self.name,
            'event_type': self.event_type.value if self.event_type else 'concert',
            'product_type': self.product_type or 'full_package',
            'event_name': self.event_name,
            'event_date': self.event_date,
            'event_time': self.event_time,
            'venue': self.venue,
            'ticket_description': self.ticket_description,
            'ticket_category': self.ticket_category,
            'price_per_ticket_euro': self.price_per_ticket_euro or 0,
            'hotel': hotel,
            'flights': flights,
            'package_price_euro': self.package_price_euro or 0,
            'stadium_map_data': map_data_b64,
            'stadium_map_mime': self.stadium_map_mime,
            'atmosphere_image_data': atmo_data_b64,
            'atmosphere_image_mime': self.atmosphere_image_mime,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

def run_migrations():
    """Run manual migrations for columns that create_all doesn't add to existing tables"""
    if not engine:
        return
    try:
        with engine.connect() as conn:
            # Add stadium_map_path to saved_concerts if missing
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'saved_concerts' AND column_name = 'stadium_map_path'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE saved_concerts ADD COLUMN stadium_map_path VARCHAR(500)"))
                conn.commit()
                print("Added stadium_map_path column to saved_concerts")
            
            # Add stadium_map_data column if missing
            result = conn.execute(text("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'saved_concerts' AND column_name = 'stadium_map_data'
            """))
            if not result.fetchone():
                conn.execute(text("ALTER TABLE saved_concerts ADD COLUMN stadium_map_data BYTEA"))
                conn.execute(text("ALTER TABLE saved_concerts ADD COLUMN stadium_map_mime VARCHAR(50)"))
                conn.commit()
                print("Added stadium_map_data and stadium_map_mime columns to saved_concerts")
    except Exception as e:
        print(f"Migration check: {e}")

def migrate_file_maps_to_db():
    """One-time migration: convert file-based stadium maps to database storage"""
    db = get_db()
    if not db:
        return
    try:
        saved_concerts = db.query(SavedConcert).filter(
            SavedConcert.stadium_map_path.isnot(None),
            SavedConcert.stadium_map_data.is_(None)
        ).all()
        
        for concert in saved_concerts:
            if concert.stadium_map_path and os.path.exists(concert.stadium_map_path):
                try:
                    with open(concert.stadium_map_path, 'rb') as f:
                        image_data = f.read()
                    ext = concert.stadium_map_path.lower().split('.')[-1]
                    mime_map = {'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'gif': 'image/gif'}
                    mime_type = mime_map.get(ext, 'image/png')
                    
                    concert.stadium_map_data = image_data
                    concert.stadium_map_mime = mime_type
                    db.commit()
                    print(f"Migrated map for: {concert.artist_name} @ {concert.venue_name}")
                except Exception as e:
                    print(f"Failed to migrate map for {concert.artist_name}: {e}")
    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    if engine:
        Base.metadata.create_all(bind=engine)
        run_migrations()
        migrate_file_maps_to_db()
        create_default_admin()

def create_default_admin():
    """Create default admin user if not exists"""
    db = get_db()
    if not db:
        return
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@tiktik.co.il",
                full_name="מנהל ראשי",
                is_admin=True,
                is_active=True
            )
            admin.set_password("admin123")
            db.add(admin)
            db.commit()
            print("Default admin user created: admin / admin123")
    except Exception as e:
        db.rollback()
        print(f"Error creating default admin: {e}")
    finally:
        db.close()

def get_db():
    """Get database session with timeout handling"""
    if SessionLocal:
        try:
            db = SessionLocal()
            # Test the connection with a simple query
            db.execute(text("SELECT 1"))
            return db
        except Exception as e:
            print(f"Database connection failed: {e}")
            return None
    return None

def generate_order_number():
    """Generate unique order number with high entropy"""
    import uuid
    now = datetime.now()
    short_uuid = str(uuid.uuid4())[:8].upper()
    return f"TT-{now.strftime('%Y%m%d')}-{short_uuid}"
