import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import date
import mysql.connector
from typing import List, Tuple, Any, Union

# --- 1. PYINSTALLER RESOURCE PATH HANDLER ---
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        # For development environment, use the current directory
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Handle Pillow import safely (Required for logo) ---
try:
    from PIL import Image, ImageTk
except ImportError:
    tk.Tk().withdraw()
    messagebox.showerror(
         "Dependency Error",
        "The 'Pillow' library is required for this application.\n\nInstall it by running:\n  pip install Pillow"
    )
    sys.exit(1)

# =================================================================
#                       2. DATABASE HANDLER SECTION
# =================================================================

# IMPORTANT: Replace these placeholders with your actual MySQL credentials
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'r2d2c3pobb-8', # Your specific password
    'database': 'library'
}

def get_db_connection() -> Union[mysql.connector.MySQLConnection, str]:
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            print("Successfully connected to MySQL database.")
            initialize_db(conn)
            return conn
    except mysql.connector.Error as err:
        error_message = f"Error: Failed to connect to MySQL: {err}"
        print(error_message)
        return error_message
    
    return "Error: Unknown database connection failure."

def initialize_db(conn: mysql.connector.MySQLConnection):
    """Creates the 'books' table if it doesn't already exist."""
    if not conn:
        return

    cursor = conn.cursor()
    # ADDED student_class column (index 6) to store the student's class/grade
    create_table_query = """
    CREATE TABLE IF NOT EXISTS books (
        ISBN VARCHAR(20),
        bookID VARCHAR(50) PRIMARY KEY,
        Title VARCHAR(255) NOT NULL,
        author_name VARCHAR(255) NOT NULL,
        issueStatus VARCHAR(50) DEFAULT 'Available',
        issueDate DATE NULL,
        issuedStudentID VARCHAR(50) NULL,
        student_class VARCHAR(50) NULL 
    )
    """
    try:
        cursor.execute(create_table_query)
        conn.commit()
    except mysql.connector.Error as err:
        print(f"Error creating table: {err}")
    finally:
        cursor.close()

def fetch_all_books() -> Union[List[Tuple[Any, ...]], str]:
    """Retrieves all books from the database. Handles NULL values and new column."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    
    # 8 COLUMNS MUST BE SELECTED HERE
    query = "SELECT ISBN, bookID, Title, author_name, issueStatus, issueDate, issuedStudentID, student_class FROM books"
    
    try:
        cursor.execute(query)
        books = cursor.fetchall()
        formatted_books = []
        for book in books:
            book_list = list(book)
            
            # CRITICAL CHECK: Ensure the tuple 'book' has exactly 8 elements
            if len(book_list) != 8:
                print(f"DEBUG: Found {len(book_list)} columns, expected 8.")
                # If this happens, your database structure or connector is misconfigured.
                # Attempt to proceed, but expect errors.
                
            # 1. ISBN (Index 0)
            book_list[0] = book_list[0] if book_list[0] not in (None, 'None') else '-N/A-'
            
            # Indices 1, 2, 3 (Book ID, Title, Author) are usually safe.
            
            # 2. issueStatus (Index 4)
            book_list[4] = book_list[4] if book_list[4] not in (None, 'None') else 'Available'
            
            # 3. issueDate (Index 5)
            book_list[5] = book_list[5].strftime("%Y-%m-%d") if book_list[5] else ""
            
            # 4. issuedStudentID (Index 6)
            book_list[6] = book_list[6] if book_list[6] else ""
            
            # 5. student_class (Index 7) - The final column
            book_list[7] = book_list[7] if book_list[7] else ""
            
            formatted_books.append(tuple(book_list))
        return formatted_books
    except mysql.connector.Error as err:
        return f"Error: Could not fetch books: {err}"
    finally:
        cursor.close()
        if conn and conn.is_connected():
            conn.close()

def fetch_book_by_id(book_id: str) -> Union[Tuple, str]:
    """Fetches a single book by its ID for the edit form. Includes new student_class column."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    
    # 7 COLUMNS ARE SELECTED HERE:
    query = "SELECT ISBN, bookID, Title, author_name, issueDate, issuedStudentID, student_class FROM books WHERE bookID = %s"
    
    try:
        cursor.execute(query, (book_id,))
        book = cursor.fetchone() 
        
        # If 'book' is only 6 items long here, the SELECT query is wrong, OR
        # the 'ISBN' column doesn't exist in your 'books' table in the database.
        
        if not book:
            return f"Error: No book found with ID: {book_id}"
        
        book_list = list(book)
        # ISBN (index 0)
        book_list[0] = book_list[0] if book_list[0] not in (None, 'None') else ''
        # issueDate (index 4)
        book_list[4] = book_list[4].strftime("%Y-%m-%d") if book_list[4] else ""
        # issuedStudentID (index 5)
        book_list[5] = book_list[5] if book_list[5] else ""
        # student_class (index 6) - NEW
        book_list[6] = book_list[6] if book_list[6] else ""
        
        # The returned tuple must have 7 elements for the GUI to unpack it.
        return tuple(book_list) 
    except mysql.connector.Error as err:
        return f"Error fetching book: {err}"
    finally:
        cursor.close()
        if conn and conn.is_connected():
            conn.close()

