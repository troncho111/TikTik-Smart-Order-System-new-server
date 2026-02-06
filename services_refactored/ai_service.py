"""
AI Service - שירות Gemini AI לצ'אט ועזרה
"""
import os
from google import genai


def get_gemini_client():
    """
    יצירת client ל-Gemini AI
    
    Returns:
        genai.Client או None במקרה של שגיאה
    """
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
    """
    יצירת תשובת AI לשאלת משתמש
    
    Args:
        question: שאלה מהמשתמש
        
    Returns:
        str: תשובת AI
    """
    client = get_gemini_client()
    if not client:
        return "שירות הצ'אט אינו זמין כרגע. פנה למנהל המערכת."
    
    system_prompt = """אתה עוזר וירטואלי של מערכת TikTik. ענה בעברית קצר וברור.

בעיות נפוצות ופתרונות:

❓ "העליתי דרכון ולא קורה כלום"
✅ תשובה: לאחר העלאת התמונה, חייבים ללחוץ על כפתור "🔍 סרוק דרכון"!

❓ "איך מוסיפים נוסעים?"
✅ תשובה: בחלק "פרטי נוסעים", מלאו את הפרטים ולחצו על "➕ הוסף נוסע". אפשר גם לסרוק דרכון.

❓ "איך מחפשים מלון?"
✅ תשובה: הכניסו שם מלון בשדה "מלון" ולחצו על "🔍 חפש מלון". אפשר גם להדביק קישור מ-Booking.

❓ "איך מחפשים טיסה?"
✅ תשובה: בחרו שדות תעופה, תאריכים ולחצו על "🔍 חפש טיסות". אפשר גם להדביק צילום מסך.

❓ "איך יוצרים PDF?"
✅ תשובה: מלאו את כל הפרטים הנדרשים ולחצו על "📄 צור PDF" בתחתית הטופס.

❓ "איך שומרים הזמנה?"
✅ תשובה: לחצו על "💾 שמור הזמנה" - ההזמנה תישמר במערכת ותוכלו למצוא אותה ב"היסטוריית הזמנות".

❓ "מה ההבדל בין חבילה לכרטיסים?"
✅ תשובה: 
   • חבילה מלאה = כרטיסים + מלון + טיסות
   • כרטיסים בלבד = רק כרטיסים לאירוע

❓ "איך מוסיפים תמונות?"
✅ תשובה: לחצו על "📁 העלה תמונה" או "📋 הדבק תמונה" בחלק הרלוונטי (אצטדיון/מלון).

❓ "המערכת לא שומרת את הנתונים"
✅ תשובה: ודאו שלחצתם על "💾 שמור הזמנה" לפני סגירת הדף.

❓ "איך מייצאים נתונים?"
✅ תשובה: עברו לעמוד "ייצוא נתונים" בתפריט הצד ובחרו את סוג הייצוא (Excel/CSV).

אם השאלה לא קשורה לנושאים אלה, ענה בצורה כללית על מערכת TikTik."""

    try:
        response = client.models.generate_content(
            model='gemini-2.0-flash-exp',
            contents=[
                {"role": "user", "parts": [{"text": system_prompt}]},
                {"role": "model", "parts": [{"text": "הבנתי. אני מוכן לעזור עם מערכת TikTik."}]},
                {"role": "user", "parts": [{"text": question}]}
            ]
        )
        return response.text
    except Exception as e:
        return f"מצטער, אירעה שגיאה: {str(e)}"
