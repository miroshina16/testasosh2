import requests
import threading

class CurrencyConverter:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://v6.exchangerate-api.com/v6"
        self.cache = {}
        
    def get_exchange_rate(self, from_currency, to_currency):
        """Получить курс обмена через API"""
        cache_key = f"{from_currency}_{to_currency}"
        
        # Проверяем кэш
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        try:
            # Запрос к API
            url = f"{self.base_url}/{self.api_key}/pair/{from_currency}/{to_currency}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['result'] == 'success':
                    rate = data['conversion_rate']
                    self.cache[cache_key] = rate
                    return rate
            return None
        except requests.RequestException:
            return None
    
    def convert(self, amount, from_currency, to_currency, callback):
        """Конвертировать валюту (асинхронно)"""
        def convert_thread():
            rate = self.get_exchange_rate(from_currency, to_currency)
            if rate is not None:
                result = amount * rate
                callback(True, result, rate)
            else:
                callback(False, None, None)
        
        thread = threading.Thread(target=convert_thread, daemon=True)
        thread.start()