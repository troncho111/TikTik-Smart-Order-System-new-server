"""
AI Service - TikTik Smart Order System
שירות AI Chatbot למערכת
"""

import os
import streamlit as st
from google import genai


def get_gemini_client():
    """Get Gemini client for AI chat"""
    api_key = os.environ.get("AI_INTEGRATIONS_GEMINI_API_KEY")
    base_url = os.environ.get("AI_INTEGRATIONS_GEMINI_BASE_URL")
    
    if not api_key:
        return None
    
    try:
        return genai.Client(
            api_key=api_key,
            http_options={
                'api_version': '',
                'base_url': base_url
            }
        )
    except Exception:
        return None


def ai_chat_response(question: str) -> str:
    """Generate AI response for user question about TikTik system"""
    client = get_gemini_client()
    if not client:
        return "שירות הצ'אט אינו זמין כרגע. פנה למנהל המערכת."
    
    system_prompt = """אתה עוזר וירטואלי של מערכת TikTik. ענה בעברית קצר וברור.

בעיות נפוצות ופתרונות:

❓ "העליתי דרכון ולא קורה כלום"
✅ תשובה: לאחר העלאת התמונה, חייבים ללחוץ על כפתור "🔍 סרוק דרכון"!

❓ "העליתי צילום טיסה ולא קורה כלום"  
✅ תשובה: לאחר העלאת התמונה, חייבים ללחוץ על כפתור "🔍 סרוק טיסה"!

❓ "איפה שער ההמרה?"
✅ תשובה: שער ההמרה מתעדכן אוטומטית (שער בנק ישראל + 5 אגורות). אין צורך להזין.

❓ "איך שולחים ללקוח?"
✅ תשובה: לחץ "צור PDF והורד", ושלח את הקובץ ללקוח דרך וואטסאפ.

מידע על המערכת:
- TikTik מוכרת כרטיסים למשחקי כדורגל והופעות באירופה
- "חבילה מלאה" = מלון + טיסות + העברות + כרטיסים
- "כרטיסים בלבד" = רק כרטיסים
- סריקת דרכון: העלה תמונה → לחץ "סרוק דרכון" → פרטים יתמלאו
- סריקת טיסה: העלה צילום מסך → לחץ "סרוק טיסה" → פרטים יתמלאו
- מלונות: הקלד שם → לחץ "חפש מלון" → פרטים יתמלאו
- מפות אצטדיון מופיעות אוטומטית לפי הקבוצה

ענה קצר וממוקד. אם לא יודע - הפנה לעמוד העזרה (כפתור ❓)."""
    
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=f"{system_prompt}\n\nשאלת המשתמש: {question}"
        )
        return response.text or "לא הצלחתי לענות. נסה שוב."
    except Exception as e:
        return f"שגיאה: לא הצלחתי לעבד את השאלה. נסה שוב מאוחר יותר."


def render_ai_chatbot():
    """Render AI chatbot widget in sidebar"""
    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 🤖 עוזר AI")
    
    if 'ai_chat_history' not in st.session_state:
        st.session_state.ai_chat_history = []
    
    if 'ai_chat_input' not in st.session_state:
        st.session_state.ai_chat_input = ""
    
    with st.sidebar.expander("💬 שאל שאלה", expanded=False):
        user_question = st.text_input(
            "הקלד שאלה",
            key="ai_question_input",
            placeholder="איך יוצרים הזמנה חדשה?"
        )
        
        if st.button("שלח", key="send_ai_question", use_container_width=True):
            if user_question.strip():
                with st.spinner("חושב..."):
                    response = ai_chat_response(user_question)
                    st.session_state.ai_chat_history.append({
                        "question": user_question,
                        "answer": response
                    })
        
        if st.session_state.ai_chat_history:
            st.markdown("---")
            for i, chat in enumerate(reversed(st.session_state.ai_chat_history[-3:])):
                st.markdown(f"**🙋 שאלה:** {chat['question']}")
                st.markdown(f"**🤖 תשובה:** {chat['answer']}")
                if i < len(st.session_state.ai_chat_history[-3:]) - 1:
                    st.markdown("---")
        
        if st.session_state.ai_chat_history and st.button("🗑️ נקה היסטוריה", key="clear_ai_history"):
            st.session_state.ai_chat_history = []
            st.rerun()
