import tkinter as tk
from tkinter import ttk, messagebox

class ClientDialog:
    """Диалоговое окно для управления клиентами"""
    
    def __init__(self, parent, db, client_id=None):
        self.parent = parent
        self.db = db
        self.client_id = client_id
        self.create_window()
        if client_id:
            self.load_client_data()
    
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Добавить клиента" if not self.client_id else f"Редактировать клиента №{self.client_id}")
        self.window.geometry("400x350")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Фамилия:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.entry_lastname = ttk.Entry(frame, width=30)
        self.entry_lastname.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Имя:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_firstname = ttk.Entry(frame, width=30)
        self.entry_firstname.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Отчество:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_middlename = ttk.Entry(frame, width=30)
        self.entry_middlename.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Телефон:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_phone = ttk.Entry(frame, width=30)
        self.entry_phone.grid(row=3, column=1, pady=5, padx=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)
    
    def load_client_data(self):
        client = self.db.get_client_by_id(self.client_id)
        if client:
            self.entry_lastname.insert(0, client['last_name'] or '')
            self.entry_firstname.insert(0, client['first_name'] or '')
            self.entry_middlename.insert(0, client.get('middle_name') or '')
            self.entry_phone.insert(0, client.get('phone') or '')
    
    def save(self):
        lastname = self.entry_lastname.get().strip()
        firstname = self.entry_firstname.get().strip()
        phone = self.entry_phone.get().strip()
        
        if not lastname or not firstname or not phone:
            messagebox.showerror("Ошибка", "Фамилия, имя и телефон обязательны")
            return
        
        try:
            if self.client_id:
                # Обновление
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        UPDATE client 
                        SET last_name=%s, first_name=%s, middle_name=%s, phone=%s
                        WHERE id_client=%s
                    """, (lastname, firstname, self.entry_middlename.get() or None, 
                          self.entry_phone.get() or None, self.client_id))
                    self.db.commit()
                messagebox.showinfo("Успех", "Клиент обновлён")
            else:
                # Создание
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        INSERT INTO client (last_name, first_name, middle_name, phone)
                        VALUES (%s, %s, %s, %s)
                    """, (lastname, firstname, self.entry_middlename.get() or None,
                          self.entry_phone.get() or None))
                    self.db.commit()
                messagebox.showinfo("Успех", "Клиент добавлен")
            
            self.window.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", str(e))