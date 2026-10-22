# --- 0. SILENT CONSOLE SUPPRESSION (Native Desktop App Feel) ---
import sys
if sys.platform == "win32":
    import ctypes
    try:
        console_hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if console_hwnd:
            ctypes.windll.user32.ShowWindow(console_hwnd, 0)  # 0 = SW_HIDE
    except Exception:
        pass

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, colorchooser
import os
import json
import random
import gc
from datetime import datetime, date
import mysql.connector
from typing import List, Tuple, Any, Union

# --- Pillow Imports with Safe Guard ---
try:
    from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageDraw
except ImportError:
    tk.Tk().withdraw()
    messagebox.showerror(
        "Dependency Error",
        "The 'Pillow' library is required for this application.\n\nInstall it by running:\n  pip install Pillow"
    )
    sys.exit(1)

# =================================================================
#                 1. RESOURCE PATH & CONFIGURATION
# =================================================================

def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

CONFIG_FILE = resource_path("config.json")

DEFAULT_CONFIG = {
    "institution_name": "INDIA INTERNATIONAL SCHOOL",
    "short_code": "IISM",
    "subtitle": "Library Management System",
    "logo_path": "IISM.jpg",
    "theme_preset": "default",       # default, default2, galaxy, modern, custom
    "theme_mode": "light",          # light, dark
    "enable_animations": True,
    "bg_image_path": "",
    "bg_image_blur": True,
    "show_log_window": False,
    "custom_colors": {
        "primary": "#1E3A8A",
        "bg": "#0B1120",
        "accent": "#3B82F6",
        "card_bg": "#1E293B",
        "text": "#F8FAFC"
    }
}

def load_app_config() -> dict:
    """Loads configuration from config.json or returns defaults."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                config = DEFAULT_CONFIG.copy()
                config.update(data)
                return config
        except Exception as e:
            print(f"[Config Error] Could not load config.json: {e}")
    return DEFAULT_CONFIG.copy()

def save_app_config(config_data: dict):
    """Saves configuration to config.json."""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        print(f"[Config Error] Could not save config.json: {e}")

# =================================================================
#                 2. COMPREHENSIVE THEME PALETTES
# =================================================================

THEME_PRESETS = {
    "default": {
        "name": "Default (Classic Navy)",
        "light": {
            "primary": "#1E3A8A",
            "primary_dark": "#172554",
            "header_text": "#FFFFFF",
            "bg": "#F1F5F9",
            "card_bg": "#FFFFFF",
            "card_border": "#CBD5E1",
            "text_dark": "#0F172A",
            "text_muted": "#64748B",
            "accent": "#2563EB",
            "accent_hover": "#1D4ED8",
            "accent_text": "#FFFFFF",
            "danger": "#DC2626",
            "danger_hover": "#B91C1C",
            "tree_bg": "#FFFFFF",
            "tree_fg": "#0F172A",
            "tree_alt": "#F8FAFC",
            "tree_sel_bg": "#3B82F6",
            "tree_sel_fg": "#FFFFFF",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#0F172A",
            "tab_bg": "#172554",
            "tab_selected": "#2563EB",
            "anim_type": "shimmer"
        },
        "dark": {
            "primary": "#0F172A",
            "primary_dark": "#020617",
            "header_text": "#F8FAFC",
            "bg": "#0B1120",
            "card_bg": "#1E293B",
            "card_border": "#334155",
            "text_dark": "#F8FAFC",
            "text_muted": "#94A3B8",
            "accent": "#3B82F6",
            "accent_hover": "#60A5FA",
            "accent_text": "#FFFFFF",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "tree_bg": "#1E293B",
            "tree_fg": "#F8FAFC",
            "tree_alt": "#243247",
            "tree_sel_bg": "#2563EB",
            "tree_sel_fg": "#FFFFFF",
            "entry_bg": "#0F172A",
            "entry_fg": "#F8FAFC",
            "tab_bg": "#020617",
            "tab_selected": "#3B82F6",
            "anim_type": "shimmer"
        }
    },
    "default2": {
        "name": "Crimson Red",
        "light": {
            "primary": "#881337",
            "primary_dark": "#4C0519",
            "header_text": "#FFFFFF",
            "bg": "#FFF1F2",
            "card_bg": "#FFFFFF",
            "card_border": "#FECDD3",
            "text_dark": "#4C0519",
            "text_muted": "#9F1239",
            "accent": "#E11D48",
            "accent_hover": "#BE123C",
            "accent_text": "#FFFFFF",
            "danger": "#991B1B",
            "danger_hover": "#7F1D1D",
            "tree_bg": "#FFFFFF",
            "tree_fg": "#4C0519",
            "tree_alt": "#FFF5F5",
            "tree_sel_bg": "#E11D48",
            "tree_sel_fg": "#FFFFFF",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#4C0519",
            "tab_bg": "#4C0519",
            "tab_selected": "#E11D48",
            "anim_type": "pulse"
        },
        "dark": {
            "primary": "#4C0519",
            "primary_dark": "#2B040F",
            "header_text": "#FFF1F2",
            "bg": "#140207",
            "card_bg": "#2A0812",
            "card_border": "#4C0519",
            "text_dark": "#FFE4E6",
            "text_muted": "#FDA4AF",
            "accent": "#F43F5E",
            "accent_hover": "#FB7185",
            "accent_text": "#FFFFFF",
            "danger": "#DC2626",
            "danger_hover": "#B91C1C",
            "tree_bg": "#2A0812",
            "tree_fg": "#FFE4E6",
            "tree_alt": "#3A0E1A",
            "tree_sel_bg": "#F43F5E",
            "tree_sel_fg": "#FFFFFF",
            "entry_bg": "#1C040B",
            "entry_fg": "#FFE4E6",
            "tab_bg": "#1F030B",
            "tab_selected": "#F43F5E",
            "anim_type": "pulse"
        }
    },
    "galaxy": {
        "name": "Galaxy (Cosmic Purple)",
        "light": {
            "primary": "#3B0764",
            "primary_dark": "#1E0338",
            "header_text": "#FAF5FF",
            "bg": "#FAF5FF",
            "card_bg": "#FFFFFF",
            "card_border": "#E9D5FF",
            "text_dark": "#2E1065",
            "text_muted": "#7E22CE",
            "accent": "#9333EA",
            "accent_hover": "#7E22CE",
            "accent_text": "#FFFFFF",
            "danger": "#E11D48",
            "danger_hover": "#BE123C",
            "tree_bg": "#FFFFFF",
            "tree_fg": "#2E1065",
            "tree_alt": "#FAF5FF",
            "tree_sel_bg": "#9333EA",
            "tree_sel_fg": "#FFFFFF",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#2E1065",
            "tab_bg": "#1E0338",
            "tab_selected": "#9333EA",
            "anim_type": "stars"
        },
        "dark": {
            "primary": "#0B0117",
            "primary_dark": "#05000A",
            "header_text": "#F5D0FE",
            "bg": "#06010F",
            "card_bg": "#15082A",
            "card_border": "#3B0764",
            "text_dark": "#F5D0FE",
            "text_muted": "#C084FC",
            "accent": "#A855F7",
            "accent_hover": "#C084FC",
            "accent_text": "#FFFFFF",
            "danger": "#F43F5E",
            "danger_hover": "#E11D48",
            "tree_bg": "#15082A",
            "tree_fg": "#F5D0FE",
            "tree_alt": "#210C3E",
            "tree_sel_bg": "#A855F7",
            "tree_sel_fg": "#FFFFFF",
            "entry_bg": "#0D021A",
            "entry_fg": "#F5D0FE",
            "tab_bg": "#05000A",
            "tab_selected": "#A855F7",
            "anim_type": "stars"
        }
    },
    "modern": {
        "name": "Modern (PS4 BIOS / Carbon)",
        "light": {
            "primary": "#181B20",
            "primary_dark": "#0F1115",
            "header_text": "#F8FAFC",
            "bg": "#EAEFF5",
            "card_bg": "#FFFFFF",
            "card_border": "#CBD5E1",
            "text_dark": "#0F172A",
            "text_muted": "#475569",
            "accent": "#0284C7",
            "accent_hover": "#0369A1",
            "accent_text": "#FFFFFF",
            "danger": "#EF4444",
            "danger_hover": "#DC2626",
            "tree_bg": "#FFFFFF",
            "tree_fg": "#0F172A",
            "tree_alt": "#F1F5F9",
            "tree_sel_bg": "#0284C7",
            "tree_sel_fg": "#FFFFFF",
            "entry_bg": "#FFFFFF",
            "entry_fg": "#0F172A",
            "tab_bg": "#0F1115",
            "tab_selected": "#0284C7",
            "anim_type": "cyber"
        },
        "dark": {
            "primary": "#0D0E11",
            "primary_dark": "#050608",
            "header_text": "#E2E8F0",
            "bg": "#090A0D",
            "card_bg": "#14171D",
            "card_border": "#282E38",
            "text_dark": "#F1F5F9",
            "text_muted": "#94A3B8",
            "accent": "#00D2FF",
            "accent_hover": "#38BDF8",
            "accent_text": "#090A0D",
            "danger": "#F87171",
            "danger_hover": "#EF4444",
            "tree_bg": "#14171D",
            "tree_fg": "#F1F5F9",
            "tree_alt": "#1E222A",
            "tree_sel_bg": "#00D2FF",
            "tree_sel_fg": "#090A0D",
            "entry_bg": "#0B0C0E",
            "entry_fg": "#F1F5F9",
            "tab_bg": "#050608",
            "tab_selected": "#00D2FF",
            "anim_type": "cyber"
        }
    }
}

def resolve_theme_colors(config: dict) -> dict:
    """Calculates active palette. When wallpaper is active, sets frosted dark acrylic for readability."""
    preset = config.get("theme_preset", "default")
    mode = config.get("theme_mode", "light")
    has_wallpaper = bool(config.get("bg_image_path", "").strip()) and os.path.exists(config.get("bg_image_path", "").strip())

    if preset == "custom":
        custom = config.get("custom_colors", {})
        acc = custom.get("accent", "#3B82F6")

        # If a custom photo wallpaper is active, auto-tune backgrounds to frosted acrylic slate!
        if has_wallpaper:
            return {
                "primary": "#0F172A",
                "primary_dark": "#0A0F1D",
                "header_text": "#FFFFFF",
                "bg": "#0A0F1D",
                "card_bg": "#131926",
                "card_border": acc,
                "text_dark": "#F8FAFC",
                "text_muted": "#94A3B8",
                "accent": acc,
                "accent_hover": acc,
                "accent_text": "#FFFFFF",
                "danger": "#DC2626",
                "danger_hover": "#B91C1C",
                "tree_bg": "#131926",
                "tree_fg": "#F8FAFC",
                "tree_alt": "#1B2232",
                "tree_sel_bg": acc,
                "tree_sel_fg": "#FFFFFF",
                "entry_bg": "#0A0F1D",
                "entry_fg": "#F8FAFC",
                "tab_bg": "#0A0F1D",
                "tab_selected": acc,
                "anim_type": "stars"
            }
        else:
            # Custom solid colors without wallpaper
            prim = custom.get("primary", "#1E3A8A")
            bg_col = custom.get("bg", "#0B1120")
            card = custom.get("card_bg", "#1E293B")
            txt = custom.get("text", "#F8FAFC")
            return {
                "primary": prim,
                "primary_dark": prim,
                "header_text": "#FFFFFF",
                "bg": bg_col,
                "card_bg": card,
                "card_border": acc,
                "text_dark": txt,
                "text_muted": "#94A3B8",
                "accent": acc,
                "accent_hover": acc,
                "accent_text": "#FFFFFF",
                "danger": "#DC2626",
                "danger_hover": "#B91C1C",
                "tree_bg": card,
                "tree_fg": txt,
                "tree_alt": bg_col,
                "tree_sel_bg": acc,
                "tree_sel_fg": "#FFFFFF",
                "entry_bg": bg_col,
                "entry_fg": txt,
                "tab_bg": prim,
                "tab_selected": acc,
                "anim_type": "stars"
            }

    preset_dict = THEME_PRESETS.get(preset, THEME_PRESETS["default"])
    return preset_dict.get(mode, preset_dict["light"]).copy()

# =================================================================
#                 3. LIVE MYSQL QUERY LOGGER
# =================================================================

class QueryLogger:
    """Manages real-time logging of all database actions (memory-capped)."""
    def __init__(self, max_history=150):
        self.listeners = []
        self.logs_history = []
        self.max_history = max_history

    def register_listener(self, callback):
        if callback not in self.listeners:
            self.listeners.append(callback)

    def unregister_listener(self, callback):
        if callback in self.listeners:
            self.listeners.remove(callback)

    def log(self, action: str, details: str = "", status: str = "SUCCESS"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "action": action,
            "details": details,
            "status": status
        }
        self.logs_history.append(entry)
        if len(self.logs_history) > self.max_history:
            self.logs_history.pop(0)

        for listener in self.listeners:
            try:
                listener(entry)
            except Exception:
                pass

query_logger = QueryLogger()

class MySQLLogWindow(tk.Toplevel):
    """Secondary Live Console Window showing MySQL query updates."""
    def __init__(self, parent, on_close_callback=None):
        super().__init__(parent)
        self.title("MySQL Live Query & Activity Monitor")
        self.geometry("750x450")
        self.configure(bg="#0D1117")
        self.on_close_callback = on_close_callback

        try:
            icon_p = resource_path("library.ico")
            if os.path.exists(icon_p):
                self.iconbitmap(icon_p)
        except Exception:
            pass

        bar = tk.Frame(self, bg="#161B22", pady=6, padx=10)
        bar.pack(fill="x")

        tk.Label(
            bar, text="⚡ Live MySQL Query Stream",
            font=("Consolas", 11, "bold"), fg="#58A6FF", bg="#161B22"
        ).pack(side="left")

        clear_btn = tk.Button(
            bar, text="Clear Logs", bg="#21262D", fg="#C9D1D9",
            activebackground="#30363D", activeforeground="#FFFFFF",
            font=("Consolas", 9), relief="flat", command=self.clear_logs
        )
        clear_btn.pack(side="right", padx=5)

        self.text_area = tk.Text(
            self, bg="#0D1117", fg="#C9D1D9", font=("Consolas", 10),
            wrap="word", relief="flat", padx=10, pady=10
        )
        self.text_area.pack(fill="both", expand=True, side="left")

        scrollbar = tk.Scrollbar(self, command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.config(yscrollcommand=scrollbar.set)

        self.text_area.tag_configure("time", foreground="#8B949E")
        self.text_area.tag_configure("action", foreground="#79C0FF", font=("Consolas", 10, "bold"))
        self.text_area.tag_configure("SUCCESS", foreground="#7EE787", font=("Consolas", 10, "bold"))
        self.text_area.tag_configure("ERROR", foreground="#FF7B72", font=("Consolas", 10, "bold"))
        self.text_area.tag_configure("INFO", foreground="#D2A8FF")
        self.text_area.tag_configure("details", foreground="#E6EDF3")

        for entry in query_logger.logs_history:
            self.append_log(entry)

        query_logger.register_listener(self.append_log)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def append_log(self, entry: dict):
        status_tag = entry["status"]
        self.text_area.insert(tk.END, f"[{entry['timestamp']}] ", "time")
        self.text_area.insert(tk.END, f"[{entry['status']}] ", status_tag)
        self.text_area.insert(tk.END, f"{entry['action']}\n", "action")
        if entry["details"]:
            self.text_area.insert(tk.END, f"    ↳ {entry['details']}\n\n", "details")
        else:
            self.text_area.insert(tk.END, "\n")
        self.text_area.see(tk.END)

    def clear_logs(self):
        self.text_area.delete("1.0", tk.END)

    def on_close(self):
        query_logger.unregister_listener(self.append_log)
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()

# =================================================================
#                 4. DATABASE HANDLER SECTION
# =================================================================

MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'r2d2c-3pobb-8',
    'database': 'library'
}

def get_db_connection() -> Union[mysql.connector.MySQLConnection, str]:
    """Establishes and returns a connection to the MySQL database."""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        if conn.is_connected():
            query_logger.log("CONNECT", "Successfully connected to MySQL database 'library'.", "SUCCESS")
            initialize_db(conn)
            return conn
    except mysql.connector.Error as err:
        error_message = f"Error: Failed to connect to MySQL: {err}"
        query_logger.log("CONNECT", error_message, "ERROR")
        return error_message
    
    return "Error: Unknown database connection failure."

def initialize_db(conn: mysql.connector.MySQLConnection):
    """Creates the 'books' table if it doesn't already exist."""
    if not conn:
        return

    cursor = conn.cursor()
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
        query_logger.log("INIT_TABLE", "Checked/Created table 'books'.", "SUCCESS")
    except mysql.connector.Error as err:
        query_logger.log("INIT_TABLE", f"Error creating table: {err}", "ERROR")
    finally:
        cursor.close()