def fetch_all_student_classes():
    """Fetches all unique student classes for the search dropdown."""
    conn = get_db_connection()
    if isinstance(conn, str): return conn
    try:
        cursor = conn.cursor()
        # Ensure we only pull non-empty, non-null, and non-'General' strings to keep the list clean
        cursor.execute("SELECT student_class FROM books WHERE student_class IS NOT NULL AND student_class != '' ORDER BY student_class")
        # Flatten the list of tuples for the Combobox
        return [row[0] for row in cursor.fetchall()]
    except sqlite3.Error as e:
        return f"Error fetching student classes: {e}"
    finally:
        conn.close()

def add_new_book(book_isbn: str, book_id: str, title: str, author: str) -> str:
    """Adds a new book record with default status 'Available'."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    # student_class will default to NULL
    query = "INSERT INTO books (ISBN, bookID, Title, author_name, issueStatus) VALUES (%s, %s, %s, %s, %s)"
    try:
        cursor.execute(query, (book_isbn, book_id, title, author, 'Available'))
        conn.commit()
        return f"Book '{title}' successfully added with ID {book_id} and ISBN {book_isbn}."
    except mysql.connector.Error as err:
        conn.rollback()
        return f"Error adding book: {err}"
    finally:
        cursor.close()

def update_book_details(original_id: str, **updates) -> str:
    """Updates book details, including the new student_class field."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    
    set_clauses = []
    params = []
    
    # Check if a status update is implied (based on issueDate/studentID)
    is_issued = bool(updates.get('new_issue_date')) and bool(updates.get('new_student_id'))

    # Update bookID if it changed
    if updates.get('new_book_id') and updates['new_book_id'] != original_id:
        set_clauses.append("bookID = %s")
        params.append(updates['new_book_id'])

    # Update Title
    if updates.get('new_title'):
        set_clauses.append("Title = %s")
        params.append(updates['new_title'])
        
    # Update Author
    if updates.get('new_author'):
        set_clauses.append("author_name = %s")
        params.append(updates['new_author'])

    # Handle Issue Status update
    if is_issued:
        set_clauses.append("issueStatus = %s")
        params.append('Issued')
        set_clauses.append("issueDate = %s")
        params.append(updates['new_issue_date'])
        set_clauses.append("issuedStudentID = %s")
        params.append(updates['new_student_id'])
        
        # NEW COLUMN: student_class
        set_clauses.append("student_class = %s")
        # Use None if the class is an empty string, allowing NULL in DB
        class_param = updates.get('new_student_class') or None
        params.append(class_param) 
    else:
        # Mark as Available (clearing issue details)
        set_clauses.append("issueStatus = %s")
        params.append('Available')
        set_clauses.append("issueDate = NULL") # Use NULL for date
        set_clauses.append("issuedStudentID = NULL") # Use NULL for studentID
        set_clauses.append("student_class = NULL") # NEW: Clear student_class
    
    # Remove NULL/empty set clauses if they are handled by the is_issued logic
    final_set_clauses = [c for c in set_clauses if "NULL" in c or "%s" in c] 
    
    if not final_set_clauses:
        return "No changes detected to update."

    # Construct the final query
    set_clause_str = ", ".join(final_set_clauses)
    query = f"UPDATE books SET {set_clause_str} WHERE bookID = %s"
    
    # Append the original ID for the WHERE clause
    params.append(original_id) 

    try:
        # The complex logic below handles the mixing of %s and NULL keywords.
        if "NULL" in set_clause_str:
            # Re-run logic to handle NULL correctly for execution
            null_handled_params = []
            final_set_parts = []
            
            # Reconstruct based on parameter list order (excluding original_id for now)
            param_index = 0
            for i, clause in enumerate(set_clauses):
                # ADDED 'student_class = NULL' check
                if clause == "issueDate = NULL" or clause == "issuedStudentID = NULL" or clause == "student_class = NULL":
                    final_set_parts.append(clause)
                elif clause.endswith("= %s"):
                    # Check if the parameter itself is None (from the 'Issued' logic, e.g., student_class=None)
                    if params[param_index] is not None:
                         final_set_parts.append(clause)
                         null_handled_params.append(params[param_index])
                    else:
                         # If param is None, it means we should force NULL for that column in the query string
                         if 'student_class' in clause:
                             final_set_parts.append("student_class = NULL")
                         else:
                             # For Title/Author/ID which are NOT NULL, keep the original logic (shouldn't be None)
                             final_set_parts.append(clause)
                             null_handled_params.append(params[param_index])
                             
                    param_index += 1
                elif "issueStatus" in clause and 'Issued' in params[param_index]:
                    final_set_parts.append(clause)
                    null_handled_params.append(params[param_index])
                    param_index += 1
                elif "issueStatus" in clause and 'Available' in params[param_index]:
                    final_set_parts.append(clause)
                    null_handled_params.append(params[param_index])
                    param_index += 1
            
            final_set_clause_str = ", ".join(final_set_parts)
            query = f"UPDATE books SET {final_set_clause_str} WHERE bookID = %s"
            null_handled_params.append(original_id)

            cursor.execute(query, tuple(null_handled_params))
        else:
            # Standard execution if no NULL resets are involved
            cursor.execute(query, tuple(params))
            
        conn.commit()
        if cursor.rowcount == 0:
            return f"Warning: Book ID {original_id} not found or no changes were made."
        return f"Book ID {original_id} details successfully updated."
    except mysql.connector.Error as err:
        conn.rollback()
        return f"Error updating book: {err}"
    finally:
        cursor.close()

