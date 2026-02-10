"""
Concert Service - TikTik Smart Order System
שירות ניהול הופעות ואמנים שמורים
"""

from models import SavedConcert, SavedArtist, get_db


def get_saved_concerts():
    """Get all saved concerts for quick reuse"""
    db = get_db()
    if not db:
        return []
    
    try:
        concerts = db.query(SavedConcert).filter(SavedConcert.is_active == True).order_by(SavedConcert.created_at.desc()).all()
        return [c.to_dict() for c in concerts]
    except Exception as e:
        print(f"Error getting saved concerts: {e}")
        return []
    finally:
        db.close()


def save_concert_to_favorites(artist_name, artist_name_he, venue_name, city, country, event_date=None, event_time=None, event_url=None, category=None, event_name=None, source=None, stadium_map_path=None, stadium_map_data=None, stadium_map_mime=None):
    """Save a manually entered concert to favorites for quick reuse"""
    db = get_db()
    if not db:
        return False
    
    try:
        existing = db.query(SavedConcert).filter(
            SavedConcert.artist_name == artist_name,
            SavedConcert.venue_name == venue_name,
            SavedConcert.is_active == True
        ).first()
        
        if existing:
            existing.city = city
            existing.country = country
            existing.event_date = event_date
            existing.event_time = event_time
            existing.event_url = event_url
            existing.category = category
            existing.event_name = event_name
            existing.source = source or 'saved'
            if stadium_map_path:
                existing.stadium_map_path = stadium_map_path
            if stadium_map_data:
                existing.stadium_map_data = stadium_map_data
                existing.stadium_map_mime = stadium_map_mime or 'image/png'
        else:
            new_concert = SavedConcert(
                artist_name=artist_name,
                artist_name_he=artist_name_he,
                event_name=event_name,
                venue_name=venue_name,
                city=city,
                country=country,
                event_date=event_date,
                event_time=event_time,
                event_url=event_url,
                category=category,
                source=source or 'saved',
                stadium_map_path=stadium_map_path,
                stadium_map_data=stadium_map_data,
                stadium_map_mime=stadium_map_mime or 'image/png' if stadium_map_data else None
            )
            db.add(new_concert)
        
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving concert: {e}")
        return False
    finally:
        db.close()


def delete_saved_concert(concert_id):
    """Delete a saved concert"""
    db = get_db()
    if not db:
        return False
    
    try:
        concert = db.query(SavedConcert).filter(SavedConcert.id == concert_id).first()
        if concert:
            concert.is_active = False
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()


def get_saved_artists():
    """Get all saved artists for the dropdown"""
    db = get_db()
    if not db:
        return []
    
    try:
        artists = db.query(SavedArtist).filter(SavedArtist.is_active == True).order_by(SavedArtist.name_en).all()
        return [a.to_dict() for a in artists]
    except Exception as e:
        print(f"Error getting saved artists: {e}")
        return []
    finally:
        db.close()


def save_artist_to_favorites(name_en, name_he=None, ticketmaster_id=None, genre=None, image_url=None):
    """Save an artist to favorites for quick access in dropdown"""
    db = get_db()
    if not db:
        return False
    
    try:
        existing = db.query(SavedArtist).filter(
            SavedArtist.name_en == name_en,
            SavedArtist.is_active == True
        ).first()
        
        if existing:
            return True
        
        new_artist = SavedArtist(
            name_en=name_en,
            name_he=name_he or name_en,
            ticketmaster_id=ticketmaster_id,
            genre=genre,
            image_url=image_url
        )
        db.add(new_artist)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        print(f"Error saving artist: {e}")
        return False
    finally:
        db.close()


def delete_saved_artist(artist_id):
    """Delete a saved artist"""
    db = get_db()
    if not db:
        return False
    
    try:
        artist = db.query(SavedArtist).filter(SavedArtist.id == artist_id).first()
        if artist:
            artist.is_active = False
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()
