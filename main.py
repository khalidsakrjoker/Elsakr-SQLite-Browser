
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import pandas as pd
import os
import sys
from PIL import Image, ImageTk

# ... (Colors, PremiumButton, PremiumCard classes stay same) ...


class Colors:
    """Premium dark theme colors."""
    BG_DARK = "#0a0a0f"
    BG_CARD = "#12121a"
    BG_CARD_HOVER = "#1a1a25"
    BG_INPUT = "#1e1e2e"
    
    PRIMARY = "#8b5cf6"  # Purple
    PRIMARY_HOVER = "#a78bfa"
    PRIMARY_DARK = "#7c3aed"
    
    SECONDARY = "#22d3ee"
    SUCCESS = "#10b981"
    WARNING = "#f59e0b"
    ERROR = "#ef4444"
    
    TEXT_PRIMARY = "#ffffff"
    TEXT_SECONDARY = "#a1a1aa"
    TEXT_MUTED = "#71717a"
    
    BORDER = "#27272a"
    BORDER_FOCUS = "#8b5cf6"

class PremiumButton(tk.Canvas):
    """Custom premium button."""
    
    def __init__(self, parent, text, command=None, width=200, height=45, 
                 primary=True, color=None, **kwargs):
        super().__init__(parent, width=width, height=height, 
                        bg=Colors.BG_CARD, highlightthickness=0, **kwargs)
        
        self.command = command
        self.text = text
        self.width = width
        self.height = height
        self.primary = primary
        self.custom_color = color
        self.hovered = False
        self.enabled = True
        
        self.draw_button()
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        
    def draw_button(self):
        self.delete("all")
        
        if not self.enabled:
            bg_color = Colors.BG_INPUT
            text_color = Colors.TEXT_MUTED
        elif self.custom_color:
            bg_color = self.custom_color
            text_color = Colors.TEXT_PRIMARY
        elif self.primary:
            bg_color = Colors.PRIMARY_HOVER if self.hovered else Colors.PRIMARY
            text_color = Colors.TEXT_PRIMARY
        else:
            bg_color = Colors.BG_CARD_HOVER if self.hovered else Colors.BG_INPUT
            text_color = Colors.TEXT_SECONDARY
        
        radius = 10
        self.create_rounded_rect(2, 2, self.width-2, self.height-2, 
                                  radius, fill=bg_color, outline="")
        self.create_text(self.width//2, self.height//2, 
                        text=self.text, fill=text_color,
                        font=("Segoe UI Semibold", 10))
        
    def create_rounded_rect(self, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1+radius, y1, x2-radius, y1, x2, y1, x2, y1+radius,
            x2, y2-radius, x2, y2, x2-radius, y2, x1+radius, y2,
            x1, y2, x1, y2-radius, x1, y1+radius, x1, y1,
        ]
        return self.create_polygon(points, smooth=True, **kwargs)
        
    def on_enter(self, event):
        if self.enabled:
            self.hovered = True
            self.draw_button()
            self.config(cursor="hand2")
        
    def on_leave(self, event):
        self.hovered = False
        self.draw_button()
        
    def on_click(self, event):
        if self.command and self.enabled:
            self.command()
            
    def set_enabled(self, enabled):
        self.enabled = enabled
        self.draw_button()


class PremiumCard(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=Colors.BG_CARD, **kwargs)
        self.config(highlightbackground=Colors.BORDER, highlightthickness=1)


# --- Application Logic ---

class SQLiteBrowserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Elsakr SQLite Browser")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        self.root.configure(bg=Colors.BG_DARK)
        
        self.conn = None
        self.current_db_path = None
        
        self.set_window_icon()
        self.load_logo()
        
        self.setup_theme()
        self.create_layout()

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def set_window_icon(self):
        try:
            icon_path = self.resource_path(os.path.join("assets", "fav.ico"))
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except Exception as e:
            print(f"Icon Error: {e}")

    def load_logo(self):
        self.logo_photo = None
        try:
            logo_path = self.resource_path(os.path.join("assets", "Sakr-logo.png"))
            if os.path.exists(logo_path):
                logo = Image.open(logo_path)
                logo.thumbnail((40, 40), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo)
        except Exception as e:
            print(f"Logo Error: {e}") 

    def setup_theme(self):
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Colors
        style.configure(".", 
            background=Colors.BG_DARK, 
            foreground=Colors.TEXT_PRIMARY, 
            fieldbackground=Colors.BG_INPUT,
            troughcolor=Colors.BG_INPUT,
            borderwidth=0
        )
        
        # Frames
        style.configure("TFrame", background=Colors.BG_DARK)
        style.configure("Card.TFrame", background=Colors.BG_CARD)
        
        # Notebook (Tabs)
        style.configure('TNotebook', background=Colors.BG_DARK, borderwidth=0)
        style.configure('TNotebook.Tab', background=Colors.BG_CARD, 
                       foreground=Colors.TEXT_SECONDARY, padding=[15, 8],
                       font=('Segoe UI', 10))
        style.map('TNotebook.Tab', background=[('selected', Colors.BG_INPUT)],
                 foreground=[('selected', Colors.PRIMARY)])

        # Treeview (Data Grid)
        style.configure("Treeview",
            background=Colors.BG_INPUT,
            foreground=Colors.TEXT_PRIMARY,
            fieldbackground=Colors.BG_INPUT,
            borderwidth=0,
            rowheight=35,
            font=('Segoe UI', 10)
        )
        style.configure("Treeview.Heading",
            background=Colors.BG_CARD,
            foreground=Colors.TEXT_SECONDARY,
            borderwidth=0,
            relief="flat",
            padding=10,
            font=('Segoe UI Semibold', 10)
        )
        style.map("Treeview.Heading",
            background=[("active", Colors.BG_CARD_HOVER)]
        )
        
        # Labels
        style.configure("TLabel", background=Colors.BG_DARK, foreground=Colors.TEXT_PRIMARY)
        style.configure("Card.TLabel", background=Colors.BG_CARD, foreground=Colors.TEXT_PRIMARY)
        style.configure("Header.TLabel", font=("Segoe UI Bold", 24))
        style.configure("SubHeader.TLabel", font=("Segoe UI", 11), foreground=Colors.TEXT_SECONDARY)
        
    def create_layout(self):
        # Top Header
        header = tk.Frame(self.root, bg=Colors.BG_DARK, height=80)
        header.pack(fill="x", padx=20, pady=20)
        
        # Show actual logo image if loaded, otherwise fallback to emoji
        if self.logo_photo:
            logo_img = tk.Label(header, image=self.logo_photo, bg=Colors.BG_DARK)
            logo_img.pack(side="left", padx=(0, 10))
        
        title_lbl = tk.Label(header, text="Elsakr", font=("Segoe UI Bold", 24), bg=Colors.BG_DARK, fg=Colors.TEXT_PRIMARY)
        title_lbl.pack(side="left")
        
        subtitle = tk.Label(header, text="SQLite Browser", font=("Segoe UI", 14), bg=Colors.BG_DARK, fg=Colors.PRIMARY)
        subtitle.pack(side="left", padx=10, pady=(6, 0))
        
        # Main Layout (Sidebar + Content)
        main_container = tk.Frame(self.root, bg=Colors.BG_DARK)
        main_container.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Sidebar
        self.sidebar = PremiumCard(main_container, width=300)
        self.sidebar.pack(side="left", fill="y", padx=(0, 20))
        self.sidebar.pack_propagate(False)
        
        self.setup_sidebar()
        
        # Content Area
        self.content_area = tk.Frame(main_container, bg=Colors.BG_DARK)
        self.content_area.pack(side="right", fill="both", expand=True)
        
        # Tabs
        self.notebook = ttk.Notebook(self.content_area)
        self.notebook.pack(fill="both", expand=True)
        
        # Create Tabs
        self.tab_data = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.tab_query = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        self.tab_structure = tk.Frame(self.notebook, bg=Colors.BG_DARK)
        
        self.notebook.add(self.tab_data, text="  Browse Data  ")
        self.notebook.add(self.tab_query, text="  Execute SQL  ")
        self.notebook.add(self.tab_structure, text="  Structure  ")
        
        self.setup_data_tab()
        self.setup_query_tab()
        self.setup_structure_tab()
        
    def setup_sidebar(self):
        # Sidebar Header
        lbl = tk.Label(self.sidebar, text="Database", font=("Segoe UI Semibold", 12), bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY)
        lbl.pack(pady=20, padx=20, anchor="w")
        
        # Action Buttons
        btn_frame = tk.Frame(self.sidebar, bg=Colors.BG_CARD)
        btn_frame.pack(fill="x", padx=20)
        
        PremiumButton(btn_frame, text="📂 Open DB", command=self.open_database, width=250, height=40, primary=True).pack(pady=5)
        PremiumButton(btn_frame, text="✅ New DB", command=self.create_database, width=250, height=40, primary=False).pack(pady=5)
        
        # Tables List
        tk.Label(self.sidebar, text="Tables", font=("Segoe UI Semibold", 12), bg=Colors.BG_CARD, fg=Colors.TEXT_PRIMARY).pack(pady=(20, 10), padx=20, anchor="w")
        
        table_frame = tk.Frame(self.sidebar, bg=Colors.BG_INPUT)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Scrollbar for tables
        sb = ttk.Scrollbar(table_frame)
        sb.pack(side="right", fill="y")
        
        self.table_list = ttk.Treeview(table_frame, selectmode="browse", show="tree", yscrollcommand=sb.set)
        self.table_list.pack(fill="both", expand=True)
        self.table_list.bind("<<TreeviewSelect>>", self.on_table_select)
        sb.config(command=self.table_list.yview)

    def setup_data_tab(self):
        # Toolbar Card
        toolbar = PremiumCard(self.tab_data, height=80)
        toolbar.pack(fill="x", padx=10, pady=10)
        
        # Left side info
        info_frame = tk.Frame(toolbar, bg=Colors.BG_CARD)
        info_frame.pack(side="left", padx=20, pady=15)
        
        tk.Label(info_frame, text="Current Table:", font=("Segoe UI", 10), bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY).pack(anchor="w")
        self.current_table_label = tk.Label(info_frame, text="None", font=("Segoe UI Bold", 12), bg=Colors.BG_CARD, fg=Colors.PRIMARY)
        self.current_table_label.pack(anchor="w")
        
        # Right side actions
        actions_frame = tk.Frame(toolbar, bg=Colors.BG_CARD)
        actions_frame.pack(side="right", padx=20)
        
        PremiumButton(actions_frame, text="🔄 Refresh", command=self.refresh_data, width=100, height=35, primary=False).pack(side="left", padx=5)
        PremiumButton(actions_frame, text="➕ Add Row", command=self.add_row, width=100, height=35, color=Colors.SUCCESS).pack(side="left", padx=5)
        PremiumButton(actions_frame, text="❌ Delete", command=self.delete_row, width=100, height=35, color=Colors.ERROR).pack(side="left", padx=5)
        PremiumButton(actions_frame, text="⬇️ CSV", command=self.export_csv, width=90, height=35, primary=False).pack(side="left", padx=5)
        PremiumButton(actions_frame, text="⬇️ Excel", command=self.export_excel, width=90, height=35, primary=False).pack(side="left", padx=5)

        # Data Grid Area
        grid_frame = PremiumCard(self.tab_data)
        grid_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.data_tree = ttk.Treeview(grid_frame, show="headings", selectmode="extended")
        
        vsb = ttk.Scrollbar(grid_frame, orient="vertical", command=self.data_tree.yview)
        hsb = ttk.Scrollbar(grid_frame, orient="horizontal", command=self.data_tree.xview)
        self.data_tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.data_tree.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        vsb.pack(side="right", fill="y", pady=2)
        hsb.pack(side="bottom", fill="x", padx=2)

    def setup_query_tab(self):
        # Input Area
        input_card = PremiumCard(self.tab_query, height=200)
        input_card.pack(fill="x", padx=10, pady=10)
        
        tk.Label(input_card, text="SQL Query", font=("Segoe UI Semibold", 11), bg=Colors.BG_CARD, fg=Colors.TEXT_SECONDARY).pack(anchor="w", padx=15, pady=10)
        
        self.query_text = tk.Text(input_card, height=6, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY,
                                insertbackground=Colors.TEXT_PRIMARY, relief="flat", font=("Consolas", 11),
                                highlightbackground=Colors.BORDER, highlightthickness=1)
        self.query_text.pack(fill="x", padx=15, pady=(0, 15))
        
        # Toolbar
        toolbar = tk.Frame(input_card, bg=Colors.BG_CARD)
        toolbar.pack(fill="x", padx=15, pady=(0, 15))
        
        PremiumButton(toolbar, text="▶ Run Query", command=self.run_query, width=120, height=35, color=Colors.SUCCESS).pack(side="left")
        PremiumButton(toolbar, text="🧹 Clear", command=lambda: self.query_text.delete("1.0", tk.END), width=100, height=35, primary=False).pack(side="left", padx=10)
        
        # Results Area
        results_card = PremiumCard(self.tab_query)
        results_card.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        self.query_results = ttk.Treeview(results_card, show="headings")
        sb = ttk.Scrollbar(results_card, orient="vertical", command=self.query_results.yview)
        self.query_results.configure(yscrollcommand=sb.set)
        
        self.query_results.pack(side="left", fill="both", expand=True, padx=2, pady=2)
        sb.pack(side="right", fill="y", pady=2)

    def setup_structure_tab(self):
        # Info Card
        structure_card = PremiumCard(self.tab_structure)
        structure_card.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Two panes: Columns (Left) and Schema (Right)
        paned = tk.PanedWindow(structure_card, orient="horizontal", bg=Colors.BG_CARD, sashwidth=4, sashrelief="flat")
        paned.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Left: Columns
        left_frame = tk.Frame(paned, bg=Colors.BG_CARD)
        tk.Label(left_frame, text="Columns", font=("Segoe UI Semibold", 11), bg=Colors.BG_CARD, fg=Colors.PRIMARY).pack(anchor="w", padx=10, pady=10)
        
        self.structure_tree = ttk.Treeview(left_frame, columns=("cid", "name", "type", "pk"), show="headings")
        self.structure_tree.heading("cid", text="#")
        self.structure_tree.heading("name", text="Name")
        self.structure_tree.heading("type", text="Type")
        self.structure_tree.heading("pk", text="PK")
        self.structure_tree.column("cid", width=40)
        self.structure_tree.column("name", width=150)
        self.structure_tree.column("type", width=80)
        self.structure_tree.column("pk", width=40)
        
        self.structure_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        paned.add(left_frame, minsize=300)
        
        # Right: Schema SQL
        right_frame = tk.Frame(paned, bg=Colors.BG_CARD)
        tk.Label(right_frame, text="Schema Definition", font=("Segoe UI Semibold", 11), bg=Colors.BG_CARD, fg=Colors.PRIMARY).pack(anchor="w", padx=10, pady=10)
        
        self.schema_text = tk.Text(right_frame, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, 
                                 font=("Consolas", 10), highlightthickness=1, highlightbackground=Colors.BORDER, relief="flat")
        self.schema_text.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        paned.add(right_frame, minsize=300)

    # --- Database Logic (Kept mostly same, adjusted for new UI) ---

    def open_database(self):
        file_path = filedialog.askopenfilename(filetypes=[("SQLite Database", "*.db *.sqlite *.sqlite3"), ("All Files", "*.*")])
        if file_path:
            self.connect_db(file_path)

    def create_database(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".db", filetypes=[("SQLite Database", "*.db")])
        if file_path:
            open(file_path, 'a').close()
            self.connect_db(file_path)

    def connect_db(self, path):
        try:
            if self.conn:
                self.conn.close()
            
            self.conn = sqlite3.connect(path)
            self.current_db_path = path
            self.root.title(f"Elsakr SQLite Browser - {os.path.basename(path)}")
            self.load_tables()
            messagebox.showinfo("Success", f"Connected to {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {str(e)}")

    def load_tables(self):
        self.table_list.delete(*self.table_list.get_children())
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            for table in tables:
                self.table_list.insert("", "end", text=table[0], values=(table[0],))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load tables: {str(e)}")

    def on_table_select(self, event):
        selected_item = self.table_list.selection()
        if selected_item:
            table_name = self.table_list.item(selected_item)['text']
            self.load_table_data(table_name)
            self.load_table_structure(table_name)

    def load_table_data(self, table_name):
        self.current_table_label.config(text=table_name)
        try:
            # Clear existing data
            self.data_tree.delete(*self.data_tree.get_children())
            self.data_tree["columns"] = []
            
            # Fetch Data with ROWID
            try:
                self.current_df = pd.read_sql_query(f"SELECT rowid, * FROM '{table_name}' LIMIT 1000", self.conn)
                has_rowid = True
            except:
                self.current_df = pd.read_sql_query(f"SELECT * FROM '{table_name}' LIMIT 1000", self.conn)
                has_rowid = False
            
            columns = list(self.current_df.columns)
            self.data_tree["columns"] = columns
            
            for col in columns:
                self.data_tree.heading(col, text=col)
                width = 50 if (col == "rowid" and has_rowid) else 150
                self.data_tree.column(col, width=width, minwidth=50)
            
            for _, row in self.current_df.iterrows():
                self.data_tree.insert("", "end", values=list(row))
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load table data: {str(e)}")

    def load_table_structure(self, table_name):
        self.structure_tree.delete(*self.structure_tree.get_children())
        self.schema_text.delete("1.0", tk.END)
        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info('{table_name}')")
            columns = cursor.fetchall()
            for col in columns:
                # cid, name, type, notnull, dflt_value, pk
                # We show: cid, name, type, pk
                filtered = (col[0], col[1], col[2], col[5])
                self.structure_tree.insert("", "end", values=filtered)
                
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table_name}'")
            create_sql = cursor.fetchone()
            if create_sql:
                self.schema_text.insert("1.0", create_sql[0])
        except Exception as e:
            self.schema_text.insert("1.0", f"Error: {str(e)}")

    def add_row(self):
        if not hasattr(self, 'current_df') or self.current_df is None:
            messagebox.showwarning("Warning", "No table loaded")
            return
            
        # Dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Add New Row")
        dialog.geometry("500x600")
        dialog.configure(bg=Colors.BG_DARK)
        
        main_frame = tk.Frame(dialog, bg=Colors.BG_DARK)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(main_frame, text=f"Add to: {self.current_table_label.cget('text')}", font=("Segoe UI Bold", 14), bg=Colors.BG_DARK, fg=Colors.PRIMARY).pack(pady=(0, 20))
        
        # Scrollable Frame for inputs
        canvas = tk.Canvas(main_frame, bg=Colors.BG_DARK, highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Colors.BG_DARK)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        entries = {}
        columns = [col for col in self.current_df.columns if col != 'rowid']
        
        for col in columns:
            row_frame = tk.Frame(scrollable_frame, bg=Colors.BG_DARK)
            row_frame.pack(fill="x", pady=5)
            tk.Label(row_frame, text=col, font=("Segoe UI", 10), bg=Colors.BG_DARK, fg=Colors.TEXT_SECONDARY, width=20, anchor="w").pack(side="left")
            entry = tk.Entry(row_frame, bg=Colors.BG_INPUT, fg=Colors.TEXT_PRIMARY, insertbackground=Colors.TEXT_PRIMARY, relief="flat", font=("Segoe UI", 10))
            entry.pack(side="right", fill="x", expand=True, ipady=5, padx=(10, 0))
            entries[col] = entry

        def save():
            try:
                values = [entries[col].get() for col in columns]
                placeholders = ", ".join(["?"] * len(values))
                cols_str = ", ".join([f"'{c}'" for c in columns])
                query = f"INSERT INTO '{self.current_table_label.cget('text')}' ({cols_str}) VALUES ({placeholders})"
                
                cursor = self.conn.cursor()
                cursor.execute(query, values)
                self.conn.commit()
                messagebox.showinfo("Success", "Row added!")
                dialog.destroy()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", str(e))
        
        PremiumButton(main_frame, text="💾 Save Row", command=save, width=200, height=40).pack(pady=20)

    def delete_row(self):
        selected_item = self.data_tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Select a row first")
            return
            
        if not hasattr(self, 'current_df') or "rowid" not in self.current_df.columns:
            messagebox.showwarning("Warning", "Cannot safe delete: No rowid")
            return

        if not messagebox.askyesno("Confirm", "Delete selected row(s)?"):
            return

        try:
            cursor = self.conn.cursor()
            table_name = self.current_table_label.cget("text")
            for item in selected_item:
                vals = self.data_tree.item(item)['values']
                cursor.execute(f"DELETE FROM '{table_name}' WHERE rowid = ?", (vals[0],))
            self.conn.commit()
            messagebox.showinfo("Success", "Deleted successfully")
            self.refresh_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def refresh_data(self):
        selected_item = self.table_list.selection()
        if selected_item:
            self.load_table_data(self.table_list.item(selected_item)['text'])

    def export_csv(self):
        if not hasattr(self, 'current_df') or self.current_df is None: return
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if path: self.current_df.to_csv(path, index=False)

    def export_excel(self):
        if not hasattr(self, 'current_df') or self.current_df is None: return
        path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")])
        if path: self.current_df.to_excel(path, index=False)

    def run_query(self):
        query = self.query_text.get("1.0", tk.END).strip()
        if not query or not self.conn: return
        try:
            df = pd.read_sql_query(query, self.conn)
            self.query_results.delete(*self.query_results.get_children())
            self.query_results["columns"] = list(df.columns)
            for col in df.columns:
                self.query_results.heading(col, text=col)
                self.query_results.column(col, width=150)
            for _, row in df.iterrows():
                self.query_results.insert("", "end", values=list(row))
        except Exception as e:
            messagebox.showerror("SQL Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SQLiteBrowserApp(root)
    root.mainloop()
