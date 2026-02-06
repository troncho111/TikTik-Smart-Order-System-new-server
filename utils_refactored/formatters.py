"""
Formatters - פונקציות עיצוב טקסט ומספרים
"""
from datetime import datetime


def format_price(price):
    """
    עיצוב מחיר
    
    Args:
        price: מחיר (int או float)
        
    Returns:
        str: מחיר מעוצב (לדוגמה: "12,500 ₪")
    """
    if price is None:
        return "0 ₪"
    return f"{price:,} ₪".replace(',', ',')


def format_date(date_obj, format_str="%d/%m/%Y"):
    """
    עיצוב תאריך
    
    Args:
        date_obj: אובייקט datetime או date
        format_str: פורמט התאריך
        
    Returns:
        str: תאריך מעוצב
    """
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime(format_str)


def format_phone(phone):
    """
    עיצוב מספר טלפון
    
    Args:
        phone: מספר טלפון
        
    Returns:
        str: מספר מעוצב
    """
    if not phone:
        return ""
    # הסרת תווים לא רצויים
    phone = ''.join(filter(str.isdigit, str(phone)))
    
    # פורמט ישראלי: 050-123-4567
    if len(phone) == 10 and phone.startswith('0'):
        return f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
    
    return phone


def format_order_number(order_num):
    """
    עיצוב מספר הזמנה
    
    Args:
        order_num: מספר הזמנה
        
    Returns:
        str: מספר מעוצב (לדוגמה: "TT-2026-001")
    """
    if not order_num:
        return ""
    return str(order_num).upper()


def truncate_text(text, max_length=50):
    """
    קיצור טקסט
    
    Args:
        text: טקסט
        max_length: אורך מקסימלי
        
    Returns:
        str: טקסט מקוצר
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
