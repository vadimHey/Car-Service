import tkinter as tk
from tkinter import ttk, messagebox

class MasterDialog:
    def __init__(self, parent, db, master_id=None):
        self.parent = parent
        self.db = db
        self.master_id = master_id
        self.create_window()
        if master_id:
            self.load_data()
    
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Добавить мастера" if not self.master_id else f"Редактировать мастера №{self.master_id}")
        self.window.geometry("500x450")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Фамилия:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_lastname = ttk.Entry(frame, width=35)
        self.entry_lastname.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Имя:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_firstname = ttk.Entry(frame, width=35)
        self.entry_firstname.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Отчество:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_middlename = ttk.Entry(frame, width=35)
        self.entry_middlename.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Должность (ID):", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_position = ttk.Entry(frame, width=35)
        self.entry_position.grid(row=3, column=1, pady=5, padx=10)
        ttk.Label(frame, text="(1 - мастер, 2 - ст. мастер, 3 - диагностик, 4 - кузовщик)", font=("Arial", 8)).grid(row=4, column=1, sticky="w", padx=10)
        
        ttk.Label(frame, text="Специализация:", font=("Arial", 10)).grid(row=5, column=0, sticky="w", pady=5)
        self.entry_specialization = ttk.Entry(frame, width=35)
        self.entry_specialization.grid(row=5, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Телефон:", font=("Arial", 10)).grid(row=6, column=0, sticky="w", pady=5)
        self.entry_phone = ttk.Entry(frame, width=35)
        self.entry_phone.grid(row=6, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Дата приёма (ГГГГ-ММ-ДД):", font=("Arial", 10)).grid(row=7, column=0, sticky="w", pady=5)
        self.entry_date = ttk.Entry(frame, width=35)
        self.entry_date.grid(row=7, column=1, pady=5, padx=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=8, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)
    
    def load_data(self):
        with self.db.get_cursor() as cur:
            cur.execute("SELECT * FROM master WHERE id_master = %s", (self.master_id,))
            master = cur.fetchone()
            if master:
                self.entry_lastname.insert(0, master['last_name'] or '')
                self.entry_firstname.insert(0, master['first_name'] or '')
                self.entry_middlename.insert(0, master.get('middle_name') or '')
                self.entry_position.insert(0, str(master.get('id_position', '')) if master.get('id_position') else '')
                self.entry_specialization.insert(0, master.get('specialization') or '')
                self.entry_phone.insert(0, master.get('phone') or '')
                self.entry_date.insert(0, str(master.get('hire_date', '')) if master.get('hire_date') else '')
    
    def save(self):
        if not self.entry_lastname.get() or not self.entry_firstname.get() or not self.entry_phone.get() or not self.entry_position.get() or not self.entry_date.get():
            messagebox.showerror("Ошибка", "Фамилия, имя, должность, телефон и дата приема обязательны")
            return
        
        try:
            position_id = int(self.entry_position.get())
            if position_id not in [1, 4]:
                messagebox.showerror("Ошибка", "ID должности должен быть 1-4")
                return
        except ValueError:
            messagebox.showerror("Ошибка", "Введите число (1-4)")
            return
        
        try:
            position_id = int(self.entry_position.get())
        except ValueError:
            messagebox.showerror("Ошибка", "ID должности должен быть числом")
            return
        
        try:
            if self.master_id:
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        UPDATE master SET last_name=%s, first_name=%s, middle_name=%s, 
                               id_position=%s, specialization=%s, phone=%s, hire_date=%s
                        WHERE id_master=%s
                    """, (self.entry_lastname.get(), self.entry_firstname.get(), 
                          self.entry_middlename.get() or None, position_id,
                          self.entry_specialization.get() or None, self.entry_phone.get() or None,
                          self.entry_date.get() or None, self.master_id))
                    self.db.commit()
                messagebox.showinfo("Успех", "Мастер обновлён")
            else:
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        INSERT INTO master (last_name, first_name, middle_name, id_position, 
                                           specialization, phone, hire_date)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (self.entry_lastname.get(), self.entry_firstname.get(), 
                          self.entry_middlename.get() or None, position_id,
                          self.entry_specialization.get() or None, self.entry_phone.get() or None,
                          self.entry_date.get() or None))
                    self.db.commit()
                messagebox.showinfo("Успех", "Мастер добавлен")
            self.window.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", str(e))