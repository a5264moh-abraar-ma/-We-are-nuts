import csv
import mysql.connector
from datetime import date
from typing import List, Any

# --- 1. MYSQL CONFIGURATION (MUST MATCH YOUR MAIN APP) ---
MYSQL_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'iism123',  # IMPORTANT: Use your actual password
    'database': 'library'
}

# --- 2. FILE PATH ---
# IMPORTANT: Ensure your CSV file is in the same directory as this script.
CSV_FILE_PATH = 'Sample.csv' 

def import_books_from_csv(csv_file: str):
    """Connects to MySQL, reads the CSV, and inserts records."""
    
    # Establish connection
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cursor = conn.cursor()
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return

    # SQL INSERT statement for all 8 columns.
    # ON DUPLICATE KEY UPDATE ensures that if a bookID already exists, 
    # it updates the title and author instead of crashing.
    insert_query = """
    INSERT INTO books 
    (ISBN, bookID, Title, author_name, issueStatus, issueDate, issuedStudentID, student_class) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE 
    Title=VALUES(Title), author_name=VALUES(author_name);
    """ 

    success_count = 0
    fail_count = 0

    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)  # Skip the header row (ISBN, bookID, Title, etc.)

            for i, row in enumerate(reader, 1):
                # Clean up and validate row data
                if not row or all(not item.strip() for item in row):
                    continue # Skip empty lines

                # Take the first 8 elements and strip whitespace
                data: List[Any] = [item.strip() for item in row[:8]] 
                
                # --- DATA VALIDATION and NULL HANDLING ---
                
                # 1. Map empty strings to None for date/ID/class (to insert NULL in MySQL)
                cleaned_data = [item if item != '' else None for item in data]
                
                # bookID (Index 1) is the primary key and must exist
                if not cleaned_data[1]:
                    print(f"Skipping row {i}: bookID is missing.")
                    fail_count += 1
                    continue

                # 2. Handle issueDate (Index 5)
                issue_date_str = cleaned_data[5]
                if issue_date_str:
                    try:
                        # Convert 'YYYY-MM-DD' string to a date object
                        cleaned_data[5] = date.fromisoformat(issue_date_str) 
                    except ValueError:
                        print(f"Skipping row {i}: Invalid date format for '{issue_date_str}'. Must be YYYY-MM-DD.")
                        fail_count += 1
                        continue
                
                try:
                    # Execute the INSERT statement
                    cursor.execute(insert_query, tuple(cleaned_data))
                    success_count += 1
                except mysql.connector.Error as err:
                    print(f"Error inserting row {i} (Book ID: {cleaned_data[1]}): {err}")
                    conn.rollback()
                    fail_count += 1

        conn.commit()
        print("\n--- Import Complete ---")
        print(f"Total rows processed: {success_count + fail_count}")
        print(f"Successfully inserted/updated: {success_count}")
        print(f"Failed to process: {fail_count}")

    except FileNotFoundError:
        print(f"Error: CSV file not found at {csv_file}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    import_books_from_csv(CSV_FILE_PATH)
