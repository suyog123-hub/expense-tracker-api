
import requests
from django.core.cache import cache

BASE_URL = "https://api.exchangerate-api.com/v4/latest/USD"


def convert_amount(amount, from_currency, to_currency):
    """Convert money from one currency to another"""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    if from_currency == to_currency:
        return round(float(amount), 2)
    
    rates = cache.get("exchange_rates")
    
    if not rates:
        try:
            response = requests.get(BASE_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            rates = data.get("rates", {})
            cache.set("exchange_rates", rates, timeout=3600) 
        except:
            return round(float(amount), 2)
    
    if from_currency not in rates or to_currency not in rates:
        return round(float(amount), 2)
    try:
        amount_in_usd = float(amount) / rates[from_currency]
        converted = amount_in_usd * rates[to_currency]
        return round(converted, 2)
    except:
        return round(float(amount), 2)


SUPPORTED_CURRENCIES = ["USD", "EUR", "GBP", "NPR", "INR", "AUD", "CAD", "JPY", "CNY", "AED"]