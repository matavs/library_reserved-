import mysql.connector
import tkinter as tk
from tkinter import messagebox

# Database Connection (Update with your MySQL details)
conn = mysql.connector.connect(
    host="localhost",      # Change if using a remote server
    user="root",           # Default XAMPP user
    password="",           # Leave empty if no password
    database="library_management"  # Change to your actual database name
)
cursor = conn.cursor()

# Function to Insert Book Data
def add_book():
    title = title_entry.get()
    author = author_entry.get()
    genre = genre_entry.get()
    copies = copies_entry.get()

    if not title or not author or not genre or not copies:
        messagebox.showwarning("Input Error", "All fields are required!")
        return

    try:
        copies = int(copies)  # Ensure AvailableCopies is an integer
        query = "INSERT INTO Books (Title, Author, Genre, AvailableCopies) VALUES (%s, %s, %s, %s)"
        values = (title, author, genre, copies)
        cursor.execute(query, values)
        conn.commit()

        messagebox.showinfo("Success", "Book added successfully!")
        clear_fields()

    except ValueError:
        messagebox.showerror("Input Error", "Available Copies must be a number!")
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

# Clear input fields after successful insertion
def clear_fields():
    title_entry.delete(0, tk.END)
    author_entry.delete(0, tk.END)
    genre_entry.delete(0, tk.END)
    copies_entry.delete(0, tk.END)

# GUI Setup
root = tk.Tk()
root.title("Library Management - Add Book")
root.geometry("350x250")


tk.Label(root, text="Title:").grid(row=0, column=0, padx=10, pady=5)
title_entry = tk.Entry(root)
title_entry.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Author:").grid(row=1, column=0, padx=10, pady=5)
author_entry = tk.Entry(root)
author_entry.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Genre:").grid(row=2, column=0, padx=10, pady=5)
genre_entry = tk.Entry(root)
genre_entry.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Available Copies:").grid(row=3, column=0, padx=10, pady=5)
copies_entry = tk.Entry(root)
copies_entry.grid(row=3, column=1, padx=10, pady=5)

# Add Book Button
add_button = tk.Button(root, text="Add Book", command=add_book)
add_button.grid(row=4, column=0, columnspan=2, pady=10)

# Run the GUI
root.mainloop()

# Close the database connection when the program ends
conn.close()
