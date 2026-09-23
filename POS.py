'''import mysql.connector
dbcon = mysql.connector.connect(host = "localhost", user = "root", passwd = "r2d2c-3pobb-8", database = "fn_alagai_marachekku")
if dbcon.is_connected():
    print("CONNECTION SUCCESS")
curser = dbcon.cursor()
def main_menu():
    print("="*40)
    print(" "*7+"FN Alagai Marachekku POS")
    print("="*40)

main_menu()'''

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

# 1. DATABASE CONNECTION AND SAVE LOGIC
def save_expense_to_db():
    exp_date = date.today() # Automatically captures today's date
    
    # Get values from the UI
    selected_cat = category_dropdown.get()
    custom_cat = custom_category_entry.get().strip()
    amount_raw = amount_entry.get().strip()
    notes = remarks_entry.get("1.0", tk.END).strip()
    
    # Determine the final category string
    final_category = custom_cat if selected_cat == "Other (Type Custom)" else selected_cat
    
    # Validation checks
    if not final_category or selected_cat == "":
        messagebox.showerror("Error", "Please select or type an expense category.")
        return
        
    try:
        # Check if amount is a valid decimal number
        final_amount = float(amount_raw)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid amount (numbers only).")
        return

    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="r2d2c-3pobb-8",  # <-- Put your real MySQL password here
            database="fn_alagai_marachekku"
        )
        cursor = conn.cursor()
        
        query = """
            INSERT INTO expenses (expense_date, category, amount, remarks)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (exp_date, final_category, final_amount, notes))
        conn.commit()
        
        messagebox.showinfo("Success", f"Logged ₹{final_amount:.2f} under '{final_category}'!")
        
        # Clear fields for the next entry
        amount_entry.delete(0, tk.END)
        remarks_entry.delete("1.0", tk.END)
        custom_category_entry.delete(0, tk.END)
        category_dropdown.set("")
        toggle_custom_field()
        
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Something went wrong: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

# 2. UI LOGIC FOR THE FREEDOM DROPDOWN
def toggle_custom_field(event=None):
    """Shows the manual text entry field only if 'Other' is picked."""
    if category_dropdown.get() == "Other (Type Custom)":
        custom_label.grid(row=2, column=0, sticky="w", pady=5)
        custom_category_entry.grid(row=2, column=1, sticky="ew", pady=5)
    else:
        custom_label.grid_remove()
        custom_category_entry.grid_remove()

# 3. TKINTER WINDOW SETUP
root = tk.Tk()
root.title("FN Alagai Marachekku POS - Log Expenses")
root.geometry("500x420")

frame = ttk.Frame(root, padding="20")
frame.pack(fill="both", expand=True)

# Tell the layout grid to allow column 1 to stretch out horizontally
frame.columnconfigure(1, weight=1)

# Heading
ttk.Label(frame, text="Log Shop Expense", font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

# Category Selection
ttk.Label(frame, text="Category:").grid(row=1, column=0, sticky="w", pady=5)
categories = ['Raw Material/Seeds', 'Packaging', 'Rent', 'Electricity', 'Salary', 'Maintenance', 'Other (Type Custom)']
category_dropdown = ttk.Combobox(frame, values=categories, state="readonly")
category_dropdown.grid(row=1, column=1, sticky="ew", pady=5)
category_dropdown.bind("<<ComboboxSelected>>", toggle_custom_field)

# Hidden Custom Category Entry
custom_label = ttk.Label(frame, text="Type Custom Category:")
custom_category_entry = ttk.Entry(frame)

# Amount Entry
ttk.Label(frame, text="Amount (₹):").grid(row=3, column=0, sticky="w", pady=5)
amount_entry = ttk.Entry(frame)
amount_entry.grid(row=3, column=1, sticky="ew", pady=5)

# Remarks Entry
ttk.Label(frame, text="Remarks/Notes:").grid(row=4, column=0, sticky="nw", pady=5)
remarks_entry = tk.Text(frame, height=4, width=30)
remarks_entry.grid(row=4, column=1, sticky="ew", pady=5)

# Save Button
save_btn = ttk.Button(frame, text="Save Expense", command=save_expense_to_db)
save_btn.grid(row=5, column=0, columnspan=2, pady=20)

root.mainloop()






'''products_to_add = [("SS001", "SESAME OIL 250ml", "135.00"), ("SS002", "SESAME OIL 500ml", "270.00"), ("SS003", "SESAME OIL 1ltr", "540.00"),
                   ("CC001", "COCONUT OIL 250ml", "120.00"), ("CC002", "COCONUT OIL 500ml", "2420.00"),("CC003", "COCONUT OIL 1ltr", "480.00"),
                   ("GN001", "GROUNDNUT OIL 500ml", "240.00"), ("GN002", "GROUNDNUT OIL 1ltr", "480.00"), ("HN001", "HONEY 250gm", "150.00"),
                   ("HN002", "HONEY 500gm", "300.00"), ("GH001", "GHEE 100ml", "95.00"), ("GH002", "GHEE 200ml", "190.00"), ("GH003", "GHEE 500ml", "450.00"),
                   ("ID001", "IDIYAPPAM MAVU 500gm", "105.00"), ("ID002", "IDIYAPPAM MAVU 1000gm", "210.00"), ("NS001", "NAATTU SARKARAI 500gm", "50.00"),
                   ("FM001", "FISH MASALA 100gm", "50.00"), ("FM002", "FISH MASALA 250gm", "110.00"), ("MM001", "MUTTON MASALA 100gm", "120.00"),
                   ("MM002", "MUTTON MASALA 250gm", "300.00"), ("CP001", "CHILLI POWDER 100gm", "0.00"), ("CP002", "CHILLI POWDER 200gm", "0.00"),
                   ("TP001", "TURMERIC POWDER 50gm", "30.00"), ("TP002", "TURMERIC POWDER 100gm", "60.00"), ("KA001", "KARUPATTI 1kg", "350.00"),
                   ("OC0001", "SESAME OIL CAKE 1kg", "40.00"), ("OC002", "GROUNDNUT OIL CAKE 1kg", "65.00"), ("OC003", "COCONUT OIL CAKE 1kg", "25.00"),
                   ("CS001", "COCONUT SOAP 80gm", "60.00"), ("CT000", "CASTOR OIL BULK", "0.00"), ("CT001", "CASTOR OIL 100ml", "70.00"),
                   ("CT002", "CASTOR OIL 250ml", "150.00"), ("CT003", "CASTOR OIL 500ml", "300.00"), ("NM000", "NEEM OIL BULK", "0.00"),
                   ("NM001", "NEEM OIL 100ml", "70.00"), ("NM002", "NEEM OIL 200ml", "150.00"), ("NM003", "NEEM OIL 500ml", "300.00"),
                   ("SM001", "SESAME SEEDS(kg)", "0.00")]

query = "INSERT INTO products(Product_Code, Item_Name, Rate) VALUES (%s, %s, %s)"
curser.executemany(query, products_to_add)

dbcon.commit()
print(f"Successfully loaded {curser.rowcount} products!")'''
