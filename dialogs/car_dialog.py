import tkinter as tk
from tkinter import ttk, messagebox

class CarDialog:
    def __init__(self, parent, db, car_id=None):
        self.parent = parent
        self.db = db
        self.car_id = car_id
        self.create_window()
        if car_id:
            self.load_data()
    
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        self.window.title("Добавить автомобиль" if not self.car_id else f"Редактировать автомобиль №{self.car_id}")
        self.window.geometry("450x400")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        frame = ttk.Frame(self.window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Выбор клиента
        ttk.Label(frame, text="Владелец:", font=("Arial", 10)).grid(row=0, column=0, sticky="w", pady=5)
        self.client_combo = ttk.Combobox(frame, width=35, state="readonly")
        self.client_combo.grid(row=0, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Марка:", font=("Arial", 10)).grid(row=1, column=0, sticky="w", pady=5)
        self.entry_brand = ttk.Entry(frame, width=35)
        self.entry_brand.grid(row=1, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Модель:", font=("Arial", 10)).grid(row=2, column=0, sticky="w", pady=5)
        self.entry_model = ttk.Entry(frame, width=35)
        self.entry_model.grid(row=2, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Госномер:", font=("Arial", 10)).grid(row=3, column=0, sticky="w", pady=5)
        self.entry_plate = ttk.Entry(frame, width=35)
        self.entry_plate.grid(row=3, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="Год выпуска:", font=("Arial", 10)).grid(row=4, column=0, sticky="w", pady=5)
        self.entry_year = ttk.Entry(frame, width=35)
        self.entry_year.grid(row=4, column=1, pady=5, padx=10)
        
        ttk.Label(frame, text="VIN:", font=("Arial", 10)).grid(row=5, column=0, sticky="w", pady=5)
        self.entry_vin = ttk.Entry(frame, width=35)
        self.entry_vin.grid(row=5, column=1, pady=5, padx=10)
        
        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)
        
        ttk.Button(btn_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=10)
        ttk.Button(btn_frame, text="Отмена", command=self.window.destroy).pack(side=tk.LEFT, padx=10)
        
        self.load_clients()
    
    def load_clients(self):
        clients = self.db.get_clients_for_combo()
        self.clients_data = {}
        client_list = []
        for c in clients:
            display = f"{c['full_name']} (ID:{c['id_client']})"
            self.clients_data[display] = c['id_client']
            client_list.append(display)
        self.client_combo['values'] = client_list
        if client_list:
            self.client_combo.current(0)
    
    def load_data(self):
        with self.db.get_cursor() as cur:
            cur.execute("SELECT * FROM car WHERE id_car = %s", (self.car_id,))
            car = cur.fetchone()
            if car:
                self.entry_brand.insert(0, car['brand'] or '')
                self.entry_model.insert(0, car['model'] or '')
                self.entry_plate.insert(0, car['plate_number'] or '')
                self.entry_year.insert(0, str(car.get('year', '')) if car.get('year') else '')
                self.entry_vin.insert(0, car.get('vin') or '')
                
                # Выбираем клиента в комбобоксе
                for display, cid in self.clients_data.items():
                    if cid == car['id_client']:
                        self.client_combo.set(display)
                        break
    
    def save(self):
        if not self.client_combo.get():
            messagebox.showerror("Ошибка", "Выберите владельца")
            return
        if not self.entry_brand.get() or not self.entry_model.get() or not self.entry_plate.get():
            messagebox.showerror("Ошибка", "Марка, модель и госномер обязательны")
            return
        
        client_id = self.clients_data[self.client_combo.get()]
        brand = self.entry_brand.get()
        model = self.entry_model.get()
        plate = self.entry_plate.get()
        year = self.entry_year.get() or None
        vin = self.entry_vin.get() or None
        
        try:
            if self.car_id:
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        UPDATE car SET brand=%s, model=%s, plate_number=%s, year=%s, vin=%s, id_client=%s
                        WHERE id_car=%s
                    """, (brand, model, plate, year, vin, client_id, self.car_id))
                    self.db.commit()
                messagebox.showinfo("Успех", "Автомобиль обновлён")
            else:
                with self.db.get_cursor() as cur:
                    cur.execute("""
                        INSERT INTO car (brand, model, plate_number, year, vin, id_client)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (brand, model, plate, year, vin, client_id))
                    self.db.commit()
                messagebox.showinfo("Успех", "Автомобиль добавлен")
            self.window.destroy()
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", str(e))