def borrow_book_record(book_id: str, student_id: str, student_class: str) -> str:
    """Updates book status to 'Issued' with current date, student ID, and student class."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    today = date.today()
    
    # ADDED student_class to the query
    query = "UPDATE books SET issueStatus = %s, issueDate = %s, issuedStudentID = %s, student_class = %s WHERE bookID = %s"
    
    # Use None if student_class is empty, so it maps to NULL in the database
    class_param = student_class if student_class else None
    
    try:
        # ADDED class_param to the execution tuple
        cursor.execute(query, ('Issued', today, student_id, class_param, book_id))
        conn.commit()
        if cursor.rowcount == 0:
            return f"Error: Book ID {book_id} not found."
        return f"Book ID {book_id} successfully issued to Student {student_id} ({student_class})."
    except mysql.connector.Error as err:
        conn.rollback()
        return f"Error issuing book: {err}"
    finally:
        cursor.close()

def return_book_record(book_id: str) -> str:
    """Updates book status to 'Available' and clears issue details, including student class."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    # Setting status back to 'Available' and clearing issue details
    # ADDED student_class = NULL
    query = "UPDATE books SET issueStatus = %s, issueDate = NULL, issuedStudentID = NULL, student_class = NULL WHERE bookID = %s AND issueStatus = %s"
    try:
        cursor.execute(query, ('Available', book_id, 'Issued'))
        conn.commit()
        if cursor.rowcount == 0:
            return f"Error: Book ID {book_id} not found or was not currently issued."
        return f"Book ID {book_id} successfully marked as Available."
    except mysql.connector.Error as err:
        conn.rollback()
        return f"Error returning book: {err}"
    finally:
        cursor.close()

def delete_book_by_id(book_id: str) -> str:
    """Deletes a book record by its ID."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    query = "DELETE FROM books WHERE bookID = %s"
    try:
        cursor.execute(query, (book_id,))
        conn.commit()
        if cursor.rowcount == 0:
            return f"Error: Book ID {book_id} not found."
        return f"Book ID {book_id} successfully deleted."
    except mysql.connector.Error as err:
        conn.rollback()
        return f"Error deleting book: {err}"
    finally:
        cursor.close()

def search_books(search_type: str, search_term: str) -> Union[List[Tuple[Any, ...]], str]:
    """Searches books based on type and term. Handles NULL status conversion and new column."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn

    # CRITICAL FIX: Ensure 'Book No:' (with colon) maps to the 'bookID' column
    # The 'Book No:' key matches the value used in the GUI's OptionMenu.
    column_map = {'Title': 'Title', 'Author': 'author_name', 'Book ID': 'bookID', 
                  'Book No:': 'bookID', 'Status': 'issueStatus', 
                  'Student/Teacher Class': 'student_class', 'ISBN': 'ISBN'}
    column_name = column_map.get(search_type)

    if not column_name:
        return "Error: Invalid search type."
    
    cursor = conn.cursor()
    
    # CRITICAL FIX: SELECT ALL 8 COLUMNS IN THE CORRECT ORDER (ISBN first) for the Treeview
    # ORDER: ISBN, bookID, Title, author_name, issueStatus, issueDate, issuedStudentID, student_class
    query = f"SELECT ISBN, bookID, Title, author_name, issueStatus, issueDate, issuedStudentID, student_class FROM books WHERE {column_name} LIKE %s"

    partial_search_fields = ('Title', 'Author', 'Book ID', 'Book No:', 'Status', 'Student Class', 'ISBN')
    param = f"%{search_term}%" if search_type in partial_search_fields else search_term

    try:
        cursor.execute(query, (param,))
        results = cursor.fetchall()

        if not results:
            return "No records found matching your search."

        formatted_results = []
        for book in results:
            book_list = list(book)
            
            # Ensure the tuple has 8 elements before processing
            if len(book_list) != 8:
                 print(f"DEBUG: Search returned {len(book_list)} columns, expected 8.")
                 continue # Skip this row if unexpected size
            
            # --- Formatting the 8 columns (Indices match the SELECT query order) ---
            # Index 0: ISBN 
            book_list[0] = book_list[0] if book_list[0] not in (None, 'None') else '-N/A-'
            
            # Index 4: issueStatus
            book_list[4] = book_list[4] if book_list[4] not in (None, 'None') else 'Available'
            
            # Index 5: issueDate
            book_list[5] = book_list[5].strftime("%Y-%m-%d") if book_list[5] else ""
            
            # Index 6: issuedStudentID
            book_list[6] = book_list[6] if book_list[6] else ""
            
            # Index 7: student_class
            book_list[7] = book_list[7] if book_list[7] else ""
            
            formatted_results.append(tuple(book_list))
            
        return formatted_results
    
    except mysql.connector.Error as err:
        return f"Error searching books: {err}"
    finally:
        cursor.close()
        if conn and conn.is_connected():
            conn.close()

