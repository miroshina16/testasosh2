import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"

def load_history():
    """Загрузить историю из JSON файла"""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_history(history):
    """Сохранить историю в JSON файл"""
    with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def add_to_history(from_currency, to_currency, amount, result, rate):
    """Добавить запись в историю"""
    history = load_history()
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "from": from_currency,
        "to": to_currency,
        "amount": amount,
        "result": result,
        "rate": rate
    }
    history.append(entry)
    save_history(history)
    return entry