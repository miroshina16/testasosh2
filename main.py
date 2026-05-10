import tkinter as tk
from tkinter import ttk, messagebox
from currency_converter import CurrencyConverter
from utils import load_history, add_to_history, save_history

class CurrencyConverterApp:
    def __init__(self, root, api_key):
        self.root = root
        self.converter = CurrencyConverter(api_key)
        
        # Настройка главного окна
        self.root.title("Currency Converter - Конвертер валют")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Доступные валюты
        self.currencies = [
            "USD", "EUR", "RUB", "GBP", "JPY", "CNY", 
            "CAD", "CHF", "AUD", "TRY", "INR", "BRL"
        ]
        
        self.setup_ui()
        self.load_history_to_table()
        
    def setup_ui(self):
        """Создание интерфейса"""
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Заголовок
        title = ttk.Label(main_frame, text="Конвертер валют", 
                         font=('Arial', 18, 'bold'))
        title.pack(pady=(0, 20))
        
        # Рамка конвертации
        convert_frame = ttk.LabelFrame(main_frame, text="Конвертация", padding="15")
        convert_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Строка 1: Из валюты
        ttk.Label(convert_frame, text="Из:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.from_currency = ttk.Combobox(convert_frame, values=self.currencies, width=10)
        self.from_currency.grid(row=0, column=1, padx=5, pady=5)
        self.from_currency.set("USD")
        
        # Строка 2: В валюту
        ttk.Label(convert_frame, text="В:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.to_currency = ttk.Combobox(convert_frame, values=self.currencies, width=10)
        self.to_currency.grid(row=1, column=1, padx=5, pady=5)
        self.to_currency.set("EUR")
        
        # Строка 3: Сумма
        ttk.Label(convert_frame, text="Сумма:").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.amount_entry = ttk.Entry(convert_frame, width=20)
        self.amount_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Кнопка конвертации
        self.convert_btn = ttk.Button(convert_frame, text="Конвертировать", 
                                      command=self.convert_currency)
        self.convert_btn.grid(row=2, column=2, padx=10, pady=5)
        
        # Результат
        self.result_label = ttk.Label(convert_frame, text="", font=('Arial', 12, 'bold'))
        self.result_label.grid(row=3, column=0, columnspan=3, pady=10)
        
        # Рамка истории
        history_frame = ttk.LabelFrame(main_frame, text="История конвертаций", padding="10")
        history_frame.pack(fill=tk.BOTH, expand=True)
        
        # Таблица истории
        columns = ("Дата", "Из", "В", "Сумма", "Результат", "Курс")
        self.history_tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=12)
        
        # Настройка колонок
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
        
        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Кнопки управления историей
        button_frame = ttk.Frame(history_frame)
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(button_frame, text="Обновить историю", 
                  command=self.load_history_to_table).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить историю", 
                  command=self.clear_history).pack(side=tk.LEFT, padx=5)
        
    def convert_currency(self):
        """Конвертация валюты"""
        # Проверка ввода суммы
        amount_str = self.amount_entry.get().strip()
        
        if not amount_str:
            messagebox.showerror("Ошибка", "Введите сумму")
            return
        
        try:
            amount = float(amount_str)
            if amount <= 0:
                messagebox.showerror("Ошибка", "Сумма должна быть положительным числом")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное число")
            return
        
        from_curr = self.from_currency.get()
        to_curr = self.to_currency.get()
        
        # Блокируем кнопку на время запроса
        self.convert_btn.config(state='disabled', text="Конвертирую...")
        self.result_label.config(text="Загрузка курса...")
        
        # Конвертация
        def on_conversion(success, result, rate):
            self.root.after(0, lambda: self.on_conversion_done(success, result, rate, 
                                                               from_curr, to_curr, amount))
        
        self.converter.convert(amount, from_curr, to_curr, on_conversion)
    
    def on_conversion_done(self, success, result, rate, from_curr, to_curr, amount):
        """Обработка результата конвертации"""
        self.convert_btn.config(state='normal', text="Конвертировать")
        
        if success:
            result_text = f"{amount:.2f} {from_curr} = {result:.2f} {to_curr} (Курс: {rate:.4f})"
            self.result_label.config(text=result_text, foreground='green')
            
            # Добавляем в историю
            add_to_history(from_curr, to_curr, amount, result, rate)
            self.load_history_to_table()
        else:
            self.result_label.config(text="Ошибка получения курса валют", foreground='red')
            messagebox.showerror("Ошибка", "Не удалось получить курс конвертации.\nПроверьте API-ключ и интернет соединение.")
    
    def load_history_to_table(self):
        """Загрузить историю в таблицу"""
        # Очищаем таблицу
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Загружаем историю
        history = load_history()
        reversed_history = reversed(history)  # Новые записи сверху
        
        for entry in reversed_history:
            self.history_tree.insert("", 0, values=(
                entry.get("timestamp", ""),
                entry.get("from", ""),
                entry.get("to", ""),
                f"{entry.get('amount', 0):.2f}",
                f"{entry.get('result', 0):.2f}",
                f"{entry.get('rate', 0):.4f}"
            ))
    
    def clear_history(self):
        """Очистить историю"""
        if messagebox.askyesno("Подтверждение", "Очистить всю историю конвертаций?"):
            save_history([])
            self.load_history_to_table()
            self.result_label.config(text="История очищена", foreground='blue')
            self.root.after(2000, lambda: self.result_label.config(text=""))

def main():
    # Укажите ваш API ключ здесь
    API_KEY = "0992b504d1de6cd8c7d7ef55"  # Замените на ваш ключ
    
    if API_KEY == "YOUR_API_KEY_HERE":
        root = tk.Tk()
        root.withdraw()  # Скрываем главное окно
        messagebox.showwarning("Внимание", 
                               "Пожалуйста, укажите ваш API-ключ в файле main.py\n"
                               "Получите ключ на https://app.exchangerate-api.com/sign-up")
        root.destroy()
        return
    
    root = tk.Tk()
    app = CurrencyConverterApp(root, API_KEY)
    root.mainloop()

if __name__ == "__main__":
    main()