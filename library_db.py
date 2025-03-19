import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox

# Database Connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="library_management"
)
cursor = conn.cursor()

def show_home():
    books_frame.pack_forget()
    home_frame.pack(fill='both', expand=True)

def show_books():
    home_frame.pack_forget()
    books_frame.pack(fill='both', expand=True)
    fetch_books()

def fetch_books():
    for row in books_table.get_children():
        books_table.delete(row)
    cursor.execute("SELECT BookID, Title, Genre, AvailableCopies FROM Books")
    for book in cursor.fetchall():
        books_table.insert("", "end", values=book)

def add_book():
    title = title_entry.get()
    genre = genre_entry.get()
    copies = copies_entry.get()
    if not title or not genre or not copies:
        messagebox.showwarning("Input Error", "All fields are required!")
        return
    try:
        copies = int(copies)
        cursor.execute("INSERT INTO Books (Title, Genre, AvailableCopies) VALUES (%s, %s, %s)", (title, genre, copies))
        conn.commit()
        messagebox.showinfo("Success", "Book added successfully!")
        fetch_books()
        title_entry.delete(0, tk.END)
        genre_entry.delete(0, tk.END)
        copies_entry.delete(0, tk.END)
    except ValueError:
        messagebox.showerror("Input Error", "Copies must be a number!")

def remove_book():
    selected_item = books_table.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a book to remove!")
        return
    book_id = books_table.item(selected_item)['values'][0]
    cursor.execute("DELETE FROM Books WHERE BookID = %s", (book_id,))
    conn.commit()
    messagebox.showinfo("Success", "Book removed successfully!")
    fetch_books()

# GUI Setup
root = tk.Tk()
root.title("Library Management System")
root.geometry("800x500")

# Sidebar
sidebar = tk.Frame(root, width=200, bg='#d3d3d3')
sidebar.pack(side='left', fill='y')

tk.Button(sidebar, text="Home", command=show_home).pack(pady=10)
tk.Button(sidebar, text="Books", command=show_books).pack(pady=10)

# Home Frame
home_frame = tk.Frame(root, bg='white')
home_frame.pack(fill='both', expand=True)
tk.Label(home_frame, text="Welcome to Library Management", font=("Arial", 20)).pack(pady=20)

# Books Frame
books_frame = tk.Frame(root, bg='white')
search_entry = tk.Entry(books_frame)
search_entry.pack(pady=5)
books_table = ttk.Treeview(books_frame, columns=("BookID", "Title", "Genre", "AvailableCopies"), show="headings")
for col in ("BookID", "Title", "Genre", "AvailableCopies"):
    books_table.heading(col, text=col)
books_table.pack(pady=5)

title_entry = tk.Entry(books_frame)
genre_entry = tk.Entry(books_frame)
copies_entry = tk.Entry(books_frame)
add_btn = tk.Button(books_frame, text="Add Book", command=add_book)
remove_btn = tk.Button(books_frame, text="Remove Book", command=remove_book)

title_entry.pack(pady=2)
genre_entry.pack(pady=2)
copies_entry.pack(pady=2)
add_btn.pack(pady=5)
remove_btn.pack(pady=5)

# Start at Home
show_home()
root.mainloop()
conn.close()