def wipe_database() -> str:
    """Truncates the 'books' table to completely wipe all records."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    try:
        cursor.execute("TRUNCATE TABLE books")
        conn.commit()
        query_logger.log("WIPE_DATABASE", "TRUNCATE TABLE books executed. All records cleared.", "SUCCESS")
        return "Database successfully reset! All books have been cleared."
    except mysql.connector.Error as err:
        conn.rollback()
        query_logger.log("WIPE_DATABASE", f"Error wiping database: {err}", "ERROR")
        return f"Error resetting database: {err}"
    finally:
        cursor.close()
        if conn and conn.is_connected():
            conn.close()

def fetch_all_books() -> Union[List[Tuple[Any, ...]], str]:
    """Retrieves all books from the database."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    
    query = "SELECT ISBN, bookID, Title, author_name, issueStatus, issueDate, issuedStudentID, student_class FROM books"
    
    try:
        cursor.execute(query)
        books = cursor.fetchall()
        query_logger.log("FETCH_ALL", f"Retrieved {len(books)} records from 'books'.", "SUCCESS")
        formatted_books = []
        for book in books:
            book_list = list(book)
            book_list[0] = book_list[0] if book_list[0] not in (None, 'None') else '-N/A-'
            book_list[4] = book_list[4] if book_list[4] not in (None, 'None') else 'Available'
            book_list[5] = book_list[5].strftime("%Y-%m-%d") if book_list[5] else ""
            book_list[6] = book_list[6] if book_list[6] else ""
            book_list[7] = book_list[7] if book_list[7] else ""
            formatted_books.append(tuple(book_list))
        return formatted_books
    except mysql.connector.Error as err:
        query_logger.log("FETCH_ALL", f"Failed to fetch books: {err}", "ERROR")
        return f"Error: Could not fetch books: {err}"
    finally:
        cursor.close()
        if conn and conn.is_connected():
            conn.close()

def fetch_book_by_id(book_id: str) -> Union[Tuple, str]:
    """Fetches a single book by its ID for the edit form."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    
    query = "SELECT ISBN, bookID, Title, author_name, issueDate, issuedStudentID, student_class FROM books WHERE bookID = %s"
    
    try:
        cursor.execute(query, (book_id,))
        book = cursor.fetchone() 
        if not book:
            query_logger.log("FETCH_BY_ID", f"Book ID '{book_id}' not found.", "INFO")
            return f"Error: No book found with ID: {book_id}"
        
        query_logger.log("FETCH_BY_ID", f"Fetched details for Book ID '{book_id}'.", "SUCCESS")
        book_list = list(book)
        book_list[0] = book_list[0] if book_list[0] not in (None, 'None') else ''
        book_list[4] = book_list[4].strftime("%Y-%m-%d") if book_list[4] else ""
        book_list[5] = book_list[5] if book_list[5] else ""
        book_list[6] = book_list[6] if book_list[6] else ""
        return tuple(book_list) 
    except mysql.connector.Error as err:
        query_logger.log("FETCH_BY_ID", f"Error fetching book '{book_id}': {err}", "ERROR")
        return f"Error fetching book: {err}"
    finally:
        cursor.close()
        if conn and conn.is_connected():
            conn.close()

def add_new_book(book_isbn: str, book_id: str, title: str, author: str) -> str:
    """Adds a new book record with default status 'Available'."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    query = "INSERT INTO books (ISBN, bookID, Title, author_name, issueStatus) VALUES (%s, %s, %s, %s, %s)"
    try:
        cursor.execute(query, (book_isbn, book_id, title, author, 'Available'))
        conn.commit()
        query_logger.log("ADD_BOOK", f"Added '{title}' (ID: {book_id}, ISBN: {book_isbn})", "SUCCESS")
        return f"Book '{title}' successfully added with ID {book_id} and ISBN {book_isbn}."
    except mysql.connector.Error as err:
        conn.rollback()
        query_logger.log("ADD_BOOK", f"Error adding '{title}': {err}", "ERROR")
        return f"Error adding book: {err}"
    finally:
        cursor.close()

