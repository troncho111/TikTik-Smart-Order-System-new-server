"""
Services - לוגיקה עסקית של המערכת
"""
from .auth_service import (
    generate_session_token,
    create_user_session,
    validate_session_token,
    delete_user_session,
    restore_session_from_token,
    set_session_token,
    clear_session_token
)

from .ai_service import (
    get_gemini_client,
    ai_chat_response
)

from .order_service import (
    save_order_to_db,
    update_order_status,
    delete_order,
    get_all_orders,
    get_status_badge
)

from .pdf_service import (
    generate_pdf
)

__all__ = [
    # Auth
    'generate_session_token',
    'create_user_session',
    'validate_session_token',
    'delete_user_session',
    'restore_session_from_token',
    'set_session_token',
    'clear_session_token',
    
    # AI
    'get_gemini_client',
    'ai_chat_response',
    
    # Orders
    'save_order_to_db',
    'update_order_status',
    'delete_order',
    'get_all_orders',
    'get_status_badge',
    
    # PDF
    'generate_pdf',
]
