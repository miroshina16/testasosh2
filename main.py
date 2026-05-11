import tkinter as tk
from tkinter import messagebox
import json
import os

class BookTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Book Tracker")

        # Поля ввода
        tk.Label(root, text="Название книги").grid(row=0)
        tk.Label(root, text="Автор").grid(row=1)
        tk.Label(root, text="Жанр").grid(row=2)
        tk.Label(root, text="Количество страниц").grid(row=3)

        self.title_entry = tk.Entry(root)
        self.author_entry = tk.Entry(root)
        self.genre_entry = tk.Entry(root)
        self.pages_entry = tk.Entry(root)

        self.title_entry.grid(row=0, column=1)
        self.author_entry.grid(row=1, column=1)
        self.genre_entry.grid(row=2, column=1)
        self.pages_entry.grid(row=3, column=1)

        # Кнопка добавления книги
        tk.Button(root, text="Добавить книгу", command=self.add_book).grid(row=4, columnspan=2)

        # Кнопка фильтрации
        tk.Button(root, text="Фильтровать", command=self.filter_books).grid(row=5, columnspan=2)

        # Список книг
        self.books_listbox = tk.Listbox(root, width=50)
        self.books_listbox.grid(row=6, columnspan=2)

        # Загрузка данных из JSON
        self.load_books()

    def add_book(self):
        title = self.title_entry.get()
        author = self.author_entry.get()
        genre = self.genre_entry.get()
        pages = self.pages_entry.get()

        if not title or not author or not genre or not pages:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
            return

        try:
            pages = int(pages)
        except ValueError:
            messagebox.showerror("Ошибка", "Количество страниц должно быть числом")
            return

        book = {"title": title, "author": author, "genre": genre, "pages": pages}
        
        with open('books.json', 'a') as f:
            json.dump(book, f)
            f.write('\n')

        self.books_listbox.insert(tk.END, f"{title} - {author} ({genre}, {pages} страниц)")
        self.clear_entries()

    def clear_entries(self):
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.genre_entry.delete(0, tk.END)
        self.pages_entry.delete(0, tk.END)

    def load_books(self):
        if os.path.exists('books.json'):
            with open('books.json', 'r') as f:
                for line in f:
                    book = json.loads(line.strip())
                    self.books_listbox.insert(tk.END, f"{book['title']} - {book['author']} ({book['genre']}, {book['pages']} страниц)")

    def filter_books(self):
        genre_filter = self.genre_entry.get()
        page_filter = self.pages_entry.get()

        filtered_books = []

        if os.path.exists('books.json'):
            with open('books.json', 'r') as f:
                for line in f:
                    book = json.loads(line.strip())
                    if (not genre_filter or book['genre'] == genre_filter) and \
                       (not page_filter or book['pages'] > int(page_filter)):
                        filtered_books.append(f"{book['title']} - {book['author']} ({book['genre']}, {book['pages']} страниц)")

            self.books_listbox.delete(0, tk.END)
            for b in filtered_books:
                self.books_listbox.insert(tk.END, b)

if __name__ == "__main__":
    root = tk.Tk()
    app = BookTracker(root)
    root.mainloop()