def update_book_details(original_id: str, **updates) -> str:
    """Updates book details, including student_class."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    
    set_clauses = []
    params = []
    is_issued = bool(updates.get('new_issue_date')) and bool(updates.get('new_student_id'))

    if updates.get('new_book_id') and updates['new_book_id'] != original_id:
        set_clauses.append("bookID = %s")
        params.append(updates['new_book_id'])

    if updates.get('new_title'):
        set_clauses.append("Title = %s")
        params.append(updates['new_title'])
        
    if updates.get('new_author'):
        set_clauses.append("author_name = %s")
        params.append(updates['new_author'])

    if is_issued:
        set_clauses.append("issueStatus = %s")
        params.append('Issued')
        set_clauses.append("issueDate = %s")
        params.append(updates['new_issue_date'])
        set_clauses.append("issuedStudentID = %s")
        params.append(updates['new_student_id'])
        set_clauses.append("student_class = %s")
        class_param = updates.get('new_student_class') or None
        params.append(class_param) 
    else:
        set_clauses.append("issueStatus = %s")
        params.append('Available')
        set_clauses.append("issueDate = NULL")
        set_clauses.append("issuedStudentID = NULL")
        set_clauses.append("student_class = NULL")
    
    final_set_clauses = [c for c in set_clauses if "NULL" in c or "%s" in c] 
    if not final_set_clauses:
        return "No changes detected to update."

    set_clause_str = ", ".join(final_set_clauses)
    params.append(original_id) 

    try:
        if "NULL" in set_clause_str:
            null_handled_params = []
            final_set_parts = []
            param_index = 0
            for clause in set_clauses:
                if clause in ("issueDate = NULL", "issuedStudentID = NULL", "student_class = NULL"):
                    final_set_parts.append(clause)
                elif clause.endswith("= %s"):
                    if params[param_index] is not None:
                        final_set_parts.append(clause)
                        null_handled_params.append(params[param_index])
                    else:
                        if 'student_class' in clause:
                            final_set_parts.append("student_class = NULL")
                        else:
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
            query = f"UPDATE books SET {set_clause_str} WHERE bookID = %s"
            cursor.execute(query, tuple(params))
            
        conn.commit()
        if cursor.rowcount == 0:
            query_logger.log("UPDATE_BOOK", f"Book ID '{original_id}' not found or no change made.", "INFO")
            return f"Warning: Book ID {original_id} not found or no changes were made."
        query_logger.log("UPDATE_BOOK", f"Book ID '{original_id}' updated successfully.", "SUCCESS")
        return f"Book ID {original_id} details successfully updated."
    except mysql.connector.Error as err:
        conn.rollback()
        query_logger.log("UPDATE_BOOK", f"Error updating '{original_id}': {err}", "ERROR")
        return f"Error updating book: {err}"
    finally:
        cursor.close()

def borrow_book_record(book_id: str, student_id: str, student_class: str) -> str:
    """Updates book status to 'Issued' with current date and student info."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    today = date.today()
    query = "UPDATE books SET issueStatus = %s, issueDate = %s, issuedStudentID = %s, student_class = %s WHERE bookID = %s"
    class_param = student_class if student_class else None
    
    try:
        cursor.execute(query, ('Issued', today, student_id, class_param, book_id))
        conn.commit()
        if cursor.rowcount == 0:
            query_logger.log("BORROW_BOOK", f"Book ID '{book_id}' not found.", "INFO")
            return f"Error: Book ID {book_id} not found."
        query_logger.log("BORROW_BOOK", f"Issued Book '{book_id}' to Student '{student_id}' ({student_class})", "SUCCESS")
        return f"Book ID {book_id} successfully issued to Student {student_id} ({student_class})."
    except mysql.connector.Error as err:
        conn.rollback()
        query_logger.log("BORROW_BOOK", f"Error issuing book '{book_id}': {err}", "ERROR")
        return f"Error issuing book: {err}"
    finally:
        cursor.close()

