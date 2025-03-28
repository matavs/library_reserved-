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

# --- Utility Functions ---
def clear_entries(entries):
    for entry in entries:
        entry.delete(0, tk.END)

# --- Dialog Functions ---
def show_dialog(parent, title, width=400, height=300):
    dialog = tk.Toplevel(parent)
    dialog.title(title)
    dialog.geometry(f"{width}x{height}")
    dialog.transient(parent)
    dialog.grab_set()
    
    # Center the dialog
    x = parent.winfo_x() + (parent.winfo_width() // 2) - (width // 2)
    y = parent.winfo_y() + (parent.winfo_height() // 2) - (height // 2)
    dialog.geometry(f"+{x}+{y}")
    
    return dialog

# --- Home Tab ---
def show_home():
    hide_all_frames()
    home_frame.pack(fill='both', expand=True)

# --- Members Tab ---
def show_members():
    hide_all_frames()
    members_frame.pack(fill='both', expand=True)
    fetch_members()

def get_member_borrowing_history(member_id):
    """
    Retrieves the borrowing history of a specific member.
    """
    cursor.execute("""
        SELECT b.Title, bh.BorrowDate, bh.ReturnDate
        FROM BorrowingHistory bh
        JOIN Books b ON bh.BookID = b.BookID
        WHERE bh.MemberID = ?
        ORDER BY bh.BorrowDate DESC;
    """, (member_id,))
    
    return cursor.fetchall()

def fetch_members():
    for row in members_table.get_children():
        members_table.delete(row)
    cursor.execute("SELECT MemberID, Name, Email, MembershipDate FROM Members")
    for member in cursor.fetchall():
        members_table.insert("", "end", values=member)

def show_add_member_dialog():
    dialog = show_dialog(root, "Add a Member")
    
    # Dialog content
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    tk.Label(content_frame, text="Member Management", font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Member ID is auto-generated, so we don't need an entry for it
    tk.Label(content_frame, text="MemberID", anchor="w").pack(fill='x')
    member_id_label = tk.Label(content_frame, text="Auto-generated", anchor="w", bg="#f0f0f0", relief="groove", height=2)
    member_id_label.pack(fill='x', pady=(0, 10))
    
    # Name field
    tk.Label(content_frame, text="Name", anchor="w").pack(fill='x')
    name_entry = tk.Entry(content_frame)
    name_entry.pack(fill='x', pady=(0, 10))
    
    # Email field
    tk.Label(content_frame, text="Email", anchor="w").pack(fill='x')
    email_entry = tk.Entry(content_frame)
    email_entry.pack(fill='x', pady=(0, 10))
    
    # Membership Date field
    tk.Label(content_frame, text="Membership Date", anchor="w").pack(fill='x')
    date_entry = tk.Entry(content_frame)
    date_entry.pack(fill='x', pady=(0, 10))
    date_entry.insert(0, "MM/DD/YY")  # Default format
    
    # Buttons frame
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=(10, 0))
    
    # Add button
    def add_member_from_dialog():
        name = name_entry.get()
        email = email_entry.get()
        membership_date = date_entry.get()
        
        if not name or not email or not membership_date or membership_date == "MM/DD/YY":
            messagebox.showwarning("Input Error", "All fields are required!", parent=dialog)
            return
        
        cursor.execute("INSERT INTO Members (Name, Email, MembershipDate) VALUES (%s, %s, %s)", 
                       (name, email, membership_date))
        conn.commit()
        messagebox.showinfo("Success", "Member added successfully!", parent=dialog)
        dialog.destroy()
        fetch_members()
    
    add_btn = tk.Button(buttons_frame, text="add", command=add_member_from_dialog, width=10)
    add_btn.pack(side='right')
    
    # Cancel button
    cancel_btn = tk.Button(buttons_frame, text="X", command=dialog.destroy, width=3)
    cancel_btn.pack(side='right', padx=10)

def remove_member():
    selected_item = members_table.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a member to remove!")
        return
    member_id = members_table.item(selected_item)['values'][0]
    
    # Confirm deletion
    if messagebox.askyesno("Confirm", "Are you sure you want to remove this member?"):
        cursor.execute("DELETE FROM Members WHERE MemberID = %s", (member_id,))
        conn.commit()
        messagebox.showinfo("Success", "Member removed successfully!")
        fetch_members()

# --- Books Tab ---
def show_books():
    hide_all_frames()
    books_frame.pack(fill='both', expand=True)
    fetch_books()

def search_books(event=None):
    search_text = book_search_entry.get().lower()
    if search_text == "search for books":
        return

    for item in books_table.get_children():
        books_table.delete(item)

    cursor.execute("SELECT BookID, Title, Author, Genre, AvailableCopies FROM Books WHERE Title LIKE %s OR Author LIKE %s OR Genre LIKE %s", 
                  (f"%{search_text}%", f"%{search_text}%", f"%{search_text}%"))

    for book in cursor.fetchall():
        books_table.insert("", "end", values=book)


def fetch_books():
    for row in books_table.get_children():
        books_table.delete(row)
    cursor.execute("SELECT BookID, Title, Author, Genre, AvailableCopies FROM Books")
    for book in cursor.fetchall():
        books_table.insert("", "end", values=book)

def show_add_book_dialog():
    dialog = show_dialog(root, "Add a Book")
    
    # Dialog content
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    tk.Label(content_frame, text="Book Management", font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Title field
    tk.Label(content_frame, text="Title", anchor="w").pack(fill='x')
    title_entry = tk.Entry(content_frame)
    title_entry.pack(fill='x', pady=(0, 10))
    
    # Author field
    tk.Label(content_frame, text="Author", anchor="w").pack(fill='x')
    author_entry = tk.Entry(content_frame)
    author_entry.pack(fill='x', pady=(0, 10))

    # Genre field
    tk.Label(content_frame, text="Genre", anchor="w").pack(fill='x')
    genre_entry = tk.Entry(content_frame)
    genre_entry.pack(fill='x', pady=(0, 10))
    
    # Available Copies field
    tk.Label(content_frame, text="Available Copies", anchor="w").pack(fill='x')
    copies_entry = tk.Entry(content_frame)
    copies_entry.pack(fill='x', pady=(0, 10))
    
    # Buttons frame
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=(10, 0))
    
    # Add button
    def add_book_from_dialog():
        title = title_entry.get()
        author = author_entry.get()
        genre = genre_entry.get()
        copies = copies_entry.get()
        
        if not title or not genre or not copies:
            messagebox.showwarning("Input Error", "All fields are required!", parent=dialog)
            return
        
        try:
            copies = int(copies)
            cursor.execute("INSERT INTO Books (Title, Author, Genre, AvailableCopies) VALUES (%s, %s, %s, %s)", 
                           (title, author, genre, copies))
            conn.commit()
            messagebox.showinfo("Success", "Book added successfully!", parent=dialog)
            dialog.destroy()
            fetch_books()
        except ValueError:
            messagebox.showerror("Input Error", "Copies must be a number!", parent=dialog)
    
    add_btn = tk.Button(buttons_frame, text="add", command=add_book_from_dialog, width=10)
    add_btn.pack(side='right')
    
    # Cancel button
    cancel_btn = tk.Button(buttons_frame, text="X", command=dialog.destroy, width=3)
    cancel_btn.pack(side='right', padx=10)

def remove_book():
    selected_item = books_table.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a book to remove!")
        return
    book_id = books_table.item(selected_item)['values'][0]
    
    # Confirm deletion
    if messagebox.askyesno("Confirm", "Are you sure you want to remove this book?"):
        cursor.execute("DELETE FROM Books WHERE BookID = %s", (book_id,))
        conn.commit()
        messagebox.showinfo("Success", "Book removed successfully!")
        fetch_books()

# --- Reservations Tab ---
def show_reservations():
    hide_all_frames()
    reservations_frame.pack(fill='both', expand=True)
    fetch_reservations()

def fetch_reservations():
    for row in reservations_table.get_children():
        reservations_table.delete(row)
    cursor.execute("SELECT ReservationID, MemberID, BookID, ReservationDate FROM Reservations")
    for reservation in cursor.fetchall():
        reservations_table.insert("", "end", values=reservation)

def show_add_reservation_dialog():
    dialog = show_dialog(root, "Add a Reservation")
    
    # Dialog content
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    tk.Label(content_frame, text="Reservation Management", font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Member ID field
    tk.Label(content_frame, text="Member ID", anchor="w").pack(fill='x')
    member_id_entry = tk.Entry(content_frame)
    member_id_entry.pack(fill='x', pady=(0, 10))
    
    # Book ID field
    tk.Label(content_frame, text="Book ID", anchor="w").pack(fill='x')
    book_id_entry = tk.Entry(content_frame)
    book_id_entry.pack(fill='x', pady=(0, 10))
    
    # Reservation Date field
    tk.Label(content_frame, text="Reservation Date", anchor="w").pack(fill='x')
    date_entry = tk.Entry(content_frame)
    date_entry.pack(fill='x', pady=(0, 10))
    date_entry.insert(0, "MM/DD/YY")  # Default format
    
    # Buttons frame
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=(10, 0))
    
    # Add button
    def add_reservation_from_dialog():
        member_id = member_id_entry.get()
        book_id = book_id_entry.get()
        reservation_date = date_entry.get()
        
        if not member_id or not book_id or not reservation_date or reservation_date == "MM/DD/YY":
            messagebox.showwarning("Input Error", "All fields are required!", parent=dialog)
            return
        
        cursor.execute("INSERT INTO Reservations (MemberID, BookID, ReservationDate) VALUES (%s, %s, %s)", 
                       (member_id, book_id, reservation_date))
        conn.commit()
        messagebox.showinfo("Success", "Reservation added successfully!", parent=dialog)
        dialog.destroy()
        fetch_reservations()
    
    add_btn = tk.Button(buttons_frame, text="add", command=add_reservation_from_dialog, width=10)
    add_btn.pack(side='right')
    
    # Cancel button
    cancel_btn = tk.Button(buttons_frame, text="X", command=dialog.destroy, width=3)
    cancel_btn.pack(side='right', padx=10)

def remove_reservation():
    selected_item = reservations_table.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a reservation to remove!")
        return
    reservation_id = reservations_table.item(selected_item)['values'][0]
    
    # Confirm deletion
    if messagebox.askyesno("Confirm", "Are you sure you want to remove this reservation?"):
        cursor.execute("DELETE FROM Reservations WHERE ReservationID = %s", (reservation_id,))
        conn.commit()
        messagebox.showinfo("Success", "Reservation removed successfully!")
        fetch_reservations()

# --- Loans Tab ---
def show_loans():
    hide_all_frames()
    loans_frame.pack(fill='both', expand=True)
    fetch_loans()

def fetch_loans():
    for row in loans_table.get_children():
        loans_table.delete(row)
    cursor.execute("SELECT LoanID, MemberID, BookID, LoanDate, ReturnDate FROM Loans")
    for loan in cursor.fetchall():
        loans_table.insert("", "end", values=loan)

def show_add_loan_dialog():
    dialog = show_dialog(root, "Add a Loan", width=400, height=350)
    
    # Dialog content
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    tk.Label(content_frame, text="Loan Management", font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Member ID field
    tk.Label(content_frame, text="Member ID", anchor="w").pack(fill='x')
    member_id_entry = tk.Entry(content_frame)
    member_id_entry.pack(fill='x', pady=(0, 10))
    
    # Book ID field
    tk.Label(content_frame, text="Book ID", anchor="w").pack(fill='x')
    book_id_entry = tk.Entry(content_frame)
    book_id_entry.pack(fill='x', pady=(0, 10))
    
    # Loan Date field
    tk.Label(content_frame, text="Loan Date", anchor="w").pack(fill='x')
    loan_date_entry = tk.Entry(content_frame)
    loan_date_entry.pack(fill='x', pady=(0, 10))
    loan_date_entry.insert(0, "MM/DD/YY")  # Default format
    
    # Return Date field
    tk.Label(content_frame, text="Return Date", anchor="w").pack(fill='x')
    return_date_entry = tk.Entry(content_frame)
    return_date_entry.pack(fill='x', pady=(0, 10))
    return_date_entry.insert(0, "MM/DD/YY")  # Default format
    
    # Buttons frame
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=(10, 0))
    
    # Add button
    def add_loan_from_dialog():
        member_id = member_id_entry.get()
        book_id = book_id_entry.get()
        loan_date = loan_date_entry.get()
        return_date = return_date_entry.get()
        
        if (not member_id or not book_id or 
            not loan_date or loan_date == "MM/DD/YY" or 
            not return_date or return_date == "MM/DD/YY"):
            messagebox.showwarning("Input Error", "All fields are required!", parent=dialog)
            return
        
        cursor.execute("INSERT INTO Loans (MemberID, BookID, LoanDate, ReturnDate) VALUES (%s, %s, %s, %s)", 
                       (member_id, book_id, loan_date, return_date))
        conn.commit()
        messagebox.showinfo("Success", "Loan added successfully!", parent=dialog)
        dialog.destroy()
        fetch_loans()
    
    add_btn = tk.Button(buttons_frame, text="add", command=add_loan_from_dialog, width=10)
    add_btn.pack(side='right')
    
    # Cancel button
    cancel_btn = tk.Button(buttons_frame, text="X", command=dialog.destroy, width=3)
    cancel_btn.pack(side='right', padx=10)

def remove_loan():
    selected_item = loans_table.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a loan to remove!")
        return
    loan_id = loans_table.item(selected_item)['values'][0]
    
    # Confirm deletion
    if messagebox.askyesno("Confirm", "Are you sure you want to remove this loan?"):
        cursor.execute("DELETE FROM Loans WHERE LoanID = %s", (loan_id,))
        conn.commit()
        messagebox.showinfo("Success", "Loan removed successfully!")
        fetch_loans()

# --- Fines Tab ---
def show_fines():
    hide_all_frames()
    fines_frame.pack(fill='both', expand=True)
    fetch_fines()

def fetch_fines():
    for row in fines_table.get_children():
        fines_table.delete(row)
    cursor.execute("SELECT FineID, LoanID, Amount, FineDate FROM Fines")
    for fine in cursor.fetchall():
        fines_table.insert("", "end", values=fine)

def show_add_fine_dialog():
    dialog = show_dialog(root, "Add a Fine")
    
    # Dialog content
    content_frame = tk.Frame(dialog, padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    tk.Label(content_frame, text="Fine Management", font=("Arial", 14, "bold")).pack(pady=(0, 20))
    
    # Loan ID field
    tk.Label(content_frame, text="Loan ID", anchor="w").pack(fill='x')
    loan_id_entry = tk.Entry(content_frame)
    loan_id_entry.pack(fill='x', pady=(0, 10))
    
    # Amount field
    tk.Label(content_frame, text="Amount", anchor="w").pack(fill='x')
    amount_entry = tk.Entry(content_frame)
    amount_entry.pack(fill='x', pady=(0, 10))
    
    # Fine Date field
    tk.Label(content_frame, text="Fine Date", anchor="w").pack(fill='x')
    date_entry = tk.Entry(content_frame)
    date_entry.pack(fill='x', pady=(0, 10))
    date_entry.insert(0, "MM/DD/YY")  # Default format
    
    # Buttons frame
    buttons_frame = tk.Frame(content_frame)
    buttons_frame.pack(fill='x', pady=(10, 0))
    
    # Add button
    def add_fine_from_dialog():
        loan_id = loan_id_entry.get()
        amount = amount_entry.get()
        fine_date = date_entry.get()
        
        if not loan_id or not amount or not fine_date or fine_date == "MM/DD/YY":
            messagebox.showwarning("Input Error", "All fields are required!", parent=dialog)
            return
        
        try:
            amount = float(amount)
            cursor.execute("INSERT INTO Fines (LoanID, Amount, FineDate) VALUES (%s, %s, %s)", 
                           (loan_id, amount, fine_date))
            conn.commit()
            messagebox.showinfo("Success", "Fine added successfully!", parent=dialog)
            dialog.destroy()
            fetch_fines()
        except ValueError:
            messagebox.showerror("Input Error", "Amount must be a number!", parent=dialog)
    
    add_btn = tk.Button(buttons_frame, text="add", command=add_fine_from_dialog, width=10)
    add_btn.pack(side='right')
    
    # Cancel button
    cancel_btn = tk.Button(buttons_frame, text="X", command=dialog.destroy, width=3)
    cancel_btn.pack(side='right', padx=10)

def remove_fine():
    selected_item = fines_table.selection()
    if not selected_item:
        messagebox.showwarning("Selection Error", "Please select a fine to remove!")
        return
    fine_id = fines_table.item(selected_item)['values'][0]
    
    # Confirm deletion
    if messagebox.askyesno("Confirm", "Are you sure you want to remove this fine?"):
        cursor.execute("DELETE FROM Fines WHERE FineID = %s", (fine_id,))
        conn.commit()
        messagebox.showinfo("Success", "Fine removed successfully!")
        fetch_fines()

# --- GUI Setup ---
root = tk.Tk()
root.title("Library Management System")
root.geometry("900x650")  # Increased size for more content
root.configure(bg='#f5f5f5')  # Light background color

# --- Style Configuration ---
style = ttk.Style()
style.theme_use('clam')  # Modern looking theme
style.configure("Treeview", background="#ffffff", fieldbackground="#ffffff", foreground="black")
style.configure("Treeview.Heading", font=('Arial', 10, 'bold'))
style.map('Treeview', background=[('selected', '#2c82c9')])  # Blue selection color

# --- Main Layout ---
# Left sidebar
sidebar = tk.Frame(root, width=150, bg='#f0f0f0')  # Blue sidebar
sidebar.pack(side='left', fill='y')
sidebar.pack_propagate(False)  # Prevent sidebar from shrinking


# Navigation buttons
button_style = {'font': ('Arial', 10), 'bg': '#2c82c9', 'fg': 'white', 'bd': 0, 
                'activebackground': '#1e6091', 'activeforeground': 'white',
                'width': 15, 'pady': 10, 'anchor': 'w'}

# Add icons to buttons

#Home Image Button #####

# Load and resize the image
img = Image.open("icons/Logo-no_bg.png")  # Supports JPG, PNG, etc.
img = img.resize((80, 80))  # Resize if needed
home_icon = ImageTk.PhotoImage(img)

# Create Image Button
home_button = tk.Button(sidebar, image=home_icon, command=show_home, bg='#f0f0f0', borderwidth=0)
home_button.image = home_icon  # Prevent garbage collection
home_button.pack(pady=10)

###########################

#Members Image Button #####

# Create a Frame for the button and label
member_frame = tk.Frame(sidebar, bg='#f0f0f0')  # Matches sidebar background
member_frame.pack(pady=10)

# Load and resize the image
img = Image.open("icons/group.png")
img = img.resize((40, 40))  # Resize if needed
member_icon = ImageTk.PhotoImage(img)

# Create Image Button
member_button = tk.Button(member_frame, image=member_icon, command=show_members, bg='#f0f0f0', borderwidth=0)
member_button.image = member_icon  # Prevent garbage collection
member_button.pack()

# Add Label Below Image
member_label = tk.Label(member_frame, text="Member", bg='#f0f0f0', font=("Arial", 10))
member_label.pack()

###########################


#Book Image Button #####

# Create a Frame for the button and label
member_frame = tk.Frame(sidebar, bg='#f0f0f0')  # Matches sidebar background
member_frame.pack(pady=10)

# Load and resize the image
img = Image.open("icons/book.png")
img = img.resize((40, 40))  # Resize if needed
member_icon = ImageTk.PhotoImage(img)

# Create Image Button
member_button = tk.Button(member_frame, image=member_icon, command=show_books, bg='#f0f0f0', borderwidth=0)
member_button.image = member_icon  # Prevent garbage collection
member_button.pack()

# Add Label Below Image
member_label = tk.Label(member_frame, text="Books", bg='#f0f0f0', font=("Arial", 10))
member_label.pack()

###########################

#Reservation Image Button #####

# Create a Frame for the button and label
member_frame = tk.Frame(sidebar, bg='#f0f0f0')  # Matches sidebar background
member_frame.pack(pady=10)

# Load and resize the image
img = Image.open("icons/reservation.png")
img = img.resize((40, 40))  # Resize if needed
member_icon = ImageTk.PhotoImage(img)

# Create Image Button
member_button = tk.Button(member_frame, image=member_icon, command=show_reservations, bg='#f0f0f0', borderwidth=0)
member_button.image = member_icon  # Prevent garbage collection
member_button.pack()

# Add Label Below Image
member_label = tk.Label(member_frame, text="Reservations", bg='#f0f0f0', font=("Arial", 10))
member_label.pack()

###########################

#loans Image Button #####

# Create a Frame for the button and label
member_frame = tk.Frame(sidebar, bg='#f0f0f0')  # Matches sidebar background
member_frame.pack(pady=10)

# Load and resize the image
img = Image.open("icons/loan.png")
img = img.resize((40, 40))  # Resize if needed
member_icon = ImageTk.PhotoImage(img)

# Create Image Button
member_button = tk.Button(member_frame, image=member_icon, command=show_loans, bg='#f0f0f0', borderwidth=0)
member_button.image = member_icon  # Prevent garbage collection
member_button.pack()

# Add Label Below Image
member_label = tk.Label(member_frame, text="Loans", bg='#f0f0f0', font=("Arial", 10))
member_label.pack()

###########################

#Fines Image Button #####

# Create a Frame for the button and label
member_frame = tk.Frame(sidebar, bg='#f0f0f0')  # Matches sidebar background
member_frame.pack(pady=10)

# Load and resize the image
img = Image.open("icons/fines.png")
img = img.resize((40, 40))  # Resize if needed
member_icon = ImageTk.PhotoImage(img)

# Create Image Button
member_button = tk.Button(member_frame, image=member_icon, command=show_fines, bg='#f0f0f0', borderwidth=0)
member_button.image = member_icon  # Prevent garbage collection
member_button.pack()

# Add Label Below Image
member_label = tk.Label(member_frame, text="Fines", bg='#f0f0f0', font=("Arial", 10))
member_label.pack()

###########################


# Main content area
main_content = tk.Frame(root, bg='#f5f5f5')
main_content.pack(side='right', fill='both', expand=True, padx=20, pady=20)

# Hide all frames function
def hide_all_frames():
    home_frame.pack_forget()
    members_frame.pack_forget()
    books_frame.pack_forget()
    reservations_frame.pack_forget()
    loans_frame.pack_forget()
    fines_frame.pack_forget()

# --- Home Frame ---
home_frame = tk.Frame(main_content, bg='#f5f5f5')
tk.Label(home_frame, text="📗Welcome to Library Management System📗", 
         font=("Arial", 24, "bold"), bg='#f5f5f5').pack(pady=30)

# Welcome message
welcome_text = """
📚 Library Management System – Your All-in-One Library Solution

Elevate your library experience with our powerful and user-friendly Library Management System. 
Designed for efficiency, scalability, and ease of use, this comprehensive application empowers
you to effortlessly manage all aspects of your library operation:

✅ Member Management
📖 Book Management 
📅 Reservation System
🔄 Loan Tracking 
💸 Fine Management

Select an option from the sidebar to get started.
"""
tk.Label(home_frame, text=welcome_text, font=("Arial", 12), 
         bg='#f5f5f5', justify='left').pack(pady=20)

# --- Members Frame ---
members_frame = tk.Frame(main_content, bg='#f5f5f5')

# Header with search
header_frame = tk.Frame(members_frame, bg='#f5f5f5')
header_frame.pack(fill='x', pady=(0, 10))

tk.Label(header_frame, text="Members", font=("Arial", 20, "bold"), 
         bg='#f5f5f5').pack(side='left')

# Search box
search_frame = tk.Frame(header_frame, bg='#f5f5f5')
search_frame.pack(side='right')

search_entry = tk.Entry(search_frame, width=30, font=("Arial", 10))
search_entry.pack(side='left')
search_entry.insert(0, "Search for Members")

search_button = tk.Button(search_frame, text="🔍", font=("Arial", 10))
search_button.pack(side='left', padx=5)

# Action buttons
actions_frame = tk.Frame(members_frame, bg='#f5f5f5')
actions_frame.pack(fill='x', pady=10)

add_member_btn = tk.Button(actions_frame, text="Add a member", bg='#4CAF50', fg='white',
                           command=show_add_member_dialog)
add_member_btn.pack(side='left', padx=5)

remove_member_btn = tk.Button(actions_frame, text="remove a member", bg='#f44336', fg='white',
                             command=remove_member)
remove_member_btn.pack(side='left', padx=5)

# Members table
table_frame = tk.Frame(members_frame, bg='white', bd=1, relief='solid')
table_frame.pack(fill='both', expand=True)

members_table = ttk.Treeview(table_frame, columns=("MemberID", "Name", "Email", "MembershipDate"), show="headings", 
                            selectmode="browse")
members_table.pack(fill='both', expand=True)

# Define column widths
members_table.column("MemberID", width=80)
members_table.column("Name", width=150)
members_table.column("Email", width=200)
members_table.column("MembershipDate", width=120)

# Define column headings
for col in ("MemberID", "Name", "Email", "MembershipDate"):
    members_table.heading(col, text=col)

# Add scrollbar
members_scrollbar = ttk.Scrollbar(members_table, orient="vertical", command=members_table.yview)
members_table.configure(yscrollcommand=members_scrollbar.set)
members_scrollbar.pack(side='right', fill='y')

# --- Books Frame ---
books_frame = tk.Frame(main_content, bg='#f5f5f5')

# Header
tk.Label(books_frame, text="Books", font=("Arial", 20, "bold"), 
         bg='#f5f5f5').pack(anchor='nw', pady=(0, 0))

# Header with search
book_header_frame = tk.Frame(books_frame, bg='#f5f5f5')
book_header_frame.pack(fill='x', pady=(0, 0))


# Search box for Books
book_search_frame = tk.Frame(book_header_frame, bg='#f5f5f5')
book_search_frame.pack(side='right')

book_search_entry = tk.Entry(book_search_frame, width=30, font=("Arial", 10))
book_search_entry.pack(side='left')
book_search_entry.insert(1, "Search for Books")
book_search_entry.bind("<FocusIn>", lambda e: book_search_entry.delete(0, tk.END) if book_search_entry.get() == "Search for Books" else None)
book_search_entry.bind("<FocusOut>", lambda e: book_search_entry.insert(0, "Search for Books") if book_search_entry.get() == "" else None)
book_search_entry.bind("<Return>", search_books)


book_search_button = tk.Button(book_search_frame, text="🔍", font=("Arial", 10))
book_search_button.pack(side='left', padx=0)
book_search_button.config(command=search_books)

book_actions_frame = tk.Frame(books_frame, bg='#f5f5f5')
book_actions_frame.pack(fill='x', pady=0)

add_book_btn = tk.Button(book_actions_frame, text="Add a book", bg='#4CAF50', fg='white',
                         command=show_add_book_dialog)
add_book_btn.pack(side='left', padx=0)

remove_book_btn = tk.Button(book_actions_frame, text="remove a book", bg='#f44336', fg='white',
                           command=remove_book)
remove_book_btn.pack(side='left', padx=0)

# Books table
books_table_frame = tk.Frame(books_frame, bg='white', bd=1, relief='solid')
books_table_frame.pack(fill='both', expand=True)

books_table = ttk.Treeview(books_table_frame, columns=("BookID", "Title", "Author", "Genre", "AvailableCopies"), 
                          show="headings", selectmode="browse")
books_table.pack(fill='both', expand=True)

# Define column widths
books_table.column("BookID", width=80)
books_table.column("Title", width=200)
books_table.column("Author", width=100)
books_table.column("Genre", width=120)
books_table.column("AvailableCopies", width=100)

# Define column headings
for col in ("BookID", "Title", "Author", "Genre", "AvailableCopies"):
    books_table.heading(col, text=col)

# Add scrollbar
books_scrollbar = ttk.Scrollbar(books_table, orient="vertical", command=books_table.yview)
books_table.configure(yscrollcommand=books_scrollbar.set)
books_scrollbar.pack(side='right', fill='y')

# --- Reservations Frame ---
reservations_frame = tk.Frame(main_content, bg='#f5f5f5')

# Header
tk.Label(reservations_frame, text="Reservations", font=("Arial", 20, "bold"), 
         bg='#f5f5f5').pack(anchor='w', pady=(0, 10))

# Action buttons
reservation_actions_frame = tk.Frame(reservations_frame, bg='#f5f5f5')
reservation_actions_frame.pack(fill='x', pady=10)

add_reservation_btn = tk.Button(reservation_actions_frame, text="Add a reservation", bg='#4CAF50', fg='white',
                               command=show_add_reservation_dialog)
add_reservation_btn.pack(side='left', padx=5)

remove_reservation_btn = tk.Button(reservation_actions_frame, text="remove a reservation", bg='#f44336', fg='white',
                                  command=remove_reservation)
remove_reservation_btn.pack(side='left', padx=5)

# Reservations table
reservations_table_frame = tk.Frame(reservations_frame, bg='white', bd=1, relief='solid')
reservations_table_frame.pack(fill='both', expand=True)

reservations_table = ttk.Treeview(reservations_table_frame, 
                                 columns=("ReservationID", "MemberID", "BookID", "ReservationDate"), 
                                 show="headings", selectmode="browse")
reservations_table.pack(fill='both', expand=True)

# Define column widths
reservations_table.column("ReservationID", width=100)
reservations_table.column("MemberID", width=100)
reservations_table.column("BookID", width=100)
reservations_table.column("ReservationDate", width=150)

# Define column headings
for col in ("ReservationID", "MemberID", "BookID", "ReservationDate"):
    reservations_table.heading(col, text=col)

# Add scrollbar
reservations_scrollbar = ttk.Scrollbar(reservations_table, orient="vertical", command=reservations_table.yview)
reservations_table.configure(yscrollcommand=reservations_scrollbar.set)
reservations_scrollbar.pack(side='right', fill='y')

# --- Loans Frame ---
loans_frame = tk.Frame(main_content, bg='#f5f5f5')

# Header
tk.Label(loans_frame, text="Loans", font=("Arial", 20, "bold"), 
         bg='#f5f5f5').pack(anchor='w', pady=(0, 10))

# Action buttons
loan_actions_frame = tk.Frame(loans_frame, bg='#f5f5f5')
loan_actions_frame.pack(fill='x', pady=10)

add_loan_btn = tk.Button(loan_actions_frame, text="Add a loan", bg='#4CAF50', fg='white',
                         command=show_add_loan_dialog)
add_loan_btn.pack(side='left', padx=5)

remove_loan_btn = tk.Button(loan_actions_frame, text="Remove a loan", bg='#f44336', fg='white',
                           command=remove_loan)
remove_loan_btn.pack(side='left', padx=5)

# Loans table
loans_table_frame = tk.Frame(loans_frame, bg='white', bd=1, relief='solid')
loans_table_frame.pack(fill='both', expand=True)

loans_table = ttk.Treeview(loans_table_frame, 
                          columns=("LoanID", "MemberID", "BookID", "LoanDate", "ReturnDate"), 
                          show="headings", selectmode="browse")
loans_table.pack(fill='both', expand=True)

# Define column widths
loans_table.column("LoanID", width=80)
loans_table.column("MemberID", width=80)
loans_table.column("BookID", width=80)
loans_table.column("LoanDate", width=120)
loans_table.column("ReturnDate", width=120)

# Define column headings
for col in ("LoanID", "MemberID", "BookID", "LoanDate", "ReturnDate"):
    loans_table.heading(col, text=col)

# Add scrollbar
loans_scrollbar = ttk.Scrollbar(loans_table, orient="vertical", command=loans_table.yview)
loans_table.configure(yscrollcommand=loans_scrollbar.set)
loans_scrollbar.pack(side='right', fill='y')

# --- Fines Frame ---
fines_frame = tk.Frame(main_content, bg='#f5f5f5')

# Header
tk.Label(fines_frame, text="Fines", font=("Arial", 20, "bold"), 
         bg='#f5f5f5').pack(anchor='w', pady=(0, 10))

# Action buttons
fine_actions_frame = tk.Frame(fines_frame, bg='#f5f5f5')
fine_actions_frame.pack(fill='x', pady=10)

add_fine_btn = tk.Button(fine_actions_frame, text="Add a fine", bg='#4CAF50', fg='white',
                         command=show_add_fine_dialog)
add_fine_btn.pack(side='left', padx=5)

remove_fine_btn = tk.Button(fine_actions_frame, text="Remove a fine", bg='#f44336', fg='white',
                           command=remove_fine)
remove_fine_btn.pack(side='left', padx=5)

# Fines table
fines_table_frame = tk.Frame(fines_frame, bg='white', bd=1, relief='solid')
fines_table_frame.pack(fill='both', expand=True)

fines_table = ttk.Treeview(fines_table_frame, 
                          columns=("FineID", "LoanID", "Amount", "FineDate"), 
                          show="headings", selectmode="browse")
fines_table.pack(fill='both', expand=True)

# Define column widths
fines_table.column("FineID", width=80)
fines_table.column("LoanID", width=80)
fines_table.column("Amount", width=100)
fines_table.column("FineDate", width=120)

# Define column headings
for col in ("FineID", "LoanID", "Amount", "FineDate"):
    fines_table.heading(col, text=col)

# Add scrollbar
fines_scrollbar = ttk.Scrollbar(fines_table, orient="vertical", command=fines_table.yview)
fines_table.configure(yscrollcommand=fines_scrollbar.set)
fines_scrollbar.pack(side='right', fill='y')

# --- Search functionality ---
def search_members(event=None):
    search_text = search_entry.get().lower()
    if search_text == "search for members":
        return
    
    for item in members_table.get_children():
        members_table.delete(item)
    
    cursor.execute("SELECT MemberID, Name, Email, MembershipDate FROM Members WHERE Name LIKE %s OR Email LIKE %s", 
                  (f"%{search_text}%", f"%{search_text}%"))
    
    for member in cursor.fetchall():
        members_table.insert("", "end", values=member)

# Bind search functionality
search_entry.bind("<FocusIn>", lambda e: search_entry.delete(0, tk.END) if search_entry.get() == "Search for Members" else None)
search_entry.bind("<FocusOut>", lambda e: search_entry.insert(0, "Search for Members") if search_entry.get() == "" else None)
search_entry.bind("<Return>", search_members)
search_button.config(command=search_members)

# --- Report Generation ---
def generate_report():
    report_window = tk.Toplevel(root)
    report_window.title("Library Reports")
    report_window.geometry("600x500")
    report_window.transient(root)
    report_notebook = ttk.Notebook(report_window)
    report_notebook.pack(fill='both', expand=True, padx=10, pady=10)


    
    # Books summary tab
    books_report = tk.Frame(report_notebook, padx=15, pady=15)
    report_notebook.add(books_report, text="Books Summary")
    
    tk.Label(books_report, text="Books Statistics", font=("Arial", 16, "bold")).pack(pady=(0, 15))
    
    # Get book stats
    cursor.execute("SELECT COUNT(*) FROM Books")
    total_books = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(AvailableCopies) FROM Books")
    total_copies = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT Genre, COUNT(*) FROM Books GROUP BY Genre ORDER BY COUNT(*) DESC LIMIT 5")
    top_genres = cursor.fetchall()
    
    # Display stats
    stats_frame = tk.Frame(books_report)
    stats_frame.pack(fill='x', pady=10)
    
    tk.Label(stats_frame, text=f"Total Books: {total_books}", font=("Arial", 12)).pack(anchor='w')
    tk.Label(stats_frame, text=f"Total Copies: {total_copies}", font=("Arial", 12)).pack(anchor='w')
    
    tk.Label(books_report, text="Top Genres:", font=("Arial", 12, "bold")).pack(anchor='w', pady=(15, 5))
    
    for genre, count in top_genres:
        tk.Label(books_report, text=f"• {genre}: {count} books", font=("Arial", 11)).pack(anchor='w')
    
    # Members summary tab
    members_report = tk.Frame(report_notebook, padx=15, pady=15)
    report_notebook.add(members_report, text="Members Summary")


    
    tk.Label(members_report, text="Membership Statistics", font=("Arial", 16, "bold")).pack(pady=(0, 15))
    
    # Get member stats
    cursor.execute("SELECT COUNT(*) FROM Members")
    total_members = cursor.fetchone()[0]
    
    # Display stats
    tk.Label(members_report, text=f"Total Members: {total_members}", font=("Arial", 12)).pack(anchor='w')
    
    # Loans summary tab
    loans_report = tk.Frame(report_notebook, padx=15, pady=15)
    report_notebook.add(loans_report, text="Loans Summary")
    
    tk.Label(loans_report, text="Loan Statistics", font=("Arial", 16, "bold")).pack(pady=(0, 15))
    
    # Get loan stats
    cursor.execute("SELECT COUNT(*) FROM Loans")
    total_loans = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM Loans WHERE ReturnDate < CURDATE()")
    active_loans = cursor.fetchone()[0]
    
    # Display stats
    tk.Label(loans_report, text=f"Total Loans: {total_loans}", font=("Arial", 12)).pack(anchor='w')
    tk.Label(loans_report, text=f"Active Loans: {active_loans}", font=("Arial", 12)).pack(anchor='w')

# Add report button to home frame
report_btn = tk.Button(home_frame, text="Generate Reports", font=("Arial", 12), 
                      command=generate_report, bg='#2c82c9', fg='white', padx=10, pady=5)
report_btn.pack(pady=20)



# --- Main Menu Bar ---
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

# File menu
file_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="File", menu=file_menu)

file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)

# Management menu
manage_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Management", menu=manage_menu)
manage_menu.add_command(label="Members", command=show_members)
manage_menu.add_command(label="Books", command=show_books)
manage_menu.add_command(label="Reservations", command=show_reservations)
manage_menu.add_command(label="Loans", command=show_loans)
manage_menu.add_command(label="Fines", command=show_fines)

# Reports menu
report_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Reports", menu=report_menu)
report_menu.add_command(label="Generate Reports", command=generate_report)

# Help menu
help_menu = tk.Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Help", menu=help_menu)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", 
                                                                       "Library Management System v1.0\n\n"
                                                                       "A comprehensive solution for managing "
                                                                       "library resources, members, and operations."))

# For .png file (Cross-platform)
from PIL import Image, ImageTk
icon = Image.open("icons/GreenBook.png")
photo = ImageTk.PhotoImage(icon)
root.wm_iconphoto(True, photo)

# Show home frame by default
show_home()

# Start the main loop
root.mainloop()

# Close the database connection when the application is closed
conn.close()
