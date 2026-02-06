"""
Order Service - ניהול הזמנות
"""
from datetime import datetime
from models import Order, OrderStatus, get_db, generate_order_number


def save_order_to_db(order_data, pdf_bytes=None):
    """
    שמירת הזמנה למסד הנתונים
    
    Args:
        order_data: נתוני ההזמנה
        pdf_bytes: bytes של קובץ PDF (אופציונלי)
        
    Returns:
        Order: אובייקט ההזמנה שנשמר
    """
    db = get_db()
    if not db:
        return None
    
    try:
        order = Order(
            order_number=generate_order_number(),
            customer_name=order_data.get('customer_name'),
            customer_email=order_data.get('customer_email'),
            customer_phone=order_data.get('customer_phone'),
            event_type=order_data.get('event_type'),
            event_name=order_data.get('event_name'),
            event_date=order_data.get('event_date'),
            event_location=order_data.get('event_location'),
            package_type=order_data.get('package_type'),
            num_tickets=order_data.get('num_tickets', 0),
            hotel_name=order_data.get('hotel_name'),
            hotel_nights=order_data.get('hotel_nights', 0),
            flight_details=order_data.get('flight_details'),
            total_price=order_data.get('total_price', 0),
            status=OrderStatus.DRAFT,
            pdf_data=pdf_bytes,
            created_by=order_data.get('created_by'),
            notes=order_data.get('notes')
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        print(f"Error saving order: {e}")
        return None
    finally:
        db.close()


def update_order_status(order_id, new_status):
    """
    עדכון סטטוס הזמנה
    
    Args:
        order_id: מזהה הזמנה
        new_status: סטטוס חדש
        
    Returns:
        bool: האם העדכון הצליח
    """
    db = get_db()
    if not db:
        return False
    
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = new_status
            order.updated_at = datetime.utcnow()
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error updating order status: {e}")
        return False
    finally:
        db.close()


def delete_order(order_id):
    """
    מחיקת הזמנה
    
    Args:
        order_id: מזהה הזמנה
        
    Returns:
        bool: האם המחיקה הצליחה
    """
    db = get_db()
    if not db:
        return False
    
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            db.delete(order)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        print(f"Error deleting order: {e}")
        return False
    finally:
        db.close()


def get_all_orders(search_query=None, status_filter=None, user_id=None, is_admin=False):
    """
    קבלת כל ההזמנות עם סינון
    
    Args:
        search_query: טקסט לחיפוש
        status_filter: סינון לפי סטטוס
        user_id: מזהה משתמש (אם לא admin)
        is_admin: האם המשתמש הוא admin
        
    Returns:
        list: רשימת הזמנות
    """
    db = get_db()
    if not db:
        return []
    
    try:
        query = db.query(Order)
        
        # אם לא admin, הצג רק הזמנות של המשתמש
        if not is_admin and user_id:
            query = query.filter(Order.created_by == user_id)
        
        # סינון לפי סטטוס
        if status_filter and status_filter != "הכל":
            query = query.filter(Order.status == status_filter)
        
        # חיפוש טקסט
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                (Order.order_number.ilike(search)) |
                (Order.customer_name.ilike(search)) |
                (Order.customer_email.ilike(search)) |
                (Order.event_name.ilike(search))
            )
        
        # מיון לפי תאריך יצירה (החדשים ראשון)
        orders = query.order_by(Order.created_at.desc()).all()
        return orders
    except Exception as e:
        print(f"Error getting orders: {e}")
        return []
    finally:
        db.close()


def get_status_badge(status):
    """
    קבלת badge HTML לסטטוס
    
    Args:
        status: סטטוס ההזמנה
        
    Returns:
        str: HTML של badge
    """
    status_colors = {
        OrderStatus.DRAFT: ("🟡", "#FFA500"),
        OrderStatus.PENDING: ("🔵", "#3498db"),
        OrderStatus.CONFIRMED: ("🟢", "#27ae60"),
        OrderStatus.CANCELLED: ("🔴", "#e74c3c"),
        OrderStatus.COMPLETED: ("✅", "#2ecc71")
    }
    
    emoji, color = status_colors.get(status, ("⚪", "#95a5a6"))
    status_text = status.value if hasattr(status, 'value') else str(status)
    
    return f'<span style="background-color: {color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em;">{emoji} {status_text}</span>'
