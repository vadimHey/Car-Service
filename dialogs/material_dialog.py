import tkinter as tk
from tkinter import ttk, messagebox

class MaterialDialog:
    def __init__(self, parent, db, material_id=None):
        self.parent = parent
        self.db = db
        self.material_id = material_id
        self.create_window()
        if material_id:
            self.load_data()
    
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Добавить материал" if not self.material_id else f"Редактировать материал №{self.material_id}")
        self.window.geometry("500x450")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Наименование:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = ttk.Entry(frame, width=35)
        self.entry_name.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Единица измерения:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_unit = ttk.Entry(frame, width=35)
        self.entry_unit.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Склад (ID):", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_storage = ttk.Entry(frame, width=35)
        self.entry_storage.grid(row=2, column=1, pady=5, padx=10)
        ttk.Label(frame, text="(1 - основной, 2 - резервный)", font=("Arial", 8)).grid(row=3, column=1, sticky="w", padx=10)
        
        ttk.Label(frame, text="Остаток на складе:", font=("Arial", 10)).grid(row=4, column=0, sticky="w", pady=5)
        self.entry_stock = ttk.Entry(frame, width=35)
        self.entry_stock.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Закупочная цена (руб):", font=("Arial", 10)).grid(row=5, column=0, sticky="w", pady=5)
        self.entry_purchase = ttk.Entry(frame, width=35)
        self.entry_purchase.grid(row=5, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Продажная цена (руб):", font=("Arial", 10)).grid(row=6, column=0, sticky="w", pady=5)
        self.entry_sale = ttk.Entry(frame, width=35)
        self.entry_sale.grid(row=6, column=1, pady=5, padx=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=7, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)
        
        # Подсказка
        ttk.Label(frame, text="Подсказка: ID склада можно узнать из таблицы storage", 
                  font=("Arial", 8), foreground="gray").grid(row=8, column=0, columnspan=2, pady=5)
    
    def load_data(self):
        with self.db.get_cursor() as cur:
            cur.execute("SELECT * FROM material WHERE id_material = %s", (self.material_id,))
            material = cur.fetchone()
            if material:
                self.entry_name.insert(0, material['name'] or '')
                self.entry_unit.insert(0, material.get('unit') or '')
                self.entry_storage.insert(0, str(material.get('id_storage', '')) if material.get('id_storage') else '')
                self.entry_stock.insert(0, str(material.get('stock_balance', '')) if material.get('stock_balance') is not None else '0')
                self.entry_purchase.insert(0, str(material.get('purchase_price', '')) if material.get('purchase_price') is not None else '0')
                self.entry_sale.insert(0, str(material.get('sale_price', '')) if material.get('sale_price') is not None else '0')
    
    def save(self):
        if not self.entry_name.get() or not self.entry_unit.get() or not self.entry_storage.get():
            messagebox.showerror("Ошибка", "Введите наименование, количество и ID склада")
            return
        
        try:
            storage_id = int(self.entry_storage.get())
            if storage_id not in [1, 2]:
                messagebox.showerror("Ошибка", "ID склада должен быть 1 или 2")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число (1 или 2)")
            return
        
        try:
            storage_id = int(self.entry_storage.get())
            stock = float(self.entry_stock.get()) if self.entry_stock.get() else 0
            purchase = float(self.entry_purchase.get()) if self.entry_purchase.get() else 0
            sale = float(self.entry_sale.get()) if self.entry_sale.get() else 0
        except ValueError:
            messagebox.showerror("Ошибка", "ID склада, цены и остаток должны быть числами")
            return
        
        try:
            if self.material_id:
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        UPDATE material SET name=%s, unit=%s, id_storage=%s, stock_balance=%s, 
                               purchase_price=%s, sale_price=%s
                        WHERE id_material=%s
                    """, (self.entry_name.get(), self.entry_unit.get() or None, 
                          storage_id, stock, purchase, sale, self.material_id))
                    self.db.commit()
                messagebox.showinfo("Успех", "Материал обновлён")
            else:
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        INSERT INTO material (name, unit, id_storage, stock_balance, purchase_price, sale_price)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (self.entry_name.get(), self.entry_unit.get() or None, 
                          storage_id, stock, purchase, sale))
                    self.db.commit()
                messagebox.showinfo("Успех", "Материал добавлен")
            self.window.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", str(e))