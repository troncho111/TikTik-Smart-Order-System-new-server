"""
Common airports list for autocomplete
"""

AIRPORTS = [
    {"code": "TLV", "name": "נתב\"ג", "city": "תל אביב", "country": "ישראל"},
    {"code": "MAD", "name": "Madrid Barajas", "city": "מדריד", "country": "ספרד"},
    {"code": "BCN", "name": "Barcelona El Prat", "city": "ברצלונה", "country": "ספרד"},
    {"code": "LHR", "name": "London Heathrow", "city": "לונדון", "country": "אנגליה"},
    {"code": "LGW", "name": "London Gatwick", "city": "לונדון", "country": "אנגליה"},
    {"code": "STN", "name": "London Stansted", "city": "לונדון", "country": "אנגליה"},
    {"code": "LTN", "name": "London Luton", "city": "לונדון", "country": "אנגליה"},
    {"code": "CDG", "name": "Paris Charles de Gaulle", "city": "פריז", "country": "צרפת"},
    {"code": "ORY", "name": "Paris Orly", "city": "פריז", "country": "צרפת"},
    {"code": "FCO", "name": "Rome Fiumicino", "city": "רומא", "country": "איטליה"},
    {"code": "MXP", "name": "Milan Malpensa", "city": "מילאנו", "country": "איטליה"},
    {"code": "VCE", "name": "Venice Marco Polo", "city": "ונציה", "country": "איטליה"},
    {"code": "AMS", "name": "Amsterdam Schiphol", "city": "אמסטרדם", "country": "הולנד"},
    {"code": "FRA", "name": "Frankfurt", "city": "פרנקפורט", "country": "גרמניה"},
    {"code": "MUC", "name": "Munich", "city": "מינכן", "country": "גרמניה"},
    {"code": "BER", "name": "Berlin Brandenburg", "city": "ברלין", "country": "גרמניה"},
    {"code": "VIE", "name": "Vienna", "city": "וינה", "country": "אוסטריה"},
    {"code": "ZRH", "name": "Zurich", "city": "ציריך", "country": "שוויץ"},
    {"code": "GVA", "name": "Geneva", "city": "ג'נבה", "country": "שוויץ"},
    {"code": "BRU", "name": "Brussels", "city": "בריסל", "country": "בלגיה"},
    {"code": "LIS", "name": "Lisbon", "city": "ליסבון", "country": "פורטוגל"},
    {"code": "ATH", "name": "Athens", "city": "אתונה", "country": "יוון"},
    {"code": "IST", "name": "Istanbul", "city": "איסטנבול", "country": "טורקיה"},
    {"code": "SAW", "name": "Istanbul Sabiha", "city": "איסטנבול", "country": "טורקיה"},
    {"code": "DXB", "name": "Dubai", "city": "דובאי", "country": "איחוד האמירויות"},
    {"code": "JFK", "name": "New York JFK", "city": "ניו יורק", "country": "ארה\"ב"},
    {"code": "EWR", "name": "Newark", "city": "ניו יורק", "country": "ארה\"ב"},
    {"code": "LAX", "name": "Los Angeles", "city": "לוס אנג'לס", "country": "ארה\"ב"},
    {"code": "MIA", "name": "Miami", "city": "מיאמי", "country": "ארה\"ב"},
    {"code": "PRG", "name": "Prague", "city": "פראג", "country": "צ'כיה"},
    {"code": "BUD", "name": "Budapest", "city": "בודפשט", "country": "הונגריה"},
    {"code": "WAW", "name": "Warsaw", "city": "ורשה", "country": "פולין"},
    {"code": "KRK", "name": "Krakow", "city": "קרקוב", "country": "פולין"},
    {"code": "CPH", "name": "Copenhagen", "city": "קופנהגן", "country": "דנמרק"},
    {"code": "OSL", "name": "Oslo", "city": "אוסלו", "country": "נורווגיה"},
    {"code": "ARN", "name": "Stockholm Arlanda", "city": "שטוקהולם", "country": "שוודיה"},
    {"code": "HEL", "name": "Helsinki", "city": "הלסינקי", "country": "פינלנד"},
    {"code": "DUB", "name": "Dublin", "city": "דבלין", "country": "אירלנד"},
    {"code": "EDI", "name": "Edinburgh", "city": "אדינבורו", "country": "סקוטלנד"},
    {"code": "MAN", "name": "Manchester", "city": "מנצ'סטר", "country": "אנגליה"},
    {"code": "AGP", "name": "Malaga", "city": "מלגה", "country": "ספרד"},
    {"code": "PMI", "name": "Palma de Mallorca", "city": "פלמה דה מיורקה", "country": "ספרד"},
    {"code": "LPA", "name": "Gran Canaria", "city": "גראן קנריה", "country": "ספרד"},
    {"code": "TFS", "name": "Tenerife South", "city": "טנריף", "country": "ספרד"},
    {"code": "NAP", "name": "Naples", "city": "נאפולי", "country": "איטליה"},
    {"code": "BLQ", "name": "Bologna", "city": "בולוניה", "country": "איטליה"},
    {"code": "PSA", "name": "Pisa", "city": "פיזה", "country": "איטליה"},
    {"code": "NCE", "name": "Nice", "city": "ניס", "country": "צרפת"},
    {"code": "LYS", "name": "Lyon", "city": "ליון", "country": "צרפת"},
    {"code": "MRS", "name": "Marseille", "city": "מרסיי", "country": "צרפת"},
    {"code": "SKG", "name": "Thessaloniki", "city": "סלוניקי", "country": "יוון"},
    {"code": "OTP", "name": "Bucharest", "city": "בוקרשט", "country": "רומניה"},
    {"code": "SOF", "name": "Sofia", "city": "סופיה", "country": "בולגריה"},
    {"code": "BEG", "name": "Belgrade", "city": "בלגרד", "country": "סרביה"},
    {"code": "ZAG", "name": "Zagreb", "city": "זאגרב", "country": "קרואטיה"},
    {"code": "SPU", "name": "Split", "city": "ספליט", "country": "קרואטיה"},
    {"code": "DBV", "name": "Dubrovnik", "city": "דוברובניק", "country": "קרואטיה"},
    {"code": "LJU", "name": "Ljubljana", "city": "לובליאנה", "country": "סלובניה"},
    {"code": "TIA", "name": "Tirana", "city": "טירנה", "country": "אלבניה"},
    {"code": "SKP", "name": "Skopje", "city": "סקופיה", "country": "מקדוניה"},
    {"code": "KBP", "name": "Kyiv Boryspil", "city": "קייב", "country": "אוקראינה"},
    {"code": "SVO", "name": "Moscow Sheremetyevo", "city": "מוסקבה", "country": "רוסיה"},
    {"code": "LED", "name": "St Petersburg", "city": "סנט פטרסבורג", "country": "רוסיה"},
    {"code": "AYT", "name": "Antalya", "city": "אנטליה", "country": "טורקיה"},
    {"code": "ESB", "name": "Ankara", "city": "אנקרה", "country": "טורקיה"},
    {"code": "LCA", "name": "Larnaca", "city": "לרנקה", "country": "קפריסין"},
    {"code": "PFO", "name": "Paphos", "city": "פאפוס", "country": "קפריסין"},
    {"code": "AMM", "name": "Amman", "city": "עמאן", "country": "ירדן"},
    {"code": "CAI", "name": "Cairo", "city": "קהיר", "country": "מצרים"},
    {"code": "SSH", "name": "Sharm el Sheikh", "city": "שארם א-שייח", "country": "מצרים"},
    {"code": "CMB", "name": "Colombo", "city": "קולומבו", "country": "סרי לנקה"},
    {"code": "BKK", "name": "Bangkok", "city": "בנגקוק", "country": "תאילנד"},
    {"code": "SIN", "name": "Singapore Changi", "city": "סינגפור", "country": "סינגפור"},
    {"code": "HKG", "name": "Hong Kong", "city": "הונג קונג", "country": "הונג קונג"},
    {"code": "PEK", "name": "Beijing", "city": "בייג'ינג", "country": "סין"},
    {"code": "NRT", "name": "Tokyo Narita", "city": "טוקיו", "country": "יפן"},
    {"code": "ICN", "name": "Seoul Incheon", "city": "סיאול", "country": "קוריאה"},
    {"code": "DEL", "name": "Delhi", "city": "דלהי", "country": "הודו"},
    {"code": "BOM", "name": "Mumbai", "city": "מומבאי", "country": "הודו"},
    {"code": "JNB", "name": "Johannesburg", "city": "יוהנסבורג", "country": "דרום אפריקה"},
    {"code": "CPT", "name": "Cape Town", "city": "קייפטאון", "country": "דרום אפריקה"},
    {"code": "ADD", "name": "Addis Ababa", "city": "אדיס אבבה", "country": "אתיופיה"},
    {"code": "YYZ", "name": "Toronto", "city": "טורונטו", "country": "קנדה"},
    {"code": "MEX", "name": "Mexico City", "city": "מקסיקו סיטי", "country": "מקסיקו"},
    {"code": "GRU", "name": "Sao Paulo", "city": "סאו פאולו", "country": "ברזיל"},
    {"code": "EZE", "name": "Buenos Aires", "city": "בואנוס איירס", "country": "ארגנטינה"},
    {"code": "SYD", "name": "Sydney", "city": "סידני", "country": "אוסטרליה"},
    {"code": "MEL", "name": "Melbourne", "city": "מלבורן", "country": "אוסטרליה"},
]

def get_airport_options():
    """Returns list of formatted airport strings for selectbox"""
    return [f"{a['code']} - {a['name']} ({a['city']})" for a in AIRPORTS]

def get_airport_code(option_string):
    """Extract IATA code from formatted option string"""
    if not option_string:
        return ""
    return option_string.split(" - ")[0] if " - " in option_string else option_string

def find_airport_by_code(code):
    """Find airport by IATA code"""
    code = code.upper().strip()
    for a in AIRPORTS:
        if a['code'] == code:
            return a
    return None

def format_airport_display(code):
    """Get display string for a code"""
    a = find_airport_by_code(code)
    if a:
        return f"{a['code']} - {a['name']} ({a['city']})"
    return code