def return_book_record(book_id: str) -> str:
    """Updates book status to 'Available' and clears issue details."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn
    cursor = conn.cursor()
    query = "UPDATE books SET issueStatus = %s, issueDate = NULL, issuedStudentID = NULL, student_class = NULL WHERE bookID = %s AND issueStatus = %s"
    try:
        cursor.execute(query, ('Available', book_id, 'Issued'))
        conn.commit()
        if cursor.rowcount == 0:
            query_logger.log("RETURN_BOOK", f"Book ID '{book_id}' not found or wasn't issued.", "INFO")
            return f"Error: Book ID {book_id} not found or was not currently issued."
        query_logger.log("RETURN_BOOK", f"Book ID '{book_id}' returned and marked Available.", "SUCCESS")
        return f"Book ID {book_id} successfully marked as Available."
    except mysql.connector.Error as err:
        conn.rollback()
        query_logger.log("RETURN_BOOK", f"Error returning book '{book_id}': {err}", "ERROR")
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
            query_logger.log("DELETE_BOOK", f"Book ID '{book_id}' not found.", "INFO")
            return f"Error: Book ID {book_id} not found."
        query_logger.log("DELETE_BOOK", f"Book ID '{book_id}' permanently deleted.", "SUCCESS")
        return f"Book ID {book_id} successfully deleted."
    except mysql.connector.Error as err:
        conn.rollback()
        query_logger.log("DELETE_BOOK", f"Error deleting book '{book_id}': {err}", "ERROR")
        return f"Error deleting book: {err}"
    finally:
        cursor.close()

def search_books(search_type: str, search_term: str) -> Union[List[Tuple[Any, ...]], str]:
    """Searches books based on type and term."""
    conn = get_db_connection()
    if isinstance(conn, str):
        return conn

    column_map = {
        'Title': 'Title', 'Author': 'author_name', 'Book ID': 'bookID', 
        'Book No:': 'bookID', 'Status': 'issueStatus', 
        'Student/Teacher Class': 'student_class', 'ISBN': 'ISBN'
    }
    column_name = column_map.get(search_type)
    if not column_name:
        return "Error: Invalid search type."
    
    cursor = conn.cursor()
    query = f"SELECT ISBN, bookID, Title, author_name, issueStatus, issueDate, issuedStudentID, student_class FROM books WHERE {column_name} LIKE %s"
    partial_search_fields = ('Title', 'Author', 'Book ID', 'Book No:', 'Status', 'Student/Teacher Class', 'ISBN')
    param = f"%{search_term}%" if search_type in partial_search_fields else search_term

    try:
        cursor.execute(query, (param,))
        results = cursor.fetchall()
        query_logger.log("SEARCH_BOOKS", f"Search ({search_type}='{search_term}') found {len(results)} matches.", "SUCCESS")

        if not results:
            return "No records found matching your search."

        formatted_results = []
        for book in results:
            book_list = list(book)
            if len(book_list) != 8:
                continue
            book_list[0] = book_list[0] if book_list[0] not in (None, 'None') else '-N/A-'
            book_list[4] = book_list[4] if book_list[4] not in (None, 'None') else 'Available'
            book_list[5] = book_list[5].strftime("%Y-%m-%d") if book_list[5] else ""
            book_list[6] = book_list[6] if book_list[6] else ""
            book_list[7] = book_list[7] if book_list[7] else ""
            formatted_results.append(tuple(book_list))
            
        return formatted_results
    except mysql.connector.Error as err:
        query_logger.log("SEARCH_BOOKS", f"Search error: {err}", "ERROR")
        return f"Error searching books: {err}"
    finally:
        cursor.close()
        if conn and conn.is_connected():
            conn.close()

# =================================================================
#                 5. GUI APPLICATION SECTION
# =================================================================

class LibraryApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.config = load_app_config()
        self.colors = resolve_theme_colors(self.config)
        self.log_window = None

        # Particle Animation Engine state (Capped at 30 FPS, zero memory allocation)
        self.anim_running = False
        self.particles_data = []
        self.particle_items = []
        self._init_particles()

        # Sliding Tab Bar state (Smooth 35 FPS interpolation)
        self.active_tab_index = 0
        self.target_tab_index = 0
        self.indicator_x = 0.0
        self.is_sliding = False
        self.hover_tab_index = -1
        self._resize_job = None

        # Cached background photo and logo
        self.bg_photo = None
        self.logo_photo = None

        self.root.title(f"Library Management System - {self.config.get('institution_name', 'IISM')}")
        self.root.geometry("1100x750")
        self.root.minsize(960, 660)

        # Window Icon
        try:
            icon_path = resource_path("library.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"[Icon Error] Could not set window icon: {e}")

        # Class options for dropdowns
        self.class_options = [
            "VI-A", "VI-B", "VI-C", "VI-D", 
            "VII-A", "VII-B", "VII-C", "VII-D", "VII-E", "VII-F",
            "VIII-A", "VIII-B", "VIII-C", "VIII-D", "VIII-E",
            "IX-A", "IX-B", "IX-C", "IX-D",
            "X-A", "X-B", "X-C", "X-D", "X-E",
            "XI-A", "XI-B", "XI-C", "XI-D",
            "XII-A", "XII-B", "XII-C", "XII-D",
            "Faculty", "Other"
        ]

        # Tab StringVars
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

        # Settings StringVars
        self.settings_name_var = tk.StringVar(value=self.config.get("institution_name", "INDIA INTERNATIONAL SCHOOL"))
        self.settings_short_var = tk.StringVar(value=self.config.get("short_code", "IISM"))
        self.settings_subtitle_var = tk.StringVar(value=self.config.get("subtitle", "Library Management System"))
        self.settings_logo_path_var = tk.StringVar(value=self.config.get("logo_path", "IISM.jpg"))
        
        self.settings_preset_var = tk.StringVar(value=self.config.get("theme_preset", "default"))
        self.settings_mode_var = tk.StringVar(value=self.config.get("theme_mode", "light"))
        self.settings_anim_var = tk.BooleanVar(value=self.config.get("enable_animations", True))
        
        self.settings_bg_path_var = tk.StringVar(value=self.config.get("bg_image_path", ""))
        self.settings_bg_blur_var = tk.BooleanVar(value=self.config.get("bg_image_blur", True))
        self.settings_show_log_var = tk.BooleanVar(value=self.config.get("show_log_window", False))

        # Build Master Edge-to-Edge Architecture
        self._build_master_canvas()
        self._build_all_tab_views()

        # Apply Complete Theme & Wallpaper
        self.apply_theme()

        # Populate View Tab
        self.populate_main_treeview()

        # Open Live Log if configured
        if self.settings_show_log_var.get():
            self.toggle_log_window(show=True)

        # Start Global Animation Loop (30 FPS cap, zero RAM churn)
        self.start_animation_engine()

        # Bind window resize handler
        self.root.bind("<Configure>", self._on_window_resize)

        # Make all Tk and TTK buttons and controls trigger when pressing the Enter key
        for btn_class in ("TButton", "Button"):
            self.root.bind_class(btn_class, "<Return>", lambda event: event.widget.invoke())
            self.root.bind_class(btn_class, "<KP_Enter>", lambda event: event.widget.invoke())

        for toggle_class in ("TRadiobutton", "Radiobutton", "TCheckbutton", "Checkbutton"):
            self.root.bind_class(toggle_class, "<Return>", lambda event: event.widget.invoke())
            self.root.bind_class(toggle_class, "<KP_Enter>", lambda event: event.widget.invoke())

    # ------------------ ANIMATION PARTICLES INIT ------------------

    def _init_particles(self):
        """Initializes ambient animated particles data."""
        self.particles_data = []
        for _ in range(35):
            self.particles_data.append({
                "x": random.randint(10, 1150),
                "y": random.randint(5, 75),
                "r": random.choice([1.2, 1.8, 2.2]),
                "speed": random.uniform(0.3, 0.9),
                "brightness": random.uniform(0.4, 1.0),
                "dir": random.choice([-0.02, 0.02])
            })

    # ------------------ MASTER CANVAS ARCHITECTURE ------------------

    def _build_master_canvas(self):
        """Builds a 100% full-window master canvas covering every corner."""
        self.master_canvas = tk.Canvas(
            self.root, highlightthickness=0, bd=0
        )
        self.master_canvas.pack(fill="both", expand=True)

        self.tab_titles = [
            ("📖 View All Books", 0),
            ("➕ Add / Delete", 1),
            ("🔄 Borrow / Return", 2),
            ("✏ Edit Book", 3),
            ("🔎 Search Books", 4),
            ("⚙ Settings & Themes", 5)
        ]

        # Tab interaction bindings on master canvas
        self.master_canvas.bind("<Button-1>", self._on_master_click)
        self.master_canvas.bind("<Motion>", self._on_master_motion)
        self.master_canvas.bind("<Leave>", self._on_master_leave)

    def _on_master_motion(self, event):
        if 82 <= event.y <= 126:
            w = self.master_canvas.winfo_width() or 1100
            tab_w = w / len(self.tab_titles)
            hover_idx = int(event.x // tab_w)
            if 0 <= hover_idx < len(self.tab_titles) and hover_idx != self.hover_tab_index:
                self.hover_tab_index = hover_idx
                self._redraw_master_canvas()
        else:
            if self.hover_tab_index != -1:
                self.hover_tab_index = -1
                self._redraw_master_canvas()

    def _on_master_leave(self, event):
        self.hover_tab_index = -1
        self._redraw_master_canvas()

    def _on_master_click(self, event):
        if 82 <= event.y <= 126:
            w = self.master_canvas.winfo_width() or 1100
            tab_w = w / len(self.tab_titles)
            idx = int(event.x // tab_w)
            if 0 <= idx < len(self.tab_titles) and idx != self.active_tab_index:
                self.select_tab(idx)

    def select_tab(self, index: int):
        """Triggers fluid sliding transition to the target tab."""
        self.target_tab_index = index
        self.is_sliding = True
        self._animate_tab_slide()

    def _animate_tab_slide(self):
        """Smooth interpolation loop capped at ~35 FPS."""
        w = self.master_canvas.winfo_width() or 1100
        tab_w = w / len(self.tab_titles)
        target_x = self.target_tab_index * tab_w

        dx = target_x - self.indicator_x
        if abs(dx) < 1.0:
            self.indicator_x = target_x
            self.active_tab_index = self.target_tab_index
            self.is_sliding = False
            self._switch_content_view(self.active_tab_index)
            self._redraw_master_canvas()
        else:
            self.indicator_x += dx * 0.35
            self._redraw_master_canvas()
            self.root.after(28, self._animate_tab_slide)

    def _switch_content_view(self, index: int):
        """Swaps the floating card view on the master canvas."""
        if hasattr(self, "content_window_id") and index < len(self.tab_views):
            self.master_canvas.itemconfigure(self.content_window_id, window=self.tab_views[index])

    def _redraw_master_canvas(self):
        """Draws edge-to-edge wallpaper, header, and sliding tab bar seamlessly."""
        w = self.master_canvas.winfo_width() or 1100
        h = self.master_canvas.winfo_height() or 750
        c = self.colors

        # Clear background and navigation tags only (preserves content window)
        self.master_canvas.delete("bg_layer")
        self.master_canvas.delete("header_layer")
        self.master_canvas.delete("tab_layer")
        self.particle_items.clear()

        # 1. 100% Full-Window Wallpaper or Theme Background
        has_wp = bool(self.bg_photo)
        if has_wp:
            self.master_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg_layer")
        else:
            self.master_canvas.create_rectangle(0, 0, w, h, fill=c["bg"], outline="", tags="bg_layer")
            # Solid Header & Tab Bar for standard themes
            self.master_canvas.create_rectangle(0, 0, w, 80, fill=c["primary"], outline="", tags="header_layer")
            self.master_canvas.create_rectangle(0, 82, w, 126, fill=c["tab_bg"], outline="", tags="tab_layer")

        # 2. Header Area Divider (y=80)
        self.master_canvas.create_line(0, 80, w, 80, fill=c["accent"], width=2, tags="header_layer")

        # Ambient Particles in Header
        if self.config.get("enable_animations", True):
            for p in self.particles_data:
                star_col = "#FFFFFF" if c.get("anim_type") != "cyber" else c["accent"]
                item = self.master_canvas.create_oval(
                    p["x"] % w, p["y"], (p["x"] % w) + p["r"], p["y"] + p["r"],
                    fill=star_col, outline="", tags="header_layer"
                )
                self.particle_items.append(item)

        # Header Logo
        logo_rel = self.config.get("logo_path", "IISM.jpg")
        logo_full = resource_path(logo_rel)
        if not os.path.exists(logo_full) and os.path.exists(logo_rel):
            logo_full = logo_rel

        x_offset = 20
        if os.path.exists(logo_full):
            try:
                img = Image.open(logo_full).resize((58, 58), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(img)
                self.master_canvas.create_image(48, 40, image=self.logo_photo, anchor="center", tags="header_layer")
                x_offset = 90
            except Exception as e:
                print(f"[Logo Render Error] {e}")

        # Header Text
        inst_title = self.config.get("institution_name", "INDIA INTERNATIONAL SCHOOL")
        sub_title = self.config.get("subtitle", "Library Management System")
        short_code = self.config.get("short_code", "IISM")

        self.master_canvas.create_text(
            x_offset, 28, text=inst_title,
            fill=c["header_text"], font=("Segoe UI", 18, "bold"), anchor="w", tags="header_layer"
        )
        self.master_canvas.create_text(
            x_offset, 54, text=sub_title,
            fill=c["text_muted"], font=("Segoe UI", 11, "italic"), anchor="w", tags="header_layer"
        )
        self.master_canvas.create_text(
            w - 25, 40, text=short_code,
            fill=c["accent"], font=("Segoe UI", 16, "bold"), anchor="e", tags="header_layer"
        )

        # 3. Sliding Tab Bar (y=82 to 126)
        if not has_wp:
            self.master_canvas.create_rectangle(0, 82, w, 126, fill=c["tab_bg"], outline="", tags="tab_layer")
        self.master_canvas.create_line(0, 126, w, 126, fill=c["card_border"], width=1, tags="tab_layer")
        num_tabs = len(self.tab_titles)
        tab_w = w / num_tabs

        # Sliding Pill Indicator
        pill_x1 = self.indicator_x + 6
        pill_x2 = self.indicator_x + tab_w - 6
        self.master_canvas.create_rectangle(
            pill_x1, 86, pill_x2, 122,
            fill=c["accent"], outline="", width=0, tags="tab_layer"
        )
        self.master_canvas.create_line(
            pill_x1 + 6, 123, pill_x2 - 6, 123,
            fill=c["accent_text"], width=2, tags="tab_layer"
        )

        # Tab Labels
        for i, (title, idx) in enumerate(self.tab_titles):
            tx = (i * tab_w) + (tab_w / 2)
            ty = 104
            if i == self.active_tab_index:
                txt_col = c["accent_text"]
                txt_font = ("Segoe UI", 10, "bold")
            elif i == self.hover_tab_index:
                txt_col = c["accent"]
                txt_font = ("Segoe UI", 10, "bold")
            else:
                txt_col = c["text_muted"]
                txt_font = ("Segoe UI", 10)

            self.master_canvas.create_text(
                tx, ty, text=title, fill=txt_col, font=txt_font, anchor="center", tags="tab_layer"
            )

        # Keep content window above background but below header/tab navigation
        self.master_canvas.tag_lower("bg_layer")

    # ------------------ BUILD ALL TAB VIEWS ------------------

    def _build_all_tab_views(self):
        """Constructs all 6 views and mounts the active one onto the master canvas."""
        self.tab_views = []

        # View 0: View All Books
        v0 = ttk.Frame(self.master_canvas, style="Card.TFrame", padding=15)
        cols = ('ISBN', 'Book No.', 'Title', 'Author', 'Status', 'Issue Date', 'Student/Teacher ID', 'Student/Teacher Class')
        
        btn_bar = ttk.Frame(v0, style="Card.TFrame", padding=6)
        btn_bar.pack(side="bottom", fill="x", pady=(8, 0))
        ttk.Button(btn_bar, text="🔄 Refresh List", command=self.populate_main_treeview).pack(side="left", padx=5)
        self.status_count_label = ttk.Label(btn_bar, text="", font=("Segoe UI", 10, "italic"))
        self.status_count_label.pack(side="right", padx=10)

        sc0 = ttk.Scrollbar(v0, orient="vertical")
        sc0.pack(side="right", fill="y")

        self.main_tree = ttk.Treeview(v0, columns=cols, show='headings', height=18, yscrollcommand=sc0.set)
        sc0.configure(command=self.main_tree.yview)
        col_widths = {
            'ISBN': 110, 'Book No.': 85, 'Title': 220, 'Author': 160,
            'Status': 95, 'Issue Date': 105, 'Student/Teacher ID': 115, 'Student/Teacher Class': 130
        }
        for col in cols:
            self.main_tree.heading(col, text=col)
            self.main_tree.column(col, width=col_widths.get(col, 100), anchor='w')
        self.main_tree.pack(side="left", fill="both", expand=True)
        self.main_tree.bind("<Return>", lambda e: self.populate_main_treeview())
        self.main_tree.bind("<KP_Enter>", lambda e: self.populate_main_treeview())
        self.tab_views.append(v0)

        # View 1: Add / Delete Book
        v1 = ttk.Frame(self.master_canvas, style="Card.TFrame", padding=20)
        add_frame = ttk.LabelFrame(v1, text=" Add New Book to Library ", padding="15")
        add_frame.pack(fill="x", padx=10, pady=8)
        ttk.Label(add_frame, text="ISBN:").grid(row=0, column=0, padx=8, pady=6, sticky='w')
        add_isbn_entry = ttk.Entry(add_frame, textvariable=self.add_book_isbn_var, width=35)
        add_isbn_entry.grid(row=0, column=1, padx=8, pady=6, sticky='w')
        ttk.Label(add_frame, text="Book ID / Accession No:").grid(row=1, column=0, padx=8, pady=6, sticky='w')
        add_id_entry = ttk.Entry(add_frame, textvariable=self.add_book_id_var, width=35)
        add_id_entry.grid(row=1, column=1, padx=8, pady=6, sticky='w')
        ttk.Label(add_frame, text="Title:").grid(row=2, column=0, padx=8, pady=6, sticky='w')
        add_title_entry = ttk.Entry(add_frame, textvariable=self.add_title_var, width=50)
        add_title_entry.grid(row=2, column=1, padx=8, pady=6, sticky='w')
        ttk.Label(add_frame, text="Author:").grid(row=3, column=0, padx=8, pady=6, sticky='w')
        add_author_entry = ttk.Entry(add_frame, textvariable=self.add_author_var, width=50)
        add_author_entry.grid(row=3, column=1, padx=8, pady=6, sticky='w')

        for ent in (add_isbn_entry, add_id_entry, add_title_entry, add_author_entry):
            ent.bind("<Return>", lambda e: self.add_new_book_gui())
            ent.bind("<KP_Enter>", lambda e: self.add_new_book_gui())

        ttk.Button(add_frame, text="💾 Add Book Record", command=self.add_new_book_gui).grid(row=4, column=1, padx=8, pady=12, sticky='w')

        del_frame = ttk.LabelFrame(v1, text=" Delete Single Book Record ", padding="15")
        del_frame.pack(fill="x", padx=10, pady=15)
        ttk.Label(del_frame, text="Book ID to Delete:").grid(row=0, column=0, padx=8, pady=6, sticky='w')
        del_book_entry = ttk.Entry(del_frame, textvariable=self.delete_book_id_var, width=35)
        del_book_entry.grid(row=0, column=1, padx=8, pady=6, sticky='w')
        del_book_entry.bind("<Return>", lambda e: self.delete_specified_book_gui())
        del_book_entry.bind("<KP_Enter>", lambda e: self.delete_specified_book_gui())
        ttk.Button(del_frame, text="🗑 Delete Book", style="Danger.TButton", command=self.delete_specified_book_gui).grid(row=1, column=1, padx=8, pady=10, sticky='w')
        self.tab_views.append(v1)

        # View 2: Borrow / Return
        v2 = ttk.Frame(self.master_canvas, style="Card.TFrame", padding=20)
        borrow_frame = ttk.LabelFrame(v2, text=" Issue / Borrow Book ", padding="15")
        borrow_frame.pack(fill="x", padx=10, pady=8)
        ttk.Label(borrow_frame, text="Book ID / No:").grid(row=0, column=0, padx=6, pady=6, sticky='w')
        borrow_id_entry = ttk.Entry(borrow_frame, textvariable=self.manage_book_id_var, width=32)
        borrow_id_entry.grid(row=0, column=1, padx=6, pady=6, sticky='w')
        ttk.Label(borrow_frame, text="Student / Teacher ID:").grid(row=1, column=0, padx=6, pady=6, sticky='w')
        borrow_student_entry = ttk.Entry(borrow_frame, textvariable=self.manage_student_id_var, width=32)
        borrow_student_entry.grid(row=1, column=1, padx=6, pady=6, sticky='w')
        ttk.Label(borrow_frame, text="Student / Teacher Class:").grid(row=2, column=0, padx=6, pady=6, sticky='w')
        combobox = ttk.Combobox(borrow_frame, textvariable=self.manage_student_class_var, values=self.class_options, state='readonly', width=30)
        combobox.grid(row=2, column=1, padx=6, pady=6, sticky='w')
        combobox.set("")

        for widget in (borrow_id_entry, borrow_student_entry, combobox):
            widget.bind("<Return>", lambda e: self.borrow_book_gui())
            widget.bind("<KP_Enter>", lambda e: self.borrow_book_gui())

        ttk.Button(borrow_frame, text="📤 Issue Book", command=self.borrow_book_gui).grid(row=3, column=1, padx=6, pady=10, sticky='w')

        return_frame = ttk.LabelFrame(v2, text=" Return Book to Inventory ", padding="15")
        return_frame.pack(fill="x", padx=10, pady=12)
        ttk.Label(return_frame, text="Book ID / No:").grid(row=0, column=0, padx=6, pady=6, sticky='w')
        self.return_book_id_entry = ttk.Entry(return_frame, width=32)
        self.return_book_id_entry.grid(row=0, column=1, padx=6, pady=6, sticky='w')
        self.return_book_id_entry.bind("<Return>", lambda e: self.return_book_gui())
        self.return_book_id_entry.bind("<KP_Enter>", lambda e: self.return_book_gui())
        ttk.Button(return_frame, text="📥 Return Book", command=self.return_book_gui).grid(row=1, column=1, padx=6, pady=10, sticky='w')
        self.tab_views.append(v2)

        # View 3: Edit Book
        v3 = ttk.Frame(self.master_canvas, style="Card.TFrame", padding=20)
        fetch_frame = ttk.LabelFrame(v3, text=" Locate Book to Edit ", padding="12")
        fetch_frame.pack(fill="x", padx=10, pady=6)
        ttk.Label(fetch_frame, text="Enter Book ID to Edit:").grid(row=0, column=0, padx=6, pady=6, sticky='w')
        edit_orig_entry = ttk.Entry(fetch_frame, textvariable=self.edit_original_id_var, width=28)
        edit_orig_entry.grid(row=0, column=1, padx=6, pady=6, sticky='w')
        edit_orig_entry.bind("<Return>", lambda e: self.fetch_book_to_edit())
        edit_orig_entry.bind("<KP_Enter>", lambda e: self.fetch_book_to_edit())
        ttk.Button(fetch_frame, text="🔍 Fetch Details", command=self.fetch_book_to_edit).grid(row=0, column=2, padx=12, pady=6)

        update_frame = ttk.LabelFrame(v3, text=" Update Record Details ", padding="15")
        update_frame.pack(fill="x", padx=10, pady=10)
        fields = [
            ("New ISBN:", self.edit_new_isbn_var),
            ("New Book No:", self.edit_new_id_var),
            ("New Title:", self.edit_title_var),
            ("New Author:", self.edit_author_var),
            ("New Issue Date (YYYY-MM-DD):", self.edit_issue_date_var),  
            ("New Student/Teacher ID:", self.edit_issued_student_id_var),
            ("New Student/Teacher Class:", self.edit_student_class_var)
        ]
        for i, (text, var) in enumerate(fields):
            ttk.Label(update_frame, text=text).grid(row=i, column=0, padx=6, pady=5, sticky='w')
            if text == "New Student/Teacher Class:":
                cb = ttk.Combobox(update_frame, textvariable=var, values=self.class_options, state='readonly', width=36)
                cb.grid(row=i, column=1, padx=6, pady=5, sticky='w')
                cb.bind("<Return>", lambda e: self.update_book_gui())
                cb.bind("<KP_Enter>", lambda e: self.update_book_gui())
            else:
                ent = ttk.Entry(update_frame, textvariable=var, width=38)
                ent.grid(row=i, column=1, padx=6, pady=5, sticky='w')
                ent.bind("<Return>", lambda e: self.update_book_gui())
                ent.bind("<KP_Enter>", lambda e: self.update_book_gui())
        ttk.Button(update_frame, text="💾 Update Book Details", command=self.update_book_gui).grid(row=len(fields), column=1, padx=6, pady=12, sticky='w')
        self.tab_views.append(v3)

        # View 4: Search Books
        v4 = ttk.Frame(self.master_canvas, style="Card.TFrame", padding=15)
        search_bar = ttk.Frame(v4, style="Card.TFrame", padding="8")
        search_bar.pack(fill="x")
        ttk.Label(search_bar, text="Search By:").pack(side=tk.LEFT, padx=5)
        search_opts = ['Title', 'Author', 'ISBN', 'Book No:', 'Status', 'Student/Teacher Class']
        self.search_opts_menu = ttk.OptionMenu(
            search_bar, self.search_type_var, self.search_type_var.get(), *search_opts,
            command=self._on_search_type_changed
        )
        self.search_opts_menu.pack(side=tk.LEFT, padx=5)
        ttk.Label(search_bar, text="Term:").pack(side=tk.LEFT, padx=5)

        # Dynamic search input container: switches between Text Entry and Dropdown Comboboxes
        self.search_term_container = ttk.Frame(search_bar, style="Card.TFrame")
        self.search_term_container.pack(side=tk.LEFT, padx=5)

        self.search_entry = ttk.Entry(self.search_term_container, textvariable=self.search_term_var, width=28)
        self.search_class_combo = ttk.Combobox(
            self.search_term_container, textvariable=self.search_term_var,
            values=self.class_options, state='readonly', width=26
        )
        self.search_status_combo = ttk.Combobox(
            self.search_term_container, textvariable=self.search_term_var,
            values=["Available", "Issued"], state='readonly', width=26
        )

        # Show appropriate input widget initially and on criteria change
        self._on_search_type_changed()
        self.search_type_var.trace_add("write", lambda *a: self._on_search_type_changed())

        # Bind Enter and selection events for all search input controls
        self.search_entry.bind("<Return>", lambda e: self.search_books_gui())
        self.search_entry.bind("<KP_Enter>", lambda e: self.search_books_gui())
        self.search_class_combo.bind("<Return>", lambda e: self.search_books_gui())
        self.search_class_combo.bind("<KP_Enter>", lambda e: self.search_books_gui())
        self.search_status_combo.bind("<Return>", lambda e: self.search_books_gui())
        self.search_status_combo.bind("<KP_Enter>", lambda e: self.search_books_gui())
        self.search_class_combo.bind("<<ComboboxSelected>>", lambda e: self.search_books_gui())
        self.search_status_combo.bind("<<ComboboxSelected>>", lambda e: self.search_books_gui())

        ttk.Button(search_bar, text="🔍 Search", command=self.search_books_gui).pack(side=tk.LEFT, padx=10)

        results_frame = ttk.Frame(v4, style="Card.TFrame", padding=8)
        results_frame.pack(fill="both", expand=True)
        sc4 = ttk.Scrollbar(results_frame, orient="vertical")
        sc4.pack(side="right", fill="y")
        self.search_tree = ttk.Treeview(results_frame, columns=cols, show='headings', height=16, yscrollcommand=sc4.set)
        sc4.configure(command=self.search_tree.yview)
        for col in cols:
            self.search_tree.heading(col, text=col)
            self.search_tree.column(col, width=col_widths.get(col, 100), anchor='w')
        self.search_tree.pack(side="left", fill="both", expand=True)
        self.tab_views.append(v4)

        # View 5: Settings & Themes (Scrollable Container)
        self.settings_container = ttk.Frame(self.master_canvas, style="Card.TFrame")
        self.settings_scrollbar = ttk.Scrollbar(self.settings_container, orient="vertical")
        self.settings_scrollbar.pack(side="right", fill="y")
        
        self.settings_scroll_canvas = tk.Canvas(self.settings_container, highlightthickness=0, bd=0, yscrollcommand=self.settings_scrollbar.set)
        self.settings_scrollbar.configure(command=self.settings_scroll_canvas.yview)
        self.settings_scroll_canvas.pack(side="left", fill="both", expand=True)

        self._build_settings_cards()
        self.tab_views.append(self.settings_container)

        # Mount active view onto Master Canvas
        w = self.master_canvas.winfo_width() or 1100
        h = self.master_canvas.winfo_height() or 750
        self.content_window_id = self.master_canvas.create_window(
            30, 134, window=self.tab_views[0], anchor="nw",
            width=w - 60, height=h - 150
        )

    # ------------------ SETTINGS CARDS ------------------

    def _build_settings_cards(self):
        """Constructs floating cards placed directly onto settings scroll canvas."""
        # 1. BRANDING CARD
        self.brand_card = ttk.LabelFrame(self.settings_scroll_canvas, text=" 🏫 Institution & Header Customization ", padding="15")
        ttk.Label(self.brand_card, text="Institution Main Title:").grid(row=0, column=0, padx=8, pady=6, sticky='w')
        brand_name_ent = ttk.Entry(self.brand_card, textvariable=self.settings_name_var, width=42)
        brand_name_ent.grid(row=0, column=1, padx=8, pady=6, sticky='w')
        ttk.Label(self.brand_card, text="Corner Tag / Acronym:").grid(row=1, column=0, padx=8, pady=6, sticky='w')
        brand_short_ent = ttk.Entry(self.brand_card, textvariable=self.settings_short_var, width=20)
        brand_short_ent.grid(row=1, column=1, padx=8, pady=6, sticky='w')
        ttk.Label(self.brand_card, text="Subtitle Description:").grid(row=2, column=0, padx=8, pady=6, sticky='w')
        brand_sub_ent = ttk.Entry(self.brand_card, textvariable=self.settings_subtitle_var, width=42)
        brand_sub_ent.grid(row=2, column=1, padx=8, pady=6, sticky='w')
        ttk.Label(self.brand_card, text="Header Logo File:").grid(row=3, column=0, padx=8, pady=6, sticky='w')
        logo_box = ttk.Frame(self.brand_card)
        logo_box.grid(row=3, column=1, padx=8, pady=6, sticky='w')
        brand_logo_ent = ttk.Entry(logo_box, textvariable=self.settings_logo_path_var, width=30)
        brand_logo_ent.pack(side="left", padx=(0, 6))

        for bent in (brand_name_ent, brand_short_ent, brand_sub_ent, brand_logo_ent):
            bent.bind("<Return>", lambda e: self.save_branding_gui())
            bent.bind("<KP_Enter>", lambda e: self.save_branding_gui())

        ttk.Button(logo_box, text="Browse Image...", command=self.browse_logo_gui).pack(side="left")
        ttk.Button(self.brand_card, text="💾 Save & Apply Branding", command=self.save_branding_gui).grid(row=4, column=1, padx=8, pady=10, sticky='w')

        # 2. APPEARANCE CARD
        self.theme_card = ttk.LabelFrame(self.settings_scroll_canvas, text=" 🎨 Appearance & Display Theme ", padding="15")
        ttk.Label(self.theme_card, text="Select Theme Style:").grid(row=0, column=0, padx=8, pady=6, sticky='w')
        preset_box = ttk.Frame(self.theme_card)
        preset_box.grid(row=0, column=1, padx=8, pady=6, sticky='w')
        theme_options = [
            ("Default (Navy)", "default"),
            ("Default 2 (Crimson)", "default2"),
            ("Galaxy (Purple)", "galaxy"),
            ("Modern (PS4 Carbon)", "modern"),
            ("Custom Color Palette", "custom")
        ]
        for label, val in theme_options:
            ttk.Radiobutton(preset_box, text=label, value=val, variable=self.settings_preset_var, command=self.on_theme_changed).pack(side="left", padx=6)

        ttk.Label(self.theme_card, text="Color Mode:").grid(row=1, column=0, padx=8, pady=6, sticky='w')
        mode_box = ttk.Frame(self.theme_card)
        mode_box.grid(row=1, column=1, padx=8, pady=6, sticky='w')
        self.light_radio = ttk.Radiobutton(mode_box, text="☀ Light Mode", value="light", variable=self.settings_mode_var, command=self.on_theme_changed)
        self.light_radio.pack(side="left", padx=10)
        self.dark_radio = ttk.Radiobutton(mode_box, text="🌙 Dark Mode", value="dark", variable=self.settings_mode_var, command=self.on_theme_changed)
        self.dark_radio.pack(side="left", padx=10)

        anim_check = ttk.Checkbutton(self.theme_card, text="✨ Enable Ambient Stars & Visual Effects (Header & Background)", variable=self.settings_anim_var, command=self.on_animation_toggle_changed)
        anim_check.grid(row=2, column=1, padx=8, pady=8, sticky='w')

        # CUSTOM COLOR SPECTRUM CHOOSER
        self.custom_color_box = ttk.LabelFrame(self.theme_card, text=" 🖌 Custom Color Spectrum Chooser ", padding="12")
        self.custom_color_box.grid(row=3, column=0, columnspan=2, padx=8, pady=8, sticky='ew')
        ttk.Label(self.custom_color_box, text="Primary:").grid(row=0, column=0, padx=4, pady=4, sticky='w')
        self.prim_swatch = tk.Label(self.custom_color_box, text="       ", relief="ridge", bg=self.config.get("custom_colors", {}).get("primary", "#1E3A8A"))
        self.prim_swatch.grid(row=0, column=1, padx=4, pady=4)
        self.pick_prim_btn = ttk.Button(self.custom_color_box, text="Pick...", command=lambda: self.pick_custom_color("primary", self.prim_swatch))
        self.pick_prim_btn.grid(row=0, column=2, padx=4, pady=4)

        ttk.Label(self.custom_color_box, text="Background:").grid(row=0, column=3, padx=4, pady=4, sticky='w')
        self.bg_swatch = tk.Label(self.custom_color_box, text="       ", relief="ridge", bg=self.config.get("custom_colors", {}).get("bg", "#0B1120"))
        self.bg_swatch.grid(row=0, column=4, padx=4, pady=4)
        self.pick_bg_btn = ttk.Button(self.custom_color_box, text="Pick...", command=lambda: self.pick_custom_color("bg", self.bg_swatch))
        self.pick_bg_btn.grid(row=0, column=5, padx=4, pady=4)

        ttk.Label(self.custom_color_box, text="Accent:").grid(row=0, column=6, padx=4, pady=4, sticky='w')
        self.acc_swatch = tk.Label(self.custom_color_box, text="       ", relief="ridge", bg=self.config.get("custom_colors", {}).get("accent", "#3B82F6"))
        self.acc_swatch.grid(row=0, column=7, padx=4, pady=4)
        self.pick_acc_btn = ttk.Button(self.custom_color_box, text="Pick...", command=lambda: self.pick_custom_color("accent", self.acc_swatch))
        self.pick_acc_btn.grid(row=0, column=8, padx=4, pady=4)

        # CUSTOM BACKGROUND WALLPAPER & BLUR (Strictly PNG/JPEG)
        self.wallpaper_box = ttk.LabelFrame(self.theme_card, text=" 🖼 Custom Background Wallpaper & Blur (PNG / JPEG Only) ", padding="12")
        self.wallpaper_box.grid(row=4, column=0, columnspan=2, padx=8, pady=8, sticky='ew')
        ttk.Label(self.wallpaper_box, text="Photo Wallpaper:").grid(row=0, column=0, padx=6, pady=4, sticky='w')
        bg_entry_box = ttk.Frame(self.wallpaper_box)
        bg_entry_box.grid(row=0, column=1, padx=6, pady=4, sticky='w')
        self.bg_path_entry = ttk.Entry(bg_entry_box, textvariable=self.settings_bg_path_var, width=32)
        self.bg_path_entry.pack(side="left", padx=(0, 6))
        self.bg_path_entry.bind("<Return>", lambda e: self.save_bg_image_settings())
        self.bg_path_entry.bind("<KP_Enter>", lambda e: self.save_bg_image_settings())
        self.browse_bg_btn = ttk.Button(bg_entry_box, text="Browse Image...", command=self.browse_bg_image_gui)
        self.browse_bg_btn.pack(side="left", padx=2)
        self.clear_bg_btn = ttk.Button(bg_entry_box, text="Clear Wallpaper", command=self.clear_bg_image_gui)
        self.clear_bg_btn.pack(side="left", padx=4)

        self.blur_check = ttk.Checkbutton(
            self.wallpaper_box,
            text="Apply Sleek Acrylic Blur Effect (Blurs wallpaper for maximum text readability)",
            variable=self.settings_bg_blur_var,
            command=self.save_bg_image_settings
        )
        self.blur_check.grid(row=1, column=1, padx=6, pady=6, sticky='w')

        # 3. LIVE QUERY LOGGER CARD
        self.log_card = ttk.LabelFrame(self.settings_scroll_canvas, text=" ⚡ Developer & Live Activity Monitor ", padding="15")
        log_check = ttk.Checkbutton(
            self.log_card,
            text="Show Live MySQL Query Log Window (Streams all queries & background updates in real-time)",
            variable=self.settings_show_log_var,
            command=self.on_log_toggle_changed
        )
        log_check.pack(anchor="w", padx=8, pady=6)

        # 4. DANGER ZONE CARD
        self.danger_card = ttk.LabelFrame(self.settings_scroll_canvas, text=" ⚠ Danger Zone - Database Reset ", padding="15")
        ttk.Label(
            self.danger_card,
            text="Permanently erase all book records and reset the library inventory back to blank.\nThis operation cannot be reversed!",
            style="Muted.TLabel"
        ).pack(anchor="w", padx=8, pady=(0, 10))
        ttk.Button(self.danger_card, text="🚨 Wipe & Reset All Tables (Permanent)", style="Danger.TButton", command=self.wipe_database_gui).pack(anchor="w", padx=8)

        # Mount Cards onto Settings Scroll Canvas
        self.card_window_ids = []
        for card in (self.brand_card, self.theme_card, self.log_card, self.danger_card):
            win_id = self.settings_scroll_canvas.create_window(20, 0, window=card, anchor="nw")
            self.card_window_ids.append(win_id)

        def _on_mousewheel(event):
            if event.delta:
                self.settings_scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif event.num == 5:
                self.settings_scroll_canvas.yview_scroll(1, "units")
            elif event.num == 4:
                self.settings_scroll_canvas.yview_scroll(-1, "units")

        self.settings_scroll_canvas.bind("<MouseWheel>", _on_mousewheel)
        self.settings_scroll_canvas.bind("<Button-4>", _on_mousewheel)
        self.settings_scroll_canvas.bind("<Button-5>", _on_mousewheel)
        for card in (self.brand_card, self.theme_card, self.log_card, self.danger_card):
            card.bind("<MouseWheel>", _on_mousewheel)

        self.settings_scroll_canvas.bind("<Configure>", self._layout_settings_cards)

    def _layout_settings_cards(self, event=None):
        """Positions settings cards with clean margins so the wallpaper shines through!"""
        w = self.settings_scroll_canvas.winfo_width() or 1000
        card_w = max(500, w - 40)
        y = 15
        cards = [self.brand_card, self.theme_card, self.log_card, self.danger_card]
        for i, card in enumerate(cards):
            card.update_idletasks()
            h = card.winfo_reqheight()
            self.settings_scroll_canvas.coords(self.card_window_ids[i], 20, y)
            self.settings_scroll_canvas.itemconfigure(self.card_window_ids[i], width=card_w)
            y += h + 18
        self.settings_scroll_canvas.configure(scrollregion=(0, 0, w, y + 25))

    # ------------------ ANIMATION ENGINE LOOP (30 FPS CAP) ------------------

    def start_animation_engine(self):
        """Starts the smooth 30 FPS ambient particle animation loop."""
        if not self.anim_running:
            self.anim_running = True
            self._animation_tick()

    def _animation_tick(self):
        """30 FPS tick using canvas.coords() for ZERO RAM churn."""
        if not self.anim_running:
            return

        if self.config.get("enable_animations", True):
            w = self.master_canvas.winfo_width() or 1100
            for i, p in enumerate(self.particles_data):
                p["x"] = (p["x"] - p["speed"]) % w
                if i < len(self.particle_items):
                    self.master_canvas.coords(
                        self.particle_items[i],
                        p["x"], p["y"], p["x"] + p["r"], p["y"] + p["r"]
                    )

        # 33ms interval = exactly 30 FPS (<0.3% CPU)
        self.root.after(33, self._animation_tick)

    # ------------------ THEME APPLICATION ------------------

    def apply_theme(self):
        """Applies colors, updates widgets, and syncs wallpaper & UI."""
        self.colors = resolve_theme_colors(self.config)
        c = self.colors

        self.root.configure(bg=c["bg"])

        style = ttk.Style(self.root)
        style.theme_use("clam")

        style.configure("TFrame", background=c["bg"])
        style.configure("Card.TFrame", background=c["card_bg"], relief="solid", bordercolor=c["card_border"], borderwidth=1)
        style.configure("TLabelframe", background=c["card_bg"], bordercolor=c["card_border"], relief="solid", borderwidth=1)
        style.configure("TLabelframe.Label", background=c["card_bg"], foreground=c["accent"],
                        font=("Segoe UI", 11, "bold"))

        style.configure("TLabel", background=c["card_bg"], foreground=c["text_dark"], font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=c["card_bg"], foreground=c["text_dark"], font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=c["card_bg"], foreground=c["text_muted"], font=("Segoe UI", 9))

        style.configure("TButton", font=("Segoe UI", 10, "bold"), background=c["accent"],
                        foreground=c["accent_text"], borderwidth=0, padding=7)
        style.map("TButton",
                  background=[("active", c["accent_hover"]), ("pressed", c["accent"])],
                  foreground=[("active", c["accent_text"])])

        style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), background=c["danger"],
                        foreground="#FFFFFF", borderwidth=0, padding=7)
        style.map("Danger.TButton",
                  background=[("active", c["danger_hover"]), ("pressed", c["danger"])],
                  foreground=[("active", "#FFFFFF")])

        style.configure("TEntry", fieldbackground=c["entry_bg"], foreground=c["entry_fg"],
                        insertcolor=c["text_dark"], padding=5)
        style.configure("TCombobox", fieldbackground=c["entry_bg"], foreground=c["entry_fg"], padding=4)
        style.map("TCombobox", fieldbackground=[("readonly", c["entry_bg"])],
                  selectbackground=[("readonly", c["accent"])])

        style.configure("Treeview",
                        background=c["tree_bg"],
                        foreground=c["tree_fg"],
                        fieldbackground=c["tree_bg"],
                        rowheight=28,
                        font=("Segoe UI", 10),
                        bordercolor=c["card_border"],
                        borderwidth=1)
        style.map("Treeview",
                  background=[("selected", c["tree_sel_bg"])],
                  foreground=[("selected", c["tree_sel_fg"])])
        
        style.configure("Treeview.Heading",
                        background=c["primary"],
                        foreground=c["header_text"],
                        font=("Segoe UI", 10, "bold"),
                        padding=6,
                        borderwidth=0)
        style.map("Treeview.Heading",
                  background=[("active", c["accent"])])

        self.main_tree.tag_configure("evenrow", background=c["tree_bg"], foreground=c["tree_fg"])
        self.main_tree.tag_configure("oddrow", background=c["tree_alt"], foreground=c["tree_fg"])
        self.search_tree.tag_configure("evenrow", background=c["tree_bg"], foreground=c["tree_fg"])
        self.search_tree.tag_configure("oddrow", background=c["tree_alt"], foreground=c["tree_fg"])

        # Update Settings Canvas Background
        if hasattr(self, "settings_scroll_canvas"):
            self.settings_scroll_canvas.configure(bg=c["bg"])

        # Sync Control States (Grey-Out Logic)
        self._sync_control_states()

        # Update Wallpaper
        self.update_background_wallpaper()

        # Redraw Master Canvas & Navigation
        self._redraw_master_canvas()

        # Run Garbage Collector
        gc.collect()

    def _sync_control_states(self):
        """Enforces clean UI grey-outs between Custom and Builtin themes."""
        preset = self.settings_preset_var.get()
        is_custom = (preset == "custom")
        has_wp = bool(self.config.get("bg_image_path", "").strip()) and os.path.exists(self.config.get("bg_image_path", "").strip())

        # 1. Light/Dark mode: Disabled when Custom is chosen!
        if hasattr(self, "light_radio") and hasattr(self, "dark_radio"):
            mode_state = "disabled" if is_custom else "normal"
            self.light_radio.config(state=mode_state)
            self.dark_radio.config(state=mode_state)

        # 2. Wallpaper Controls: Always enabled for all themes!
        if hasattr(self, "bg_path_entry"):
            self.bg_path_entry.config(state="normal")
            self.browse_bg_btn.config(state="normal")
            self.clear_bg_btn.config(state="normal")
            self.blur_check.config(state="normal")

        # 3. If Wallpaper is active in Custom, Primary/Background swatches are locked (wallpaper is background)
        if hasattr(self, "pick_prim_btn") and hasattr(self, "pick_bg_btn"):
            if is_custom and has_wp:
                self.pick_prim_btn.config(state="disabled")
                self.pick_bg_btn.config(state="disabled")
            elif is_custom and not has_wp:
                self.pick_prim_btn.config(state="normal")
                self.pick_bg_btn.config(state="normal")
            else:
                self.pick_prim_btn.config(state="disabled")
                self.pick_bg_btn.config(state="disabled")

    # ------------------ WALLPAPER RENDERER ------------------

    def update_background_wallpaper(self):
        """Loads, blurs, and renders wallpaper across 100% of the entire window."""
        path = self.config.get("bg_image_path", "").strip()

        if not path or not os.path.exists(path):
            self.bg_photo = None
            if hasattr(self, "settings_scroll_canvas"):
                self.settings_scroll_canvas.delete("bg_img")
            return

        try:
            mw = self.master_canvas.winfo_width() or self.root.winfo_width() or 1100
            mh = self.master_canvas.winfo_height() or self.root.winfo_height() or 750
            mw = max(mw, 800)
            mh = max(mh, 600)

            # Load image
            img = Image.open(path).convert("RGBA")

            # 16:9 Landscape Aspect-Ratio Cover Scaling
            img_ratio = img.width / img.height
            target_ratio = mw / mh

            if target_ratio > img_ratio:
                new_w = mw
                new_h = int(mw / img_ratio)
            else:
                new_h = mh
                new_w = int(mh * img_ratio)

            img = img.resize((new_w, new_h), Image.Resampling.BILINEAR)

            # Center Crop
            left = (new_w - mw) // 2
            top = (new_h - mh) // 2
            img = img.crop((left, top, left + mw, top + mh))

            # Apply Acrylic Blur if checked
            if self.config.get("bg_image_blur", True):
                img = img.filter(ImageFilter.GaussianBlur(16))

            # Translucent dark wash (True 32-bit alpha composite -> NO STIPPLE GLITCH!)
            dark_wash = Image.new("RGBA", (mw, mh), (15, 23, 42, 130))
            img = Image.alpha_composite(img, dark_wash)

            # Sleek frosted glass bands for header (0..80) and tab bar (80..126)
            def _hex_to_rgba(hex_code, alpha):
                hex_code = hex_code.lstrip('#')
                if len(hex_code) == 6:
                    return (int(hex_code[0:2], 16), int(hex_code[2:4], 16), int(hex_code[4:6], 16), alpha)
                return (15, 23, 42, alpha)

            glass_overlay = Image.new("RGBA", (mw, mh), (0, 0, 0, 0))
            draw = ImageDraw.Draw(glass_overlay)
            header_color = _hex_to_rgba(self.colors.get("primary", "#0F172A"), 110)
            tab_color = _hex_to_rgba(self.colors.get("tab_bg", "#020617"), 140)
            draw.rectangle([0, 0, mw, 80], fill=header_color)
            draw.rectangle([0, 80, mw, 126], fill=tab_color)
            img = Image.alpha_composite(img, glass_overlay)

            self.bg_photo = ImageTk.PhotoImage(img)

            # Also draw on Settings Scroll Canvas
            if hasattr(self, "settings_scroll_canvas"):
                self.settings_scroll_canvas.delete("bg_img")
                self.settings_scroll_canvas.create_image(0, 0, image=self.bg_photo, anchor="nw", tags="bg_img")
                self.settings_scroll_canvas.tag_lower("bg_img")
        except Exception as e:
            print(f"[Wallpaper Render Error] {e}")
            self.bg_photo = None

    def _on_window_resize(self, event):
        """Handles responsive window resizing across the master canvas."""
        w = self.master_canvas.winfo_width() or 1100
        h = self.master_canvas.winfo_height() or 750

        # Resize content view window
        if hasattr(self, "content_window_id"):
            self.master_canvas.coords(self.content_window_id, 30, 134)
            self.master_canvas.itemconfigure(self.content_window_id, width=w - 60, height=h - 150)

        # Debounced wallpaper re-scaling (250ms)
        if hasattr(self, "_resize_job") and self._resize_job:
            self.root.after_cancel(self._resize_job)
        self._resize_job = self.root.after(250, self._delayed_resize_action)

    def _delayed_resize_action(self):
        self.update_background_wallpaper()
        self._redraw_master_canvas()

    # ------------------ SETTINGS HANDLERS ------------------

    def browse_logo_gui(self):
        file_path = filedialog.askopenfilename(
            title="Select Logo Image",
            filetypes=[("Image Files (*.png;*.jpg;*.jpeg;*.ico)", "*.png;*.jpg;*.jpeg;*.ico"), ("All Files", "*.*")]
        )
        if file_path:
            self.settings_logo_path_var.set(file_path)

    def save_branding_gui(self):
        self.config["institution_name"] = self.settings_name_var.get().strip()
        self.config["short_code"] = self.settings_short_var.get().strip()
        self.config["subtitle"] = self.settings_subtitle_var.get().strip()
        self.config["logo_path"] = self.settings_logo_path_var.get().strip()
        save_app_config(self.config)

        self.root.title(f"Library Management System - {self.config['institution_name']}")
        self._redraw_master_canvas()
        messagebox.showinfo("Settings Saved", "Header branding details updated successfully!")

    def on_theme_changed(self):
        preset = self.settings_preset_var.get()
        mode = self.settings_mode_var.get()
        self.config["theme_preset"] = preset
        self.config["theme_mode"] = mode
        save_app_config(self.config)
        self.apply_theme()

    def on_animation_toggle_changed(self):
        self.config["enable_animations"] = self.settings_anim_var.get()
        save_app_config(self.config)
        self._redraw_master_canvas()

    def pick_custom_color(self, color_key: str, swatch_widget: tk.Label):
        current_col = self.config.get("custom_colors", {}).get(color_key, "#1E3A8A")
        picked = colorchooser.askcolor(color=current_col, title=f"Choose {color_key.title()} Color")
        if picked and picked[1]:
            hex_color = picked[1]
            swatch_widget.config(bg=hex_color)
            if "custom_colors" not in self.config:
                self.config["custom_colors"] = {}
            self.config["custom_colors"][color_key] = hex_color
            self.settings_preset_var.set("custom")
            self.config["theme_preset"] = "custom"
            save_app_config(self.config)
            self.apply_theme()

    def browse_bg_image_gui(self):
        """Allows selecting image wallpaper (PNG, JPEG, JPG, WEBP, BMP)."""
        file_path = filedialog.askopenfilename(
            parent=self.root,
            title="Select Custom Background Image",
            filetypes=[
                ("All Image Files (*.png;*.jpg;*.jpeg;*.webp;*.bmp)", "*.png;*.jpg;*.jpeg;*.webp;*.bmp;*.jfif"),
                ("PNG Images (*.png)", "*.png"),
                ("JPEG Images (*.jpg;*.jpeg)", "*.jpg;*.jpeg"),
                ("All Files (*.*)", "*.*")
            ]
        )
        if file_path:
            norm_path = os.path.normpath(file_path)
            try:
                with Image.open(norm_path) as test_img:
                    test_img.verify()
            except Exception as e:
                messagebox.showerror("Invalid Image File", f"Could not load the selected image:\n{e}")
                return

            self.settings_bg_path_var.set(norm_path)
            self.save_bg_image_settings()

    def clear_bg_image_gui(self):
        self.settings_bg_path_var.set("")
        self.save_bg_image_settings()

    def save_bg_image_settings(self):
        self.config["bg_image_path"] = self.settings_bg_path_var.get().strip()
        self.config["bg_image_blur"] = self.settings_bg_blur_var.get()
        save_app_config(self.config)
        self.apply_theme()

    def on_log_toggle_changed(self):
        show = self.settings_show_log_var.get()
        self.config["show_log_window"] = show
        save_app_config(self.config)
        self.toggle_log_window(show)

    def toggle_log_window(self, show: bool):
        if show:
            if not self.log_window or not tk.Toplevel.winfo_exists(self.log_window):
                self.log_window = MySQLLogWindow(
                    self.root,
                    on_close_callback=self._on_log_window_closed
                )
        else:
            if self.log_window and tk.Toplevel.winfo_exists(self.log_window):
                self.log_window.destroy()
                self.log_window = None

    def _on_log_window_closed(self):
        self.settings_show_log_var.set(False)
        self.config["show_log_window"] = False
        save_app_config(self.config)
        self.log_window = None

    def wipe_database_gui(self):
        confirm1 = messagebox.askyesno(
            "⚠ CRITICAL CONFIRMATION: DATABASE RESET",
            "Are you ABSOLUTELY sure you want to wipe all records from the 'books' table?\n\n"
            "This will permanently delete ALL books, issues, and student records.\n"
            "This action CANNOT be undone!"
        )
        if not confirm1:
            return

        confirm2 = messagebox.askyesno(
            "FINAL WARNING",
            "This is your final confirmation.\n\nProceed with deleting all database records?"
        )
        if not confirm2:
            return

        result = wipe_database()
        if result.startswith("Error"):
            messagebox.showerror("Reset Failed", result)
        else:
            messagebox.showinfo("Database Reset", result)
            self.populate_main_treeview()

    # ------------------ TAB HANDLERS ------------------

    def populate_main_treeview(self):
        """Fetches all books and displays them with alternating row colors."""
        for item in self.main_tree.get_children():
            self.main_tree.delete(item)
            
        books = fetch_all_books()
        if isinstance(books, str):
            messagebox.showerror("Database Error", books)
            return
            
        for i, book in enumerate(books):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.main_tree.insert('', tk.END, values=book, tags=(tag,))
            
        self.status_count_label.config(text=f"Total Books: {len(books)}")

    def add_new_book_gui(self):
        isbn = self.add_book_isbn_var.get().strip()
        book_id = self.add_book_id_var.get().strip()
        title = self.add_title_var.get().strip()
        author = self.add_author_var.get().strip()

        if not all([book_id, title, author]):
            messagebox.showwarning("Input Error", "Book ID, Title, and Author are mandatory fields.")
            return

        result = add_new_book(isbn, book_id, title, author)
        if result.startswith("Error"):
            messagebox.showerror("Operation Failed", result)
        else:
            messagebox.showinfo("Success", result)
            self.add_book_isbn_var.set("")
            self.add_book_id_var.set("")
            self.add_title_var.set("")
            self.add_author_var.set("")
            self.populate_main_treeview()

    def delete_specified_book_gui(self):
        book_id = self.delete_book_id_var.get().strip()
        if not book_id:
            messagebox.showwarning("Input Error", "Please enter a valid Book ID to delete.")
            return

        confirm = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to permanently delete Book ID: {book_id}?"
        )
        if not confirm:
            return

        result = delete_book_by_id(book_id)
        if result.startswith("Error"):
            messagebox.showerror("Error", result)
        else:
            messagebox.showinfo("Success", result)
            self.delete_book_id_var.set("")
            self.populate_main_treeview()

    def borrow_book_gui(self):
        book_id = self.manage_book_id_var.get().strip()
        student_id = self.manage_student_id_var.get().strip()
        student_class = self.manage_student_class_var.get().strip()

        if not all([book_id, student_id]):
            messagebox.showwarning("Input Error", "Book ID and Student ID are required.")
            return

        result = borrow_book_record(book_id, student_id, student_class)
        if result.startswith("Error"):
            messagebox.showerror("Issue Failed", result)
        else:
            messagebox.showinfo("Success", result)
            self.manage_book_id_var.set("")
            self.manage_student_id_var.set("")
            self.manage_student_class_var.set("")
            self.populate_main_treeview()

    def return_book_gui(self):
        book_id = self.return_book_id_entry.get().strip()
        if not book_id:
            messagebox.showwarning("Input Error", "Please enter the Book ID to return.")
            return

        result = return_book_record(book_id)
        if result.startswith("Error"):
            messagebox.showerror("Return Failed", result)
        else:
            messagebox.showinfo("Success", result)
            self.return_book_id_entry.delete(0, tk.END)
            self.populate_main_treeview()

    def fetch_book_to_edit(self):
        book_id = self.edit_original_id_var.get().strip()
        if not book_id:
            messagebox.showwarning("Input Error", "Please enter a Book ID to fetch.")
            return

        book = fetch_book_by_id(book_id)
        if isinstance(book, str):
            messagebox.showerror("Error", book)
            return

        self.edit_new_isbn_var.set(book[0])
        self.edit_new_id_var.set(book[1])
        self.edit_title_var.set(book[2])
        self.edit_author_var.set(book[3])
        self.edit_issue_date_var.set(book[4])
        self.edit_issued_student_id_var.set(book[5])
        self.edit_student_class_var.set(book[6])

    def update_book_gui(self):
        orig_id = self.edit_original_id_var.get().strip()
        if not orig_id:
            messagebox.showwarning("Input Error", "Fetch a book first before updating.")
            return

        updates = {
            'new_isbn': self.edit_new_isbn_var.get().strip(),
            'new_book_id': self.edit_new_id_var.get().strip(),
            'new_title': self.edit_title_var.get().strip(),
            'new_author': self.edit_author_var.get().strip(),
            'new_issue_date': self.edit_issue_date_var.get().strip(),
            'new_student_id': self.edit_issued_student_id_var.get().strip(),
            'new_student_class': self.edit_student_class_var.get().strip()
        }

        result = update_book_details(orig_id, **updates)
        if result.startswith("Error"):
            messagebox.showerror("Update Failed", result)
        else:
            messagebox.showinfo("Success", result)
            self.populate_main_treeview()

    def _on_search_type_changed(self, *args):
        """Dynamically switches between Text Entry and Dropdown Comboboxes for search criteria."""
        if not hasattr(self, "search_entry") or not hasattr(self, "search_class_combo") or not hasattr(self, "search_status_combo"):
            return

        stype = self.search_type_var.get()
        self.search_entry.pack_forget()
        self.search_class_combo.pack_forget()
        self.search_status_combo.pack_forget()

        if stype == "Student/Teacher Class":
            self.search_class_combo.pack(side=tk.LEFT)
            if self.search_term_var.get() not in self.class_options:
                self.search_class_combo.set(self.class_options[0] if self.class_options else "")
            self.search_class_combo.focus_set()
        elif stype == "Status":
            self.search_status_combo.pack(side=tk.LEFT)
            if self.search_term_var.get() not in ("Available", "Issued"):
                self.search_status_combo.set("Available")
            self.search_status_combo.focus_set()
        else:
            self.search_entry.pack(side=tk.LEFT)
            if self.search_term_var.get() in self.class_options or self.search_term_var.get() in ("Available", "Issued"):
                self.search_term_var.set("")
            self.search_entry.focus_set()

    def search_books_gui(self):
        stype = self.search_type_var.get()
        sterm = self.search_term_var.get().strip()
        
        for item in self.search_tree.get_children():
            self.search_tree.delete(item)

        if not sterm:
            messagebox.showwarning("Input Error", "Please enter a search term.")
            return
            
        results = search_books(stype, sterm)
        if isinstance(results, str):
            messagebox.showinfo("Search Results", results)
            return

        for i, book in enumerate(results):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            self.search_tree.insert('', tk.END, values=book, tags=(tag,))

# =================================================================
#                 6. MAIN APPLICATION EXECUTION
# =================================================================

if __name__ == "__main__":
    conn_test = get_db_connection()
    if isinstance(conn_test, str):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Fatal Connection Error",
            f"Could not connect to the MySQL database.\n\nPlease check your MySQL service and credentials:\n\n{conn_test}"
        )
    else:
        try:
            conn_test.close()
        except Exception:
            pass
            
        root = tk.Tk()
        app = LibraryApp(root)
        root.mainloop()
