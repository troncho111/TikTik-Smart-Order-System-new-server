"""
קודי IATA של חברות תעופה - מתמקד באירופה וישראל
"""

AIRLINE_CODES = {
    # ספרד
    'UX': 'Air Europa',
    'IB': 'Iberia',
    'VY': 'Vueling',
    'I2': 'Iberia Express',
    'NT': 'Binter Canarias',
    
    # בריטניה
    'BA': 'British Airways',
    'U2': 'easyJet',
    'BY': 'TUI Airways',
    'LS': 'Jet2',
    'FR': 'Ryanair',
    
    # גרמניה
    'LH': 'Lufthansa',
    'EW': 'Eurowings',
    '4Y': 'Eurowings Discover',
    'DE': 'Condor',
    
    # צרפת
    'AF': 'Air France',
    'TO': 'Transavia France',
    'XK': 'Air Corsica',
    
    # איטליה
    'AZ': 'ITA Airways',
    'IG': 'Air Italy',
    'AP': 'AlbaStar',
    
    # הולנד
    'KL': 'KLM',
    'HV': 'Transavia',
    
    # בלגיה
    'SN': 'Brussels Airlines',
    
    # שווייץ
    'LX': 'Swiss International',
    
    # אוסטריה
    'OS': 'Austrian Airlines',
    
    # סקנדינביה
    'SK': 'SAS Scandinavian',
    'AY': 'Finnair',
    'DY': 'Norwegian',
    
    # טורקיה
    'TK': 'Turkish Airlines',
    'PC': 'Pegasus Airlines',
    
    # יוון
    'A3': 'Aegean Airlines',
    'GQ': 'Sky Express',
    
    # פורטוגל
    'TP': 'TAP Air Portugal',
    
    # אירלנד
    'EI': 'Aer Lingus',
    
    # פולין
    'LO': 'LOT Polish Airlines',
    
    # צ'כיה
    'OK': 'Czech Airlines',
    
    # רומניה
    'RO': 'Tarom',
    
    # Low-cost אירופה
    'W6': 'Wizz Air',
    'W4': 'Wizz Air Malta',
    'U2': 'easyJet',
    'FR': 'Ryanair',
    
    # ישראל
    'LY': 'El Al',
    '6H': 'Israir',
    'UP': 'El Al (UP)',
    
    # ארה"ב/קנדה (למונדיאל)
    'AA': 'American Airlines',
    'UA': 'United Airlines',
    'DL': 'Delta Air Lines',
    'AC': 'Air Canada',
    'WS': 'WestJet',
    
    # מקסיקו (למונדיאל)
    'AM': 'Aeroméxico',
    'VB': 'VivaAerobus',
    'Y4': 'Volaris',
    
    # אחרות
    'EK': 'Emirates',
    'QR': 'Qatar Airways',
    'SV': 'Saudia',
    'MS': 'EgyptAir',
    'RJ': 'Royal Jordanian',
}


def get_airline_from_flight(flight_number: str) -> str:
    """
    מחלץ שם חברת תעופה ממספר טיסה לפי קוד IATA
    
    Args:
        flight_number: מספר טיסה (לדוגמה: "UX1302", "LY315")
    
    Returns:
        שם חברת התעופה או מחרוזת ריקה אם לא זוהה
    
    Examples:
        >>> get_airline_from_flight("UX1302")
        'Air Europa'
        >>> get_airline_from_flight("LY315")
        'El Al'
        >>> get_airline_from_flight("BA123")
        'British Airways'
        >>> get_airline_from_flight("XYZ99")
        ''
    """
    if not flight_number or len(flight_number) < 2:
        return ""
    
    # Extract first 2 characters as IATA code
    code = flight_number[:2].upper()
    
    return AIRLINE_CODES.get(code, "")


def get_all_airlines():
    """מחזיר רשימה של כל חברות התעופה הזמינות"""
    return sorted(set(AIRLINE_CODES.values()))
