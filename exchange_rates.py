"""
Exchange Rate Module
Fetches current exchange rates from Bank of Israel official API
EUR, USD, GBP to ILS with 0.05 NIS margin
"""

import requests
from datetime import datetime, timedelta

RATE_MARGIN = 0.05
CACHE_DURATION_HOURS = 1

_rates_cache = {
    'rates': None,
    'last_updated': None
}

DEFAULT_RATES = {
    'EUR': 3.76,
    'USD': 3.20,
    'GBP': 4.28
}

def fetch_single_rate(currency: str) -> float:
    """Fetch single currency rate from Bank of Israel CSV endpoint"""
    try:
        series_code = f"RER_{currency}_ILS"
        url = f"https://edge.boi.gov.il/FusionEdgeServer/sdmx/v2/data/dataflow/BOI.STATISTICS/EXR/1.0/{series_code}"
        params = {
            "format": "csv",
            "lastNObservations": "1"
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        lines = response.text.strip().split('\n')
        if len(lines) >= 2:
            data_line = lines[1]
            fields = data_line.split(',')
            obs_value_index = 13
            if len(fields) > obs_value_index:
                return float(fields[obs_value_index])
        
        return DEFAULT_RATES.get(currency, 3.50)
        
    except Exception as e:
        print(f"Error fetching {currency} rate: {e}")
        return DEFAULT_RATES.get(currency, 3.50)


def fetch_exchange_rates():
    """
    Fetch current exchange rates from Bank of Israel API
    Returns dict with EUR, USD, GBP rates to ILS (with margin added)
    """
    global _rates_cache
    
    now = datetime.now()
    if _rates_cache['rates'] and _rates_cache['last_updated']:
        if now - _rates_cache['last_updated'] < timedelta(hours=CACHE_DURATION_HOURS):
            return _rates_cache['rates']
    
    rates = {}
    for currency in ['EUR', 'USD', 'GBP']:
        base_rate = fetch_single_rate(currency)
        rates[currency] = round(base_rate + RATE_MARGIN, 2)
    
    _rates_cache['rates'] = rates
    _rates_cache['last_updated'] = now
    
    return rates


def get_rate_for_currency(currency: str) -> float:
    """Get exchange rate for specific currency to ILS"""
    rates = fetch_exchange_rates()
    return rates.get(currency, round(DEFAULT_RATES.get(currency, 3.50) + RATE_MARGIN, 2))


def get_currency_symbol(currency: str) -> str:
    """Get currency symbol"""
    symbols = {
        'EUR': '€',
        'USD': '$',
        'GBP': '£'
    }
    return symbols.get(currency, currency)


def get_currency_name_hebrew(currency: str) -> str:
    """Get Hebrew name for currency"""
    names = {
        'EUR': 'יורו',
        'USD': 'דולר',
        'GBP': 'פאונד'
    }
    return names.get(currency, currency)