# =================================================================
#                       3. GUI APPLICATION SECTION
# =================================================================

class LibraryApp:
    
    # ------------------ HANDLER/LOGIC METHODS ------------------
    
    def populate_main_treeview(self):
        """Fetches all books and displays them in the main Treeview."""
        for item in self.main_tree.get_children():
            self.main_tree.delete(item)
            
        books = fetch_all_books()
        
        if isinstance(books, str):
            messagebox.showerror("Database Error", books)
            return
            
        # Inserts the 7-column data (including Student Class)
        for book in books:
            self.main_tree.insert('', tk.END, values=book)

    def add_new_book_gui(self):
        """Handles the 'Add Book' button click."""
        book_isbn = self.add_book_isbn_var.get().strip()
        book_id = self.add_book_id_var.get().strip()
        title = self.add_title_var.get().strip()
        author = self.add_author_var.get().strip()

        if not all([book_id, title, author]):
            messagebox.showwarning("Input Error", "All fields (ISBN, ID, Title, Author) are required for adding a book.")
            return

        result = add_new_book(book_isbn, book_id, title, author)
        
        if result.startswith("Error"):
            messagebox.showerror("Add Book Failed", result)
        else:
            messagebox.showinfo("Success", result)
            self.add_book_isbn_var.set("")
            self.add_book_id_var.set("")
            self.add_title_var.set("")
            self.add_author_var.set("")
            self.populate_main_treeview()
            
    def delete_specified_book_gui(self):
        """Deletes the book specified by ID from the Add/Delete tab."""
        book_id = self.delete_book_id_var.get().strip()
        
        if not book_id:
            messagebox.showwarning("Input Error", "Please enter a Book ID to delete.")
            return
            
        if messagebox.askyesno("Confirm Delete", f"Are you absolutely sure you want to permanently delete Book ID: {book_id}?"):
            result = delete_book_by_id(book_id)
            if result.startswith("Error"):
                messagebox.showerror("Delete Failed", result)
            else:
                messagebox.showinfo("Success", result)
                self.delete_book_id_var.set("") 
                self.populate_main_treeview()
                
    def borrow_book_gui(self):
        """Handles the 'Borrow Book' button click. Now includes student class from Combobox."""
        # --- ADD THIS LINE ---
        book_id = self.manage_book_id_var.get().strip()
        # ---------------------
        student_id = self.manage_student_id_var.get().strip()
        student_class = self.manage_student_class_var.get().strip() # Fetched from Combobox

        # Check for required fields (now book_id is defined)
        if not all([book_id, student_id]):
            messagebox.showwarning("Input Error", "Book ID and Student ID are required to borrow.")
            return

        # Passing student_class to the database handler
        result = borrow_book_record(book_id, student_id, student_class)
        
        if result.startswith("Error"):
            messagebox.showerror("Borrow Failed", result)
        else:
            messagebox.showinfo("Success", result)
            
        # Clear fields
        self.manage_book_id_var.set("")
        self.manage_student_id_var.set("")
        self.manage_student_class_var.set("") # Clear new field (set back to default blank)
        self.populate_main_treeview()
            
    def return_book_gui(self):
        """Marks a book as available and clears all issue details."""
        book_id = self.return_book_id_entry.get().strip()
        
        if not book_id:
            messagebox.showwarning("Input Error", "Book ID is required to return.")
            return

        # return_book_record now clears student_class as well
        result = return_book_record(book_id)
        
        if result.startswith("Error"):
            messagebox.showerror("Return Failed", result)
        else:
            messagebox.showinfo("Success", result)
            self.return_book_id_entry.delete(0, tk.END)
            self.populate_main_treeview()

    def fetch_book_to_edit(self):
            """Fetches book details including student class and populates the edit fields."""
            book_id = self.edit_original_id_var.get().strip()
            if not book_id:
                messagebox.showwarning("Input Error", "Please enter a Book ID to fetch details.")
                return

            # Fetches: ISBN, ID, Title, Author, IssueDate, StudentID, StudentClass (7 items now)
            book_data = fetch_book_by_id(book_id)
            
            if isinstance(book_data, str):
                messagebox.showerror("Fetch Failed", book_data)
                # Clear all edit fields if fetch fails
                self.edit_new_isbn_var.set("")
                self.edit_new_id_var.set("")
                self.edit_title_var.set("")
                self.edit_author_var.set("")
                self.edit_issue_date_var.set("")
                self.edit_issued_student_id_var.set("")
                self.edit_student_class_var.set("")
                return

            # Unpack the 7 returned values
            fetched_isbn, fetched_id, title, author, issue_date, student_id, student_class = book_data

            # The set methods populate the fields, using "" for NULL values from DB handler
            self.edit_original_id_var.set(fetched_id) # Set original ID for reference
            
            # --- FIX APPLIED HERE ---
            self.edit_new_isbn_var.set(fetched_isbn) # <--- CORRECT: Sets ISBN to the actual fetched ISBN
            # ------------------------
            
            self.edit_new_id_var.set(fetched_id) 
            self.edit_title_var.set(title)
            self.edit_author_var.set(author)
            self.edit_issue_date_var.set(issue_date)
            self.edit_issued_student_id_var.set(student_id)
            self.edit_student_class_var.set(student_class) # NEW SET (sets Combobox value)

    def update_book_gui(self):
        """Handles the 'Update Book Details' button click, now including student class."""
        original_id = self.edit_original_id_var.get().strip()
        new_isbn = self.edit_new_isbn_var.get().strip()
        new_id = self.edit_new_id_var.get().strip()
        new_title = self.edit_title_var.get().strip()
        new_author = self.edit_author_var.get().strip()
        new_issue_date = self.edit_issue_date_var.get().strip()
        new_student_id = self.edit_issued_student_id_var.get().strip()
        new_student_class = self.edit_student_class_var.get().strip() # NEW (from Combobox)
        
        if not original_id:
            messagebox.showwarning("Input Error", "Please fetch a book ID first.")
            return
        
        if not (new_id and new_title and new_author):
            messagebox.showwarning("Input Error", "Book ID, Title, and Author cannot be empty.")
            return

        # Basic Date validation: YYYY-MM-DD format (or empty)
        if new_issue_date and not (len(new_issue_date) == 10 and new_issue_date[4] == '-' and new_issue_date[7] == '-'):
             messagebox.showwarning("Input Error", "Issue Date must be in YYYY-MM-DD format, or left blank.")
             return

        # Status consistency check for Issued/Available
        is_issue_date_filled = bool(new_issue_date)
        is_student_id_filled = bool(new_student_id)
        
        # If one is filled but not the other, it's an error.
        if is_issue_date_filled != is_student_id_filled:
             messagebox.showwarning("Status Error", "To mark a book as 'Issued', both the Issue Date and Issued Student ID must be filled. To mark as 'Available', both must be empty.")
             return
            
        updates = {
            'new_book_id': new_id, 
            'new_title': new_title, 
            'new_author': new_author,
            'new_issue_date': new_issue_date, 
            'new_student_id': new_student_id,
            'new_student_class': new_student_class # NEW ADDITION
        }
        
        result = update_book_details(original_id, **updates)
        
        if result.startswith("Error"):
            messagebox.showerror("Update Failed", result)
        else:
            messagebox.showinfo("Success", result)
            # Clear fields and refresh list
            self.edit_original_id_var.set("")
            self.edit_new_isbn_var.set("")
            self.edit_new_id_var.set("")
            self.edit_title_var.set("")
            self.edit_author_var.set("")
            self.edit_issue_date_var.set("")
            self.edit_issued_student_id_var.set("")
            self.edit_student_class_var.set("") # NEW CLEAR
            self.populate_main_treeview()

    def search_books_gui(self):
        """Handles the 'Search' button click and displays results."""
        search_type = self.search_type_var.get()
        search_term = self.search_term_var.get().strip()
        
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        if not search_term:
            messagebox.showwarning("Input Error", "Please enter a search term.")
            return
            
        results = search_books(search_type, search_term)
        
        if isinstance(results, str):
            messagebox.showinfo("Search Results", results)
            return

        # Inserts the 7-column data (including Student Class)
        for book in results:
            self.search_tree.insert('', tk.END, values=book)
            
            
    # ------------------ TAB CREATION METHODS ------------------

    def _create_view_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="View All Books")

        frame = ttk.Frame(tab)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        # UPDATED: Added 'Student Class' to the Treeview headers
        cols = ('ISBN', 'Book No.', 'Title', 'Author', 'Status', 'Issue Date', 'Student/Teacher ID', 'Student/Teacher Class')
        self.main_tree = ttk.Treeview(frame, columns=cols, show='headings', height=20)
        
        # Adjusted column widths for the new column
        column_widths = {'ISBN': 80, 'Book No:':80, 'Title': 200, 'Author': 150, 'Status': 80, 'Issue Date': 100, 'Student/Teacher ID': 80, 'Student/Teacher Class': 100}
        for col in cols:
            self.main_tree.heading(col, text=col)
            self.main_tree.column(col, width=column_widths.get(col, 10), anchor='w')
            
        self.main_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.main_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.main_tree.configure(yscrollcommand=scrollbar.set)

        button_frame = ttk.Frame(tab)
        button_frame.pack(pady=10)
        
        refresh_button = ttk.Button(button_frame, text="Refresh List", command=self.populate_main_treeview)
        refresh_button.pack(side=tk.LEFT, padx=10)
        
        
    def _create_add_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Add/Delete Book")
        main_frame = ttk.Frame(tab, padding="20")
        main_frame.pack(fill="both", expand=True)

        # ADD BOOK SECTION
        add_frame = ttk.LabelFrame(main_frame, text=" Add New Book ", padding="15")
        add_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(add_frame, text="ISBN:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        ttk.Entry(add_frame, textvariable=self.add_book_isbn_var, width=40).grid(row=0, column=1, padx=10, pady=10, sticky='w')

        ttk.Label(add_frame, text="Book ID:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=10, sticky='w')
        ttk.Entry(add_frame, textvariable=self.add_book_id_var, width=40).grid(row=1, column=1, padx=10, pady=10, sticky='w')

        ttk.Label(add_frame, text="Title:", font=("Helvetica", 12)).grid(row=2, column=0, padx=10, pady=10, sticky='w')
        ttk.Entry(add_frame, textvariable=self.add_title_var, width=40).grid(row=2, column=1, padx=10, pady=10, sticky='w')

        ttk.Label(add_frame, text="Author:", font=("Helvetica", 12)).grid(row=3, column=0, padx=10, pady=10, sticky='w')
        ttk.Entry(add_frame, textvariable=self.add_author_var, width=40).grid(row=3, column=1, padx=10, pady=10, sticky='w')

        ttk.Button(add_frame, text="Add Book to Database", command=self.add_new_book_gui).grid(row=4, column=2, padx=10, pady=20, sticky='w')

        # DELETE BOOK SECTION
        delete_frame = ttk.LabelFrame(main_frame, text=" Delete Book ", padding="15")
        delete_frame.pack(fill="x", padx=10, pady=20)
        
        # --- FIXED LABEL: Changed "ISBN to Delete:" to "Book ID to Delete:" ---
        ttk.Label(delete_frame, text="Book ID to Delete:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=10, sticky='w')
        # ---------------------------------------------------------------------

        ttk.Entry(delete_frame, textvariable=self.delete_book_id_var, width=40).grid(row=0, column=1, padx=10, pady=10, sticky='w')
        ttk.Button(delete_frame, text="Delete Book Permanently", command=self.delete_specified_book_gui).grid(row=1, column=1, padx=10, pady=20, sticky='w')


    def _create_manage_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Borrow/Return")
        
        main_frame = ttk.Frame(tab, padding="20")
        main_frame.pack(fill="both", expand=True)
        
        # Borrow Section
        borrow_frame = ttk.LabelFrame(main_frame, text=" Borrow Book ", padding="15")
        borrow_frame.pack(fill="x", padx=10, pady=10)

        ttk.Label(borrow_frame, text="Book No:", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(borrow_frame, textvariable=self.manage_book_id_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Label(borrow_frame, text="Student/Teacher ID:", font=("Helvetica", 11)).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(borrow_frame, textvariable=self.manage_student_id_var, width=30).grid(row=1, column=1, padx=5, pady=5, sticky='w')
        
        # Student Class - Combobox
        ttk.Label(borrow_frame, text="Student/Teacher Class:", font=("Helvetica", 11)).grid(row=2, column=0, padx=5, pady=5, sticky='w')
        class_combobox = ttk.Combobox(borrow_frame, 
                                      textvariable=self.manage_student_class_var, 
                                      values=self.class_options, 
                                      state='readonly', # Prevents free-text entry
                                      width=28) 
        class_combobox.grid(row=2, column=1, padx=5, pady=5, sticky='w')
        class_combobox.set("") # Default selection (empty string)
        
        ttk.Button(borrow_frame, text="Borrow Book", command=self.borrow_book_gui).grid(row=3, column=1, padx=5, pady=10, sticky='w')
        
        # Return Section
        return_frame = ttk.LabelFrame(main_frame, text=" Return Book ", padding="15")
        return_frame.pack(fill="x", padx=10, pady=20)
        
        ttk.Label(return_frame, text="Book No:", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.return_book_id_entry = ttk.Entry(return_frame, width=30)
        self.return_book_id_entry.grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        ttk.Button(return_frame, text="Return Book", command=self.return_book_gui).grid(row=1, column=1, padx=5, pady=10, sticky='w')

    def _create_edit_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Edit Book")
        
        main_frame = ttk.Frame(tab, padding="20")
        main_frame.pack(fill="both", expand=True)

        # 1. Fetch Section
        fetch_frame = ttk.LabelFrame(main_frame, text=" Fetch Book Details ", padding="15")
        fetch_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Label(fetch_frame, text="Enter Book No. to Edit:", font=("Helvetica", 11)).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        ttk.Entry(fetch_frame, textvariable=self.edit_original_id_var, width=30).grid(row=0, column=1, padx=5, pady=5, sticky='w')
        
        # This button is now fully functional!
        ttk.Button(fetch_frame, text="Fetch Details", command=self.fetch_book_to_edit).grid(row=0, column=2, padx=10, pady=5)
        
        # 2. Update Section
        update_frame = ttk.LabelFrame(main_frame, text=" Update Details ", padding="15")
        update_frame.pack(fill="x", padx=10, pady=10)
        
        fields = [
            ("New ISBN:", self.edit_new_isbn_var),
            ("New Book No:", self.edit_new_id_var),
            ("New Title:", self.edit_title_var),
            ("New Author:", self.edit_author_var),
            ("New Issue Date (YYYY-MM-DD):", self.edit_issue_date_var),  
            ("New Issued Student/Teacher ID:", self.edit_issued_student_id_var),
            ("New Student/Teacher Class:", self.edit_student_class_var) # This one will be the Combobox
        ]
        
        # Layout for the input fields
        for i, (text, var) in enumerate(fields):
            ttk.Label(update_frame, text=text, font=("Helvetica", 11)).grid(row=i, column=0, padx=5, pady=5, sticky='w')
            
            # Use Combobox only for the Student Class field
            if text == "New Student Class:":
                # Student Class - Combobox
                combobox = ttk.Combobox(update_frame, 
                                        textvariable=var, 
                                        values=self.class_options, 
                                        state='readonly', # Prevents free-text entry
                                        width=38)
                combobox.grid(row=i, column=1, padx=5, pady=5, sticky='w')
            else:
                # Use standard Entry for all other fields
                ttk.Entry(update_frame, textvariable=var, width=40).grid(row=i, column=1, padx=5, pady=5, sticky='w')
            
        ttk.Button(update_frame, text="Update Book Details", command=self.update_book_gui).grid(row=len(fields), column=1, padx=5, pady=10, sticky='w')
        
        # NOTE UPDATED
        ttk.Label(update_frame, text="NOTE: To mark book as 'Available', clear Issue Date, Student/Teacher ID, and Student/Teacher Class fields.", foreground="gray", font=("Helvetica", 9, "italic")).grid(row=len(fields) + 1, column=0, columnspan=2, pady=5)


    def _create_search_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Search Books")
        
        # Search Controls
        search_frame = ttk.Frame(tab, padding="10")
        search_frame.pack(fill="x")
        
        ttk.Label(search_frame, text="Search By:", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        
        search_options = ['Title', 'Author', 'ISBN', 'Book No:', 'Status', 'Student/Teacher Class']
        self.search_type_var.set("Title") # Set initial value
        ttk.OptionMenu(search_frame, self.search_type_var, self.search_type_var.get(), *search_options).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(search_frame, text="Term:", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=5)
        ttk.Entry(search_frame, textvariable=self.search_term_var, width=30).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(search_frame, text="Search", command=self.search_books_gui).pack(side=tk.LEFT, padx=10)
        
        # Results Treeview
        results_frame = ttk.Frame(tab)
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # UPDATED: Added 'Student Class' to the Treeview headers
        cols = ('ISBN', 'Book No:', 'Title', 'Author', 'Status', 'Issue Date', 'Student/Teacher ID', 'Student/Teacher Class')
        self.search_tree = ttk.Treeview(results_frame, columns=cols, show='headings', height=20)
        
        # Adjusted column widths for the new column
        column_widths = {'ISBN': 80, 'Book No:':80, 'Title': 200, 'Author': 150, 'Status': 80, 'Issue Date': 100, 'Student/Teacher ID': 80, 'Student/Teacher Class': 100}
        for col in cols:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=column_widths.get(col, 10), anchor='w')
            
        self.search_tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=self.search_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.search_tree.configure(yscrollcommand=scrollbar.set)
        
        
    # ------------------ INITIALIZATION ------------------
    
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System - India International School")
        self.root.geometry("1000x700")

        # --- ICON LOADING ---
        try:
            icon_path = resource_path("library.ico")
            self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"[Icon Error] Could not set window icon: {e}")

        # --- COLOR SCHEME & STYLE ---
        self.colors = {
            "primary": "#1E3A8A", "secondary": "#E0E7FF", "accent": "#3B82F6", "text_light": "#FFFFFF", "text_dark": "#1E293B"
        }
        self.root.configure(bg=self.colors["secondary"])
        style = ttk.Style(self.root)
        style.theme_use("clam")
        style.configure("Treeview", background="white", foreground=self.colors["text_dark"], rowheight=25, fieldbackground="white", bordercolor=self.colors["secondary"])
        style.map("Treeview", background=[("selected", self.colors["accent"])])
        style.configure("TButton", font=("Helvetica", 10, "bold"), background=self.colors["accent"], foreground=self.colors["text_light"], padding=6)
        style.map("TButton", background=[("active", self.colors["primary"])])
        
        # --- CLASS OPTIONS for Combobox (Dropdown) ---
        self.class_options = ["VI-A", "VI-B", "VI-C", "VI-D", 
                              "VII-A", "VII-B", "VII-C", "VII-D", "VII-E", "VII-F", "VIII-A", "VIII-B", "VIII-C", "VIII-D", "VIII-E", "IX-A", "IX-B", "IX-C", "IX-D",
                              "X-A", "X-B", "X-C", "X-D", "X-E", "XI-A", "XI-B", "XI-C", "XI-D", "XII-A", "XII-B", "XII-C", "XII-D", "Faculty", "Other"] 

        # --- HEADER FRAME ---
        header_frame = tk.Frame(root, bg=self.colors["primary"])
        header_frame.pack(fill="x", pady=(0, 10))
        try:
            logo_path = resource_path("IISM.jpg")
            if not os.path.exists(logo_path): raise FileNotFoundError(f"Logo not found at {logo_path}")
            logo_image = Image.open(logo_path).resize((80, 80), Image.Resampling.LANCZOS)
            self.logo_photo = ImageTk.PhotoImage(logo_image)
            tk.Label(header_frame, image=self.logo_photo, bg=self.colors["primary"]).pack(side="left", padx=20, pady=10)
        except Exception as e:
            print(f"[Logo Error] {e}")
            tk.Label(header_frame, text="IISM", bg=self.colors["primary"], fg="white", font=("Helvetica", 18, "bold")).pack(side="left", padx=20, pady=10)

        tk.Label(header_frame, text="INDIA INTERNATIONAL SCHOOL", font=("Helvetica", 24, "bold"), bg=self.colors["primary"], fg="white").pack(side="left", padx=10, pady=10, expand=True)
        tk.Label(header_frame, text="Library Management System", font=("Helvetica", 14), bg=self.colors["primary"], fg="white").pack(side="left", padx=5, pady=10)

        # --- MAIN NOTEBOOK ---
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)
        
        # --- Entry Variables (All defined here for global access) ---
        self.add_book_isbn_var = tk.StringVar()
        self.add_book_id_var = tk.StringVar()
        self.add_title_var = tk.StringVar()
        self.add_author_var = tk.StringVar()
        self.delete_book_id_var = tk.StringVar()
        
        self.manage_book_id_var = tk.StringVar()
        self.manage_student_id_var = tk.StringVar()
        self.manage_student_class_var = tk.StringVar() 
        
        self.edit_original_id_var = tk.StringVar()
        self.edit_new_isbn_var = tk.StringVar()
        self.edit_new_id_var = tk.StringVar()
        self.edit_title_var = tk.StringVar()
        self.edit_author_var = tk.StringVar()
        self.edit_issue_date_var = tk.StringVar()
        self.edit_issued_student_id_var = tk.StringVar()
        self.edit_student_class_var = tk.StringVar() 
        
        self.search_type_var = tk.StringVar(value="Title")
        self.search_term_var = tk.StringVar()

        # Create tabs
        self._create_view_tab()
        self._create_add_tab()
        self._create_manage_tab()
        self._create_edit_tab()
        self._create_search_tab()

        self.populate_main_treeview() 
        
# --- 4. Main Application Execution ---
if __name__ == "__main__":
    # Test connection before running GUI
    conn_test = get_db_connection()
    if isinstance(conn_test, str):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Fatal Error",
            f"Could not connect to the database. Please check your credentials in the code.\n\n{conn_test}"
        )
    else:
        root = tk.Tk()
        app = LibraryApp(root)
        root.mainloop()
