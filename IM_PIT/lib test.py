import mysql.connector
import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage  # Keep this for tkinter icons
from PIL import Image, ImageTk  # Import Image from Pillow


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
root.configure(bg="#ADD8E6")

# Sidebar
sidebar = tk.Frame(root, width=150, bg='#d3d3d3')  # Increased width from 200 to 250
sidebar.pack(side='left', fill='y')
sidebar.pack_propagate(False)

#Home Image Button #####

# Load and resize the image
img = Image.open("IM_PIT/icons/Logo-no_bg.png")  # Supports JPG, PNG, etc.
img = img.resize((80, 80))  # Resize if needed
home_icon = ImageTk.PhotoImage(img)

# Create Image Button
home_button = tk.Button(sidebar, image=home_icon, command=show_home, bg='#d3d3d3', borderwidth=0)
home_button.image = home_icon  # Prevent garbage collection
home_button.pack(pady=10)

###########################

#Members Image Button #####

# Create a Frame for the button and label
member_frame = tk.Frame(sidebar, bg='#d3d3d3')  # Matches sidebar background
member_frame.pack(pady=10)

# Load and resize the image
img = Image.open("IM_PIT/icons/group.png")
img = img.resize((40, 40))  # Resize if needed
member_icon = ImageTk.PhotoImage(img)

# Create Image Button
member_button = tk.Button(member_frame, image=member_icon, command=show_books, bg='#d3d3d3', borderwidth=0)
member_button.image = member_icon  # Prevent garbage collection
member_button.pack()

# Add Label Below Image
member_label = tk.Label(member_frame, text="Member", bg='#d3d3d3', font=("Arial", 10))
member_label.pack()
###########################


# Home Frame
home_frame = tk.Frame(root, bg='#808080')
home_frame.pack(fill='both', expand=True)
welcome_label = tk.Label(home_frame, text="Welcome to Library Management", font=("Arial", 20), bg='#808080')
welcome_label.place(x=40, y=30)

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
