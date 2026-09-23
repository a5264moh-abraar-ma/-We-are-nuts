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
        tk.Label(self.logo_space, text="[ LOGO ]", bg=COLOR_WHITE, font=("Arial", 8, "bold")).pack(expand=True)

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

        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        # Load data out of MySQL
        self.load_products_from_db()

        # --- 4. FLOATING POPUP SIDEBAR (Initially Hidden) ---
        self.sidebar_frame = tk.Frame(self.root, bg=COLOR_SKY_BLUE, relief="raised", bd=2)
        self.sidebar_visible = False

    # --- DATABASE CONNECTION HELPER ---
    def get_db_connection(self):
        return mysql.connector.connect(
            host="localhost", 
            user="root", 
            password="r2d2c-3pobb-8", 
            database="fn_alagai_marachekku"
        )

    # --- MOUSEWHEEL SCROLLING EXECUTION INTERFACE ---
    def _on_mousewheel(self, event):
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
        
        ttk.Button(self.sidebar_frame, text="🛒 POS Billing", command=self.toggle_sidebar).pack(fill="x", padx=10, pady=6)
        ttk.Button(self.sidebar_frame, text="📦 Manage Stock", command=self.open_stock_window).pack(fill="x", padx=10, pady=6)
        ttk.Button(self.sidebar_frame, text="🔮 Yield Predictor", command=self.open_predictor_window).pack(fill="x", padx=10, pady=6)
        ttk.Button(self.sidebar_frame, text="💸 Expenses", command=self.open_expenses_window).pack(fill="x", padx=10, pady=6)
        ttk.Button(self.sidebar_frame, text="📊 Daily Sales", command=self.open_sales_window).pack(fill="x", padx=10, pady=6)
        ttk.Button(self.sidebar_frame, text="🧮 Calculator", command=self.open_calculator_window).pack(fill="x", padx=10, pady=6)

    # --- PRODUCT COLOR & TAMIL CODE PATTERNS ---
    def get_product_metadata(self, code):
        if not code: return "📦", "இதர பொருட்கள்", "#F5F5F5"
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
        tk.Label(self.cart_frame, text="Current Invoice Items", bg=COLOR_SKY_BLUE, font=("Arial", 13, "bold")).pack(side="top", pady=10)

        btn_box = tk.Frame(self.cart_frame, bg=COLOR_SKY_BLUE)
        btn_box.pack(fill="x", side="bottom", pady=15)
        ttk.Button(btn_box, text="❌ Clear Cart", command=self.clear_cart).pack(side="left", padx=15, expand=True, fill="x")
        ttk.Button(btn_box, text="🧾 Preview Bill", command=self.open_preview_window).pack(side="right", padx=15, expand=True, fill="x")

        self.total_var = tk.StringVar(value="Grand Total: ₹0.00")
        tk.Label(self.cart_frame, textvariable=self.total_var, bg=COLOR_SKY_BLUE, font=("Arial", 16, "bold"), fg="#D32F2F").pack(side="bottom", pady=5)

        columns = ("code", "item", "qty")
        self.cart_tree = ttk.Treeview(self.cart_frame, columns=columns, show="headings")
        
        self.cart_tree.heading("code", text="Code")
        self.cart_tree.heading("item", text="Product Name")
        self.cart_tree.heading("qty", text="Qty")
        
        self.cart_tree.column("code", width=70, anchor="center")
        self.cart_tree.column("item", width=220, anchor="w")
        self.cart_tree.column("qty", width=55, anchor="center")
        self.cart_tree.pack(fill="both", expand=True, padx=10, pady=5)

    # --- CONTROLLER: DATABASE CATALOG FETCHING (NOW WITH STOCK) ---
    def refresh_product_grid(self):
        for widget in self.products_frame.winfo_children():
            widget.destroy()
        self.load_products_from_db()

    def load_products_from_db(self):
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT Product_ID, Product_Code, Item_Name, Rate, Current_Stock FROM products WHERE Is_Active = 1")
            products = cursor.fetchall()

            row, col = 0, 0
            for prod in products:
                prod_id, code, name, rate, stock = prod[0], prod[1], prod[2], float(prod[3]), int(prod[4] or 0)
                emoji, tamil_name, btn_color = self.get_product_metadata(code)
                
                if code:
                    button_label = f"{emoji} {name}\n{tamil_name}\nStock: {stock}"
                else:
                    button_label = f"{emoji} {name}\nStock: {stock}"
                
                btn = tk.Button(
                    self.products_frame, text=button_label, bg=btn_color,
                    font=("Arial", 9, "bold"), height=5, width=22, relief="raised", bd=2,
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
        prod_id, code, name, rate = product[0], product[1], product[2], float(product[3])
        display_code = code if code else f"ID:{prod_id}"
        
        if prod_id in self.cart:
            self.cart[prod_id]['qty'] += 1
            self.cart[prod_id]['total'] = self.cart[prod_id]['qty'] * rate
        else:
            self.cart[prod_id] = {'code': display_code, 'name': name, 'qty': 1, 'rate': rate, 'total': rate}
        self.refresh_tree_display()

    def refresh_tree_display(self):
        for row in self.cart_tree.get_children():
            self.cart_tree.delete(row)
        grand_total = 0.0
        for prod_id, data in self.cart.items():
            self.cart_tree.insert("", "end", values=(data['code'], data['name'], data['qty']))
            grand_total += data['total']
        self.total_var.set(f"Grand Total: ₹{grand_total:.2f}")

    def clear_cart(self):
        self.cart.clear()
        self.refresh_tree_display()

    # --- PREDICTIVE SOFTWARE: PRODUCTION YIELD CALCULATOR ---
    def open_predictor_window(self):
        self.toggle_sidebar()
        pred_win = tk.Toplevel(self.root)
        pred_win.title("Production Yield Predictor")
        pred_win.geometry("500x450")
        pred_win.configure(bg=COLOR_SANDY_BEIGE)

        tk.Label(pred_win, text="🔮 Marachekku Yield Predictor", font=("Arial", 15, "bold"), bg=COLOR_SANDY_BEIGE).pack(pady=15)
        
        f = tk.Frame(pred_win, bg=COLOR_SANDY_BEIGE)
        f.pack(padx=20, pady=10, fill="both", expand=True)

        tk.Label(f, text="Select Raw Material:", bg=COLOR_SANDY_BEIGE, font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="w", pady=10)
        
        materials = [
            'Sesame Seeds (Ellu)', 
            'Groundnut (Kadalai)', 
            'Copra / Coconut (Thengai)', 
            'Raw Spices (to Masala Powder)'
        ]
        mat_drop = ttk.Combobox(f, values=materials, state="readonly", width=25)
        mat_drop.grid(row=0, column=1, sticky="ew", pady=10)
        mat_drop.set(materials[0])

        tk.Label(f, text="Input Quantity (in KG):", bg=COLOR_SANDY_BEIGE, font=("Arial", 10, "bold")).grid(row=1, column=0, sticky="w", pady=10)
        qty_ent = ttk.Entry(f, font=("Arial", 12))
        qty_ent.grid(row=1, column=1, sticky="ew", pady=10)

        # Output Display Frame
        res_frame = tk.Frame(pred_win, bg=COLOR_WHITE, relief="sunken", bd=2)
        res_frame.pack(fill="both", expand=True, padx=20, pady=15)

        res_lbl = tk.Label(res_frame, text="Awaiting Input...", bg=COLOR_WHITE, font=("Arial", 11), justify="left")
        res_lbl.pack(pady=20, padx=20, anchor="w")

        def calculate_prediction():
            material = mat_drop.get()
            try:
                weight = float(qty_ent.get().strip())
                if weight <= 0:
                    raise ValueError
                
                # Standard industry extraction rates (Percentages & Densities)
                # Density formula: Liters = KG / Density
                if material == 'Sesame Seeds (Ellu)':
                    oil_kg = weight * 0.45      # 45% oil extraction
                    cake_kg = weight * 0.50     # 50% cake residue
                    loss = weight * 0.05        # 5% moisture/evaporation loss
                    oil_ltr = oil_kg / 0.92     # Sesame oil density ~0.92 kg/L
                    
                    output = f"🧪 PREDICTED YIELD FOR {weight} KG SESAME:\n\n"
                    output += f"🫗 Pure Sesame Oil: {oil_kg:.2f} KG (approx {oil_ltr:.2f} Liters)\n"
                    output += f"🧼 Sesame Oil Cake (Punnakku): {cake_kg:.2f} KG\n"
                    output += f"💨 Estimated Process Loss: {loss:.2f} KG"

                elif material == 'Groundnut (Kadalai)':
                    oil_kg = weight * 0.43
                    cake_kg = weight * 0.52
                    loss = weight * 0.05
                    oil_ltr = oil_kg / 0.91     # Groundnut oil density ~0.91 kg/L
                    
                    output = f"🧪 PREDICTED YIELD FOR {weight} KG GROUNDNUT:\n\n"
                    output += f"🥜 Pure Groundnut Oil: {oil_kg:.2f} KG (approx {oil_ltr:.2f} Liters)\n"
                    output += f"🧼 Groundnut Oil Cake (Punnakku): {cake_kg:.2f} KG\n"
                    output += f"💨 Estimated Process Loss: {loss:.2f} KG"

                elif material == 'Copra / Coconut (Thengai)':
                    oil_kg = weight * 0.62
                    cake_kg = weight * 0.33
                    loss = weight * 0.05
                    oil_ltr = oil_kg / 0.92     # Coconut oil density ~0.92 kg/L
                    
                    output = f"🧪 PREDICTED YIELD FOR {weight} KG COPRA:\n\n"
                    output += f"🥥 Pure Coconut Oil: {oil_kg:.2f} KG (approx {oil_ltr:.2f} Liters)\n"
                    output += f"🧼 Coconut Oil Cake (Punnakku): {cake_kg:.2f} KG\n"
                    output += f"💨 Estimated Process Loss: {loss:.2f} KG"

                elif material == 'Raw Spices (to Masala Powder)':
                    powder_kg = weight * 0.95
                    loss = weight * 0.05
                    
                    output = f"🧪 PREDICTED YIELD FOR {weight} KG RAW SPICES:\n\n"
                    output += f"🌶️ Ground Masala Powder: {powder_kg:.2f} KG\n"
                    output += f"💨 Grinding/Moisture Loss: {loss:.2f} KG"

                res_lbl.config(text=output, fg="darkgreen", font=("Arial", 11, "bold"))

            except ValueError:
                res_lbl.config(text="❌ Invalid Input! Please enter a valid number\nfor the weight in KG.", fg="red")

        ttk.Button(f, text="⚡ Run Prediction AI", command=calculate_prediction).grid(row=2, column=0, columnspan=2, pady=15)

    # --- MANAGE INVENTORY STOCK WINDOW ---
    def open_stock_window(self):
        self.toggle_sidebar()
        stock_win = tk.Toplevel(self.root)
        stock_win.title("Manage Inventory Stock")
        stock_win.geometry("600x500")
        stock_win.configure(bg=COLOR_SANDY_BEIGE)
        
        tk.Label(stock_win, text="📦 Update Product Stock", font=("Arial", 14, "bold"), bg=COLOR_SANDY_BEIGE).pack(pady=10)
        
        columns = ("id", "code", "name", "stock")
        tree = ttk.Treeview(stock_win, columns=columns, show="headings", height=12)
        tree.heading("id", text="ID")
        tree.heading("code", text="Code")
        tree.heading("name", text="Product Name")
        tree.heading("stock", text="Current Stock")
        
        tree.column("id", width=50, anchor="center")
        tree.column("code", width=100, anchor="center")
        tree.column("name", width=250, anchor="w")
        tree.column("stock", width=100, anchor="center")
        tree.pack(fill="both", expand=True, padx=20, pady=5)
        
        def load_stock_data():
            for row in tree.get_children(): tree.delete(row)
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT Product_ID, Product_Code, Item_Name, Current_Stock FROM products WHERE Is_Active = 1")
                for pid, code, name, stk in cursor.fetchall():
                    tree.insert("", "end", values=(pid, code, name, int(stk or 0)))
                conn.close()
            except Exception as e: 
                messagebox.showerror("Error", str(e), parent=stock_win)

        load_stock_data()
        
        ctrl_frame = tk.Frame(stock_win, bg=COLOR_SANDY_BEIGE)
        ctrl_frame.pack(fill="x", padx=20, pady=15)
        
        tk.Label(ctrl_frame, text="Quantity to Add:", bg=COLOR_SANDY_BEIGE, font=("Arial", 10, "bold")).pack(side="left")
        qty_ent = ttk.Entry(ctrl_frame, width=15)
        qty_ent.pack(side="left", padx=10)
        
        def update_stock():
            selected = tree.focus()
            if not selected:
                messagebox.showwarning("Warning", "Please select a product from the list first!", parent=stock_win)
                return
            item_vals = tree.item(selected, "values")
            prod_id = item_vals[0]
            prod_name = item_vals[2]
            
            try:
                add_qty = int(qty_ent.get().strip())
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE products SET Current_Stock = Current_Stock + %s WHERE Product_ID = %s", (add_qty, prod_id))
                conn.commit()
                conn.close()
                
                messagebox.showinfo("Success", f"Added {add_qty} units to '{prod_name}'.", parent=stock_win)
                qty_ent.delete(0, tk.END)
                
                load_stock_data()
                self.refresh_product_grid() 
                
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid integer number.", parent=stock_win)
            except Exception as e:
                messagebox.showerror("Error", str(e), parent=stock_win)
                
        ttk.Button(ctrl_frame, text="➕ Add to Stock", command=update_stock).pack(side="left", padx=10)

    # --- EXPENSES WINDOW ---
    def open_expenses_window(self):
        self.toggle_sidebar() 
        exp_win = tk.Toplevel(self.root)
        exp_win.title("Log Shop Expenses")
        exp_win.geometry("460x420") 
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
                conn = self.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO expenses (Expense_Date, Category, Amount, Remarks) VALUES (%s, %s, %s, %s)", 
                    (date.today(), cat, val, rem)
                )
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"Saved ₹{val} under {cat}", parent=exp_win)
                exp_win.destroy()
            except Exception as e: messagebox.showerror("Error", str(e), parent=exp_win)

        tk.Label(exp_win, text="Log Shop Expense", font=("Arial", 14, "bold"), bg=COLOR_SANDY_BEIGE).pack(pady=10)
        f = tk.Frame(exp_win, bg=COLOR_SANDY_BEIGE)
        f.pack(padx=20, pady=10, fill="both", expand=True)
        
        tk.Label(f, text="Category:", bg=COLOR_SANDY_BEIGE).grid(row=0, column=0, sticky="w", pady=5)
        
        categories = [
            'Raw Material/Seeds', 'Packaging', 'Rent', 'Electricity', 'Salary', 'Maintenance', 
            'Vehicle - Bike', 'Vehicle - Car', 
            'Personal - Medical', 'Personal - Travel', 'Personal - House', 
            'Other'
        ]
        cat_drop = ttk.Combobox(f, values=categories, state="readonly", width=25)
        cat_drop.grid(row=0, column=1, sticky="ew", pady=5)
        
        tk.Label(f, text="Amount (₹):", bg=COLOR_SANDY_BEIGE).grid(row=1, column=0, sticky="w", pady=5)
        amt_ent = ttk.Entry(f)
        amt_ent.grid(row=1, column=1, sticky="ew", pady=5)
        
        tk.Label(f, text="Remarks:", bg=COLOR_SANDY_BEIGE).grid(row=2, column=0, sticky="nw", pady=5)
        rem_txt = tk.Text(f, height=4, width=25)
        rem_txt.grid(row=2, column=1, sticky="ew", pady=5)
        
        ttk.Button(f, text="Save Expense", command=local_save).grid(row=3, column=0, columnspan=2, pady=15)

    # --- DAILY SALES WINDOW ---
    def open_sales_window(self):
        self.toggle_sidebar()
        sales_win = tk.Toplevel(self.root)
        sales_win.title("Daily Sales Ledger")
        sales_win.geometry("550x400")
        sales_win.configure(bg=COLOR_SANDY_BEIGE)
        
        tk.Label(sales_win, text="📊 Today's Revenue Log", font=("Arial", 14, "bold"), bg=COLOR_SANDY_BEIGE).pack(pady=15)
        
        columns = ("type", "details", "amount")
        tree = ttk.Treeview(sales_win, columns=columns, show="headings", height=10)
        tree.heading("type", text="Payment Mode")
        tree.heading("details", text="Item Details")
        tree.heading("amount", text="Amount")
        tree.column("type", width=120, anchor="center")
        tree.column("details", width=250, anchor="w")
        tree.column("amount", width=100, anchor="e")
        tree.pack(fill="both", expand=True, padx=20, pady=10)
        
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT sp.Payment_Mode, pr.Item_Name, sd.Quantity, sd.Total_Price 
                FROM sales_details sd
                JOIN sales_parent sp ON sd.Invoice_ID = sp.Invoice_ID
                JOIN products pr ON sd.Product_ID = pr.Product_ID
                WHERE DATE(sp.Sale_Date) = %s
            """, (date.today(),))
            
            sales = cursor.fetchall()
            
            total_revenue = 0.0
            for p_mode, name, qty, amt in sales:
                tree.insert("", "end", values=(f"{p_mode} 💰", f"{qty}x {name}", f"₹{float(amt):.2f}"))
                total_revenue += float(amt)
                
            if sales:
                tree.insert("", "end", values=("TOTAL", "Gross Revenue", f"₹{total_revenue:.2f}"))
                
            conn.close()
        except Exception as e: 
            messagebox.showerror("DB Error", str(e), parent=sales_win)
        
        if not tree.get_children():
            tree.insert("", "end", values=("Ledger Clear", "No operational transactions found for today.", "₹0.00"))

    # --- CALCULATOR ---
    def open_calculator_window(self):
        self.toggle_sidebar()
        calc_win = tk.Toplevel(self.root)
        calc_win.title("Accounts Calculator")
        calc_win.geometry("520x460")
        calc_win.configure(bg=COLOR_SANDY_BEIGE)
        
        tk.Label(calc_win, text="🧮 End of Day Accounts Calculator", font=("Arial", 13, "bold"), bg=COLOR_SANDY_BEIGE).pack(pady=15)
        f = tk.Frame(calc_win, bg=COLOR_SANDY_BEIGE)
        f.pack(padx=25, pady=10, fill="both", expand=True)

        day_cash_total = 0.0
        day_digital_total = 0.0
        day_expenses = 0.0

        try:
            conn = self.get_db_connection()
            cursor = conn.cursor()
            
            cursor.execute("SELECT SUM(Grand_Total) FROM sales_parent WHERE DATE(Sale_Date) = %s AND Payment_Mode = 'Cash'", (date.today(),))
            res_cash = cursor.fetchone()
            day_cash_total = float(res_cash[0]) if res_cash and res_cash[0] else 0.0
            
            cursor.execute("SELECT SUM(Grand_Total) FROM sales_parent WHERE DATE(Sale_Date) = %s AND Payment_Mode IN ('UPI', 'Card', 'Credit')", (date.today(),))
            res_digi = cursor.fetchone()
            day_digital_total = float(res_digi[0]) if res_digi and res_digi[0] else 0.0
            
            cursor.execute("SELECT SUM(Amount) FROM expenses WHERE Expense_Date = %s", (date.today(),))
            res2 = cursor.fetchone()
            day_expenses = float(res2[0]) if res2 and res2[0] else 0.0
            conn.close()
        except Exception:
            pass

        tk.Label(f, text="Starting Petty Cash (₹):", bg=COLOR_SANDY_BEIGE).grid(row=0, column=0, sticky="w", pady=6)
        petty_start = ttk.Entry(f); petty_start.grid(row=0, column=1, pady=6, sticky="ew"); petty_start.insert(0, "0.00")
        
        tk.Label(f, text=f"Total Cash Sales (₹):", bg=COLOR_SANDY_BEIGE).grid(row=1, column=0, sticky="w", pady=6)
        cash_sales = ttk.Entry(f); cash_sales.grid(row=1, column=1, pady=6, sticky="ew"); cash_sales.insert(0, f"{day_cash_total:.2f}")

        tk.Label(f, text=f"Total Digital Sales (₹):", bg=COLOR_SANDY_BEIGE).grid(row=2, column=0, sticky="w", pady=6)
        digi_sales = ttk.Entry(f); digi_sales.grid(row=2, column=1, pady=6, sticky="ew"); digi_sales.insert(0, f"{day_digital_total:.2f}")
        
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
                net_prof = tot_rev - day_expenses
                rev_lbl.config(text=f"Total Sales Revenue: ₹{tot_rev:.2f}")
                prof_lbl.config(text=f"Net Day Profit: ₹{net_prof:.2f} (After Deducting ₹{day_expenses:.2f} Expenses)")
            except ValueError: 
                messagebox.showerror("Error", "Invalid digit entries.", parent=calc_win)

        ttk.Button(f, text="Calculate Day Balances", command=run_calc).grid(row=6, column=0, columnspan=2, pady=15)

    # --- PREVIEW AND PRINT POPUP ---
    def open_preview_window(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Cannot preview an empty checkout payload.")
            return
            
        preview_win = tk.Toplevel(self.root)
        preview_win.title("Invoice Receipt Layout Preview")
        preview_win.geometry("420x600")
        preview_win.configure(bg=COLOR_WHITE)

        tk.Label(preview_win, text="Payment Mode:", bg=COLOR_WHITE, font=("Arial", 10, "bold")).pack(pady=(10, 0))
        payment_var = tk.StringVar(value="Cash")
        payment_drop = ttk.Combobox(preview_win, textvariable=payment_var, values=['Cash', 'UPI', 'Card', 'Credit'], state="readonly")
        payment_drop.pack(pady=5)
        
        receipt_box = tk.Text(preview_win, font=("Courier", 10), bg=COLOR_WHITE, bd=0, padx=15, pady=15)
        receipt_box.pack(fill="both", expand=True)
        
        receipt_text = "==========================================\n"
        receipt_text += "          FN ALAGAI MARACHEKKU            \n"
        receipt_text += "     Pure Cold Pressed Oil Merchant       \n"
        receipt_text += f"   Date: {date.today().strftime('%d-%m-%Y')}                         \n"
        receipt_text += "==========================================\n"
        receipt_text += f"{'Code':<8}{'Item Description':<22}{'Qty':<5}{'Total':<7}\n"
        receipt_text += "------------------------------------------\n"
        
        g_total = 0.0
        for prod_id, data in self.cart.items():
            receipt_text += f"{data['code']:<8}{data['name'][:20]:<22}{data['qty']:<5}₹{data['total']:0.2f}\n"
            g_total += data['total']
            
        receipt_text += "------------------------------------------\n"
        receipt_text += f"GRAND TOTAL DUE:                 ₹{g_total:.2f}\n"
        receipt_text += "==========================================\n"
        receipt_text += "      Thank You! Support Local Shops!     \n"
        receipt_text += "==========================================\n"
        
        receipt_box.insert("1.0", receipt_text)
        receipt_box.config(state="disabled")
        
        def commit_and_print():
            try:
                conn = self.get_db_connection()
                cursor = conn.cursor()
                
                cursor.execute(
                    "INSERT INTO sales_parent (Payment_Mode, Grand_Total) VALUES (%s, %s)", 
                    (payment_var.get(), g_total)
                )
                invoice_id = cursor.lastrowid
                
                for prod_id, data in self.cart.items():
                    cursor.execute(
                        "INSERT INTO sales_details (Invoice_ID, Product_ID, Quantity, Rate_At_Sale, Total_Price) VALUES (%s, %s, %s, %s, %s)", 
                        (invoice_id, prod_id, data['qty'], data['rate'], data['total'])
                    )
                    
                    cursor.execute(
                        "UPDATE products SET Current_Stock = Current_Stock - %s WHERE Product_ID = %s",
                        (data['qty'], prod_id)
                    )
                    
                conn.commit()
                conn.close()
            except Exception as e:
                messagebox.showerror("Database Error", f"Failed to save sale to database: {e}", parent=preview_win)
                return

            try:
                import win32print
                printer_name = win32print.GetDefaultPrinter()
                hPrinter = win32print.OpenPrinter(printer_name)
                try:
                    hJob = win32print.StartDocPrinter(hPrinter, 1, ("POS Receipt", None, "RAW"))
                    win32print.StartPagePrinter(hPrinter)
                    win32print.WritePrinter(hPrinter, receipt_text.encode('utf-8'))
                    win32print.WritePrinter(hPrinter, b'\n\n\n\n\x1d\x56\x00') 
                    win32print.EndPagePrinter(hPrinter)
                finally:
                    win32print.EndDocPrinter(hPrinter)
                    win32print.ClosePrinter(hPrinter)
                
                messagebox.showinfo("Success", f"Printed, Saved, & Inventory Deducted! (Paid via {payment_var.get()})", parent=preview_win)
                
            except ImportError:
                messagebox.showwarning("Print Error", "pywin32 not installed. Sale & Inventory saved to database, but print was bypassed.", parent=preview_win)
            except Exception as e:
                messagebox.showerror("Printer Error", f"Failed to print: {str(e)}", parent=preview_win)

            self.clear_cart()
            preview_win.destroy()
            self.refresh_product_grid()
            
        ttk.Button(preview_win, text="🖨️ Commit Sale & Deduct Stock", command=commit_and_print).pack(fill="x", side="bottom", padx=20, pady=15)

if __name__ == "__main__":
    root = tk.Tk()
    app = AlagaiPOS(root)
    root.mainloop()
