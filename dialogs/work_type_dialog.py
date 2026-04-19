import tkinter as tk
from tkinter import ttk, messagebox

class WorkTypeDialog:
    def __init__(self, parent, db, work_id=None):
        self.parent = parent
        self.db = db
        self.work_id = work_id
        self.create_window()
        if work_id:
            self.load_data()
    
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Добавить вид работы" if not self.work_id else f"Редактировать вид работы №{self.work_id}")
        self.window.geometry("400x300")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Наименование:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_name = ttk.Entry(frame, width=35)
        self.entry_name.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Трудоёмкость (часы):", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_hours = ttk.Entry(frame, width=35)
        self.entry_hours.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Стоимость (руб):", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_cost = ttk.Entry(frame, width=35)
        self.entry_cost.grid(row=2, column=1, pady=5, padx=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)
    
    def load_data(self):
        with self.db.get_cursor() as cur:
            cur.execute("SELECT * FROM work_type WHERE id_work_type = %s", (self.work_id,))
            work = cur.fetchone()
            if work:
                self.entry_name.insert(0, work['name'] or '')
                self.entry_hours.insert(0, str(work.get('labor_hours', '')) if work.get('labor_hours') else '')
                self.entry_cost.insert(0, str(work.get('cost', '')) if work.get('cost') else '')
    
    def save(self):
        if not self.entry_name.get():
            messagebox.showerror("Ошибка", "Введите наименование")
            return
        
        try:
            hours = float(self.entry_hours.get()) if self.entry_hours.get() else None
            price = float(self.entry_cost.get()) if self.entry_cost.get() else None
        except ValueError:
            messagebox.showerror("Ошибка", "Трудоёмкость и стоимость должны быть числами")
            return
        
        try:
            if self.work_id:
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        UPDATE work_type SET name=%s, labor_hours=%s, price=%s
                        WHERE id_work_type=%s
                    """, (self.entry_name.get(), hours, price, self.work_id))
                    self.db.commit()
                messagebox.showinfo("Успех", "Вид работы обновлён")
            else:
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        INSERT INTO work_type (name, labor_hours, price)
                        VALUES (%s, %s, %s)
                    """, (self.entry_name.get(), hours, price))
                    self.db.commit()
                messagebox.showinfo("Успех", "Вид работы добавлен")
            self.window.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", str(e))