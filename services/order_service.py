"""
Order Service - TikTik Smart Order System
שירות ניהול הזמנות
"""

import json
import uuid
import streamlit as st
from datetime import datetime
from models import (
    Order, OrderStatus, get_db, generate_order_number
)
from ui_helpers import get_event_type_from_hebrew


def save_order_to_db(order_data, pdf_bytes=None):
    """Save order to database"""
    db = get_db()
    if not db:
        return None
    
    try:
        event_type = get_event_type_from_hebrew(order_data.get('event_type', 'אחר'))
        
        user_id = None
        if st.session_state.get('user'):
            user_id = st.session_state.user.get('id')
        
        order = Order(
            order_number=order_data.get('order_number') or generate_order_number(),
            user_id=user_id,
            event_name=order_data['event_name'],
            event_date=order_data.get('event_date_str', ''),
            event_time=order_data.get('event_time_str', ''),
            venue=order_data.get('venue', ''),
            event_type=event_type,
            customer_name=order_data['customer_name'],
            customer_id=order_data.get('customer_id', ''),
            customer_email=order_data.get('customer_email', ''),
            customer_phone=order_data.get('customer_phone', ''),
            ticket_description=order_data.get('ticket_description', ''),
            block=order_data.get('category', ''),
            row='',
            seats='',
            num_tickets=order_data.get('num_tickets', 1),
            price_per_ticket_euro=order_data.get('price_per_ticket', 0),
            exchange_rate=order_data.get('exchange_rate', 3.78),
            total_euro=order_data.get('total_euro', 0),
            total_nis=order_data.get('total_nis', 0),
            passengers=json.dumps(order_data.get('passengers', []), ensure_ascii=False),
            status=OrderStatus.DRAFT,
            signature_token=str(uuid.uuid4())
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        return order
    except Exception as e:
        db.rollback()
        st.error(f"שגיאה בשמירת ההזמנה: {str(e)}")
        return None
    finally:
        db.close()


def update_order_status(order_id, new_status):
    """Update order status"""
    db = get_db()
    if not db:
        return False
    
    try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if order:
            order.status = new_status
            if new_status == OrderStatus.SENT:
                order.sent_at = datetime.utcnow()
            elif new_status == OrderStatus.VIEWED:
                order.viewed_at = datetime.utcnow()
            elif new_status == OrderStatus.SIGNED:
                order.signed_at = datetime.utcnow()
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        return False
    finally:
        db.close()


def delete_order(order_id):
    """Delete an order permanently"""
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
        return False
    finally:
        db.close()


def get_all_orders(search_query=None, status_filter=None, user_id=None, is_admin=False):
    """Get all orders with optional filtering"""
    db = get_db()
    if not db:
        return []
    
    try:
        query = db.query(Order).order_by(Order.created_at.desc())
        
        if not is_admin and user_id:
            query = query.filter(Order.user_id == user_id)
        
        if search_query:
            search = f"%{search_query}%"
            query = query.filter(
                (Order.customer_name.ilike(search)) |
                (Order.event_name.ilike(search)) |
                (Order.order_number.ilike(search)) |
                (Order.customer_email.ilike(search))
            )
        
        if status_filter and status_filter != "הכל":
            status_map = {
                "טיוטה": OrderStatus.DRAFT,
                "נשלח": OrderStatus.SENT,
                "נצפה": OrderStatus.VIEWED,
                "נחתם": OrderStatus.SIGNED,
                "בוטל": OrderStatus.CANCELLED
            }
            if status_filter in status_map:
                query = query.filter(Order.status == status_map[status_filter])
        
        return query.all()
    except Exception as e:
        return []
    finally:
        db.close()
