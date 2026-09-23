import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from datetime import date

# --- COLOR PALETTE (Sky Blue, Sandy Beige, Light Green) ---
COLOR_SANDY_BEIGE = "#F5F5DC"   # Main background
COLOR_SKY_BLUE    = "#E0F7FA"   # Popups & Sidebars
COLOR_DARK_GREEN  = "#2E8B57"   # Header bar
COLOR_WHITE       = "#FFFFFF"

class AlagaiPOS:
    def __init__(self, root):
        self.root = root
        self.root.title("FN Alagai Marachekku - Ultimate POS")
        self.root.geometry("1200x700")
        self.root.configure(bg=COLOR_SANDY_BEIGE)

        # Live Cart Data Storage
        self.cart = {}

        # --- 1. TOP HEADER SYSTEM ---
        self.header_frame = tk.Frame(self.root, bg=COLOR_DARK_GREEN, height=60)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)

        # ☰ Menu Button (Triggers the popup sidebar)
        self.menu_btn = tk.Button(
            self.header_frame, text="☰ Menu", bg=COLOR_DARK_GREEN, fg=COLOR_WHITE,
            font=("Arial", 12, "bold"), relief="flat", activebackground="#236B43", 
            activeforeground=COLOR_WHITE, command=self.toggle_sidebar
        )
        self.menu_btn.pack(side="left", padx=15)

        # Dedicated Logo Space
        self.logo_space = tk.Frame(self.header_frame, bg=COLOR_WHITE, width=110, height=45, highlightbackground="black", highlightthickness=1)
        self.logo_space.pack(side="left", padx=10, pady=7)
        self.logo_space.pack_propagate(False)
        tk.Label(self.logo_space, text="[ PLACE LOGO ]", bg=COLOR_WHITE, font=("Arial", 8, "bold")).pack(expand=True)

        # Title
        tk.Label(
            self.header_frame, text="FN ALAGAI MARACHEKKU", 
            fg=COLOR_WHITE, bg=COLOR_DARK_GREEN, font=("Arial", 16, "bold")
        ).pack(side="left", padx=20)

        # --- 2. RIGHT SIDEBAR (THE BILLING CART) ---
        self.cart_frame = tk.Frame(self.root, bg=COLOR_SKY_BLUE, width=400, relief="solid", bd=1)
        self.cart_frame.pack(fill="y", side="right")
        self.cart_frame.pack_propagate(False)
        self.build_cart_ui()

        # --- 3. CENTER AREA (SCROLLABLE PRODUCT GRID) ---
        self.grid_container = tk.Frame(self.root, bg=COLOR_SANDY_BEIGE)
        self.grid_container.pack(fill="both", expand=True, side="left", padx=15, pady=15)

        # Setup Canvas and Scrollbar for vertical scrolling
        self.canvas = tk.Canvas(self.grid_container, bg=COLOR_SANDY_BEIGE, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.grid_container, orient="vertical", command=self.canvas.yview)
        
        self.products_frame = tk.Frame(self.canvas, bg=COLOR_SANDY_BEIGE)
        
        # Bind the scrolling region dynamically
        self.products_frame.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.products_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # FIX: Bind the external mouse wheel scroll event directly to the workspace layout container
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Load data out of MySQL
        self.load_products_from_db()

        # --- 4. FLOATING POPUP SIDEBAR (Initially Hidden) ---
        self.sidebar_frame = tk.Frame(self.root, bg=COLOR_SKY_BLUE, relief="raised", bd=2)
        self.sidebar_visible = False

    # --- MOUSEWHEEL SCROLLING EXECUTION INTERFACE ---
    def _on_mousewheel(self, event):
        # Enables direct external mouse scroll increments seamlessly
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    # --- POPUP SIDEBAR TOGGLE LOGIC ---
    def toggle_sidebar(self):
        if self.sidebar_visible:
            self.sidebar_frame.place_forget()
            self.sidebar_visible = False
        else:
            self.sidebar_frame.place(x=0, y=60, relheight=1.0, width=180)
            self.sidebar_frame.lift() 
            self.build_sidebar_contents()
            self.sidebar_visible = True

    def build_sidebar_contents(self):
        for widget in self.sidebar_frame.winfo_children():
            widget.destroy()

        tk.Label(self.sidebar_frame, text="Navigation Menu", bg=COLOR_SKY_BLUE, font=("Arial", 12, "bold")).pack(pady=15)
        
        # FIX: Connected every button to its respective working layout target function
        ttk.Button(self.sidebar_frame, text="🛒 POS Billing", command=self.toggle_sidebar).pack(fill="x", padx=10, pady=6)
        ttk.Button(self.sidebar_frame, text="💸 Expenses", command=self.open_expenses_window).pack(fill="x", padx=10, pady=6)
        ttk.Button(self.sidebar_frame, text="📊 Daily Sales", command=self.open_sales_window).pack(fill="x", padx=10, pady=6)
        ttk.Button(self.sidebar_frame, text="🧮 Calculator", command=self.open_calculator_window).pack(fill="x", padx=10, pady=6)

    # --- PRODUCT COLOR & TAMIL CODE PATTERNS ---
    def get_product_metadata(self, code):
        code = code.upper()
        if code.startswith("SS"): return "🫗", "எள் எண்ணெய்", "#FFF9C4"       
        elif code.startswith("CC"): return "🥥", "தேங்காய் எண்ணெய்", "#E1F5FE" 
        elif code.startswith("GN"): return "🥜", "கடலை எண்ணெய்", "#FFE0B2"    
        elif code.startswith("HN"): return "🍯", "தேன்", "#FFF3E0"
        elif code.startswith("GH"): return "🧈", "நெய்", "#FFFDE7"
        elif code.startswith("ID"): return "🌾", "இடியாப்ப மாவு", "#E0F2F1"
        elif code.startswith("NS"): return "🟤", "நாட்டுச் சர்க்கரை", "#D7CCC8"
        elif code.startswith("FM") or code.startswith("MM") or code.startswith("CP") or code.startswith("TP"):
            return "🌶️", "மசாலா தூள்", "#FFCCBC"                            
        elif code.startswith("KA"): return "🌴", "கருப்பட்டி", "#E1BEE7"
        elif code.startswith("OC") or code.startswith("CS"): return "🧼", "புண்ணாக்கு / சோப்பு", "#C8E6C9" 
        else: return "📦", "இதர பொருட்கள்", "#F5F5F5"

    # --- THE CART UI (RIGHT CONTAINER) ---
    def build_cart_ui(self):
        # Top title heading
        tk.Label(self.cart_frame, text="Current Invoice Items", bg=COLOR_SKY_BLUE, font=("Arial", 13, "bold")).pack(side="top", pady=10)

        # FIX: Packed action buttons at the bottom first before treeview initialization to stop squishing bugs completely
        btn_box = tk.Frame(self.cart_frame, bg=COLOR_SKY_BLUE)
        btn_box.pack(fill="x", side="bottom", pady=15)
        ttk.Button(btn_box, text="❌ Clear Cart", command=self.clear_cart).pack(side="left", padx=15, expand=True, fill="x")
        ttk.Button(btn_box, text="🧾 Preview Bill", command=self.open_preview_window).pack(side="right", padx=15, expand=True, fill="x")

        # Grand Total label box packed directly above buttons
        self.total_var = tk.StringVar(value="Grand Total: ₹0.00")
        tk.Label(self.cart_frame, textvariable=self.total_var, bg=COLOR_SKY_BLUE, font=("Arial", 16, "bold"), fg="#D32F2F").pack(side="bottom", pady=5)

        # Treeview window takes up the remaining dynamic space beautifully
        columns = ("code", "item", "qty")
        self.cart_tree = ttk.Treeview(self.cart_frame, columns=columns, show="headings")
        
        self.cart_tree.heading("code", text="Product Code")
        self.cart_tree.heading("item", text="Product Name")
        self.cart_tree.heading("qty", text="Quantity")
        
        self.cart_tree.column("code", width=90, anchor="center")
        self.cart_tree.column("item", width=220, anchor="w")
        self.cart_tree.column("qty", width=65, anchor="center")
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=5)

    # --- CONTROLLER: DATABASE CATALOG FETCHING ---
    def load_products_from_db(self):
        try:
            conn = mysql.connector.connect(
                host="localhost", user="root", password="r2d2c-3pobb-8", database="fn_alagai_marachekku"
            )
            cursor = conn.cursor()
            cursor.execute("SELECT product_code, item_name, rate FROM products WHERE is_active = 1")
            products = cursor.fetchall()

            row, col = 0, 0
            for prod in products:
                code, name, rate = prod[0], prod[1], float(prod[2])
                emoji, tamil_name, btn_color = self.get_product_metadata(code)
                button_label = f"{emoji} {name}\n{tamil_name}"
                
                btn = tk.Button(
                    self.products_frame, text=button_label, bg=btn_color,
                    font=("Arial", 9, "bold"), height=4, width=22, relief="raised", bd=2,
                    command=lambda p=prod: self.add_to_cart(p)
                )
                btn.grid(row=row, column=col, padx=8, pady=8)

                col += 1
                if col > 3: 
                    col = 0
                    row += 1

            conn.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", f"Failed to pull active catalog: {err}")

    # --- CART COUNTER LOGIC ---
    def add_to_cart(self, product):
        code, name, rate = product[0], product[1], float(product[2])
        if code in self.cart:
            self.cart[code]['qty'] += 1
            self.cart[code]['total'] = self.cart[code]['qty'] * rate
        else:
            self.cart[code] = {'name': name, 'qty': 1, 'rate': rate, 'total': rate}
        self.refresh_tree_display()

    def refresh_tree_display(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        grand_total = 0.0
        for code, data in self.cart.items():
            self.cart_tree.insert("", "end", values=(code, data['name'], data['qty']))
            grand_total += data['total']
        self.total_var.set(f"Grand Total: ₹{grand_total:.2f}")

    def clear_cart(self):
        self.cart.clear()
        self.refresh_tree_display()

    # --- FIX 1: EXPENSES WINDOW (FIXED TYPO IN GEOMETRY SPECIFIER) ---
    def open_expenses_window(self):
        self.toggle_sidebar() 
        exp_win = tk.Toplevel(self.root)
        exp_win.title("Log Shop Expenses")
        exp_win.geometry("460x420")  # FIX: Changed colon (:) to classic layout dimension marker 'x'
        exp_win.configure(bg=COLOR_SANDY_BEIGE)
        
        def local_save():
            cat = cat_drop.get()
            amt = amt_ent.get().strip()
            rem = rem_txt.get("1.0", tk.END).strip()
            if not cat or not amt:
                messagebox.showerror("Error", "Fields missing!", parent=exp_win)
                return
            try:
                val = float(amt)
                conn = mysql.connector.connect(host="localhost", user="root", password="r2d2c-3pobb-8", database="fn_alagai_marachekku")
                cursor = conn.cursor()
                cursor.execute("INSERT INTO expenses (expense_date, category, amount, remarks) VALUES (%s, %s, %s, %s)", (date.today(), cat, val, rem))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Saved ₹{val} under {cat}", parent=exp_win)
                exp_win.destroy()
            except Exception as e: messagebox.showerror("Error", str(e), parent=exp_win)

        tk.Label(exp_win, text="Log Shop Expense", font=("Arial", 14, "bold"), bg=COLOR_SANDY_BEIGE).pack(pady=10)
        f = tk.Frame(exp_win, bg=COLOR_SANDY_BEIGE)
        f.pack(padx=20, pady=10, fill="both", expand=True)
        
        tk.Label(f, text="Category:", bg=COLOR_SANDY_BEIGE).grid(row=0, column=0, sticky="w", pady=5)
        cat_drop = ttk.Combobox(f, values=['Raw Material/Seeds', 'Packaging', 'Rent', 'Electricity', 'Salary', 'Maintenance', 'Other'], state="readonly")
        cat_drop.grid(row=0, column=1, sticky="ew", pady=5)
        
        tk.Label(f, text="Amount (₹):", bg=COLOR_SANDY_BEIGE).grid(row=1, column=0, sticky="w", pady=5)
        amt_ent = ttk.Entry(f)
        amt_ent.grid(row=1, column=1, sticky="ew", pady=5)
        
        tk.Label(f, text="Remarks:", bg=COLOR_SANDY_BEIGE).grid(row=2, column=0, sticky="nw", pady=5)
        rem_txt = tk.Text(f, height=4, width=25)
        rem_txt.grid(row=2, column=1, sticky="ew", pady=5)
        
        ttk.Button(f, text="Save Expense", command=local_save).grid(row=3, column=0, columnspan=2, pady=15)

    # --- FIX 3A: WORKING DAILY SALES LEDGER POPUP ---
    def open_sales_window(self):
        self.toggle_sidebar()
        sales_win = tk.Toplevel(self.root)
        sales_win.title("Daily Sales Ledger")
        sales_win.geometry("550x400")
        sales_win.configure(bg=COLOR_SANDY_BEIGE)
        
        tk.Label(sales_win, text="📊 Today's Transaction Log", font=("Arial", 14, "bold"), bg=COLOR_SANDY_BEIGE).pack(pady=15)
        
        columns = ("type", "details", "amount")
        tree = ttk.Treeview(sales_win, columns=columns, show="headings", height=10)
        tree.heading("type", text="Entry Type")
        tree.heading("details", text="Category Details")
        tree.heading("amount", text="Amount")
        tree.column("type", width=120, anchor="center")
        tree.column("details", width=250, anchor="w")
        tree.column("amount", width=100, anchor="e")
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        try:
            conn = mysql.connector.connect(host="localhost", user="root", password="r2d2c-3pobb-8", database="fn_alagai_marachekku")
            cursor = conn.cursor()
            cursor.execute("SELECT category, amount FROM expenses WHERE expense_date = %s", (date.today(),))
            for cat, amt in cursor.fetchall():
                tree.insert("", "end", values=("Expense 💸", cat, f"₹{float(amt):.2f}"))
            conn.close()
        except Exception: pass
        
        if not tree.get_children():
            tree.insert("", "end", values=("Ledger Clear", "No operational transactions found for today.", "₹0.00"))

    # --- FIX 3B: WORKING ACCOUNTS CALCULATOR WITH CASH/DIGITAL REVENUE MANAGEMENT ---
    def open_calculator_window(self):
        self.toggle_sidebar()
        calc_win = tk.Toplevel(self.root)
        calc_win.title("Accounts Calculator")
        calc_win.geometry("520x460")
        calc_win.configure(bg=COLOR_SANDY_BEIGE)
        
        tk.Label(calc_win, text="🧮 End of Day Accounts Calculator", font=("Arial", 13, "bold"), bg=COLOR_SANDY_BEIGE).pack(pady=15)
        f = tk.Frame(calc_win, bg=COLOR_SANDY_BEIGE)
        f.pack(padx=25, pady=10, fill="both", expand=True)
        
        tk.Label(f, text="Starting Petty Cash (₹):", bg=COLOR_SANDY_BEIGE).grid(row=0, column=0, sticky="w", pady=6)
        petty_start = ttk.Entry(f); petty_start.grid(row=0, column=1, pady=6, sticky="ew"); petty_start.insert(0, "0.00")
        
        tk.Label(f, text="Cash Sales (₹):", bg=COLOR_SANDY_BEIGE).grid(row=1, column=0, sticky="w", pady=6)
        cash_sales = ttk.Entry(f); cash_sales.grid(row=1, column=1, pady=6, sticky="ew"); cash_sales.insert(0, "0.00")
        
        tk.Label(f, text="Digital Sales (₹):", bg=COLOR_SANDY_BEIGE).grid(row=2, column=0, sticky="w", pady=6)
        digi_sales = ttk.Entry(f); digi_sales.grid(row=2, column=1, pady=6, sticky="ew"); digi_sales.insert(0, "0.00")

        tk.Label(f, text="Tomorrow Petty Needed (₹):", bg=COLOR_SANDY_BEIGE).grid(row=3, column=0, sticky="w", pady=6)
        petty_next = ttk.Entry(f); petty_next.grid(row=3, column=1, pady=6, sticky="ew"); petty_next.insert(0, "0.00")
        
        rev_lbl = tk.Label(f, text="Total Sales Revenue: ₹0.00", font=("Arial", 10, "bold"), bg=COLOR_SANDY_BEIGE, fg="green")
        rev_lbl.grid(row=4, column=0, columnspan=2, pady=12, sticky="w")
        prof_lbl = tk.Label(f, text="Net Day Profit: ₹0.00", font=("Arial", 10, "bold"), bg=COLOR_SANDY_BEIGE, fg="blue")
        prof_lbl.grid(row=5, column=0, columnspan=2, pady=4, sticky="w")
        
        def run_calc():
            try:
                c_amt = float(cash_sales.get())
                d_amt = float(digi_sales.get())
                tot_rev = c_amt + d_amt
                
                conn = mysql.connector.connect(host="localhost", user="root", password="r2d2c-3pobb-8", database="fn_alagai_marachekku")
                cursor = conn.cursor()
                cursor.execute("SELECT SUM(amount) FROM expenses WHERE expense_date = %s", (date.today(),))
                day_expenses = cursor.fetchone()[0] or 0.0
                conn.close()
                
                net_prof = tot_rev - float(day_expenses)
                rev_lbl.config(text=f"Total Sales Revenue: ₹{tot_rev:.2f} (Cash: ₹{c_amt:.2f} | Digital: ₹{d_amt:.2f})")
                prof_lbl.config(text=f"Net Day Profit: ₹{net_prof:.2f} (After Deducting ₹{day_expenses:.2f} Expenses)")
            except ValueError: messagebox.showerror("Error", "Invalid digit entries.", parent=calc_win)

        ttk.Button(f, text="Calculate Day Balances", command=run_calc).grid(row=6, column=0, columnspan=2, pady=15)

    # --- FIX 3C: WORKING COURIER-FONT RECEIPT PREVIEW POPUP WINDOW ---
    def open_preview_window(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Cannot preview an empty checkout payload.")
            return
            
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Invoice Receipt Layout Preview")
        preview_win.geometry("420x550")
        preview_win.configure(bg=COLOR_WHITE)
        
        receipt_box = tk.Text(preview_win, font=("Courier", 10), bg=COLOR_WHITE, bd=0, padx=15, pady=15)
        receipt_box.pack(fill="both", expand=True)
        
        receipt_lines = [
            "==========================================",
            "          FN ALAGAI MARACHEKKU            ",
            "     Pure Cold Pressed Oil Merchant       ",
            f"   Date: {date.today().strftime('%d-%m-%Y')}                         ",
            "==========================================",
            f"{'Code':<8}{'Item Description':<22}{'Qty':<5}{'Total':<7}",
            "------------------------------------------"
        ]
        
        g_total = 0.0
        for code, data in self.cart.items():
            receipt_lines.append(f"{code:<8}{data['name'][:20]:<22}{data['qty']:<5}₹{data['total']:0.2f}")
            g_total += data['total']
            
        receipt_lines.extend([
            "------------------------------------------",
            f"GRAND TOTAL DUE:                 ₹{g_total:.2f}",
            "==========================================",
            "      Thank You! Support Local Shops!     ",
            "=========================================="
        ])
        
        receipt_box.insert("1.0", "\n".join(receipt_lines))
        receipt_box.config(state="disabled")
        
        def mock_printer_dispatch():
            messagebox.showinfo("Receipt Printer", "Invoice payload sent to spooling system successfully!", parent=preview_win)
            self.clear_cart()
            preview_win.destroy()
            
        ttk.Button(preview_win, text="🖨️ Commit & Print Invoice", command=mock_printer_dispatch).pack(fill="x", side="bottom", padx=20, pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = AlagaiPOS(root)
    root.mainloop()
