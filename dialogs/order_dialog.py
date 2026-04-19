import tkinter as tk
from tkinter import ttk, messagebox

class OrderDialog:
    def __init__(self, parent, db, order_id=None):
        self.parent = parent
        self.db = db
        self.order_id = order_id
        self.create_window()
        if order_id:
            self.load_order_data()
    
    def create_window(self):
        self.window = tk.Toplevel(self.parent)
        if self.order_id:
            self.window.title(f"Редактирование заказа №{self.order_id}")
        else:
            self.window.title("Создание нового заказа")
        self.window.geometry("800x700")
        self.window.transient(self.parent)
        self.window.grab_set()
        
        # Основной фрейм
        main_frame = ttk.Frame(self.window, padding=10)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # ===== Клиент и автомобиль =====
        client_frame = ttk.LabelFrame(main_frame, text="Клиент и автомобиль", padding=10)
        client_frame.pack(fill=tk.X, pady=5)
        
        # Выбор клиента
        ttk.Label(client_frame, text="Клиент:").grid(row=0, column=0, sticky="w", pady=5)
        self.client_combo = ttk.Combobox(client_frame, width=50, state="readonly")
        self.client_combo.grid(row=0, column=1, pady=5, padx=10)
        self.client_combo.bind("<<ComboboxSelected>>", self.on_client_selected)
        
        # Выбор автомобиля
        ttk.Label(client_frame, text="Автомобиль:").grid(row=1, column=0, sticky="w", pady=5)
        self.car_combo = ttk.Combobox(client_frame, width=50, state="readonly")
        self.car_combo.grid(row=1, column=1, pady=5, padx=10)
        
        # Статус (только для редактирования)
        if self.order_id:
            ttk.Label(client_frame, text="Статус:").grid(row=2, column=0, sticky="w", pady=5)
            self.status_combo = ttk.Combobox(client_frame, 
                values=["принят", "в работе", "выполнен", "закрыт"], 
                width=20, state="readonly")
            self.status_combo.grid(row=2, column=1, pady=5, padx=10, sticky="w")
        
        # ===== Виды работ =====
        works_frame = ttk.LabelFrame(main_frame, text="Виды работ", padding=10)
        works_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Верхняя панель добавления работ
        add_work_frame = ttk.Frame(works_frame)
        add_work_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_work_frame, text="Работа:").pack(side=tk.LEFT, padx=5)
        self.work_combo = ttk.Combobox(add_work_frame, width=40, state="readonly")
        self.work_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_work_frame, text="Кол-во:").pack(side=tk.LEFT, padx=5)
        self.work_quantity = ttk.Entry(add_work_frame, width=10)
        self.work_quantity.insert(0, "1")
        self.work_quantity.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_work_frame, text="➕ Добавить работу", command=self.add_work).pack(side=tk.LEFT, padx=10)
        
        # Таблица работ
        self.works_tree = ttk.Treeview(works_frame, columns=("name", "quantity", "price", "total"), show="headings", height=2)
        self.works_tree.heading("name", text="Наименование работы")
        self.works_tree.heading("quantity", text="Кол-во")
        self.works_tree.heading("price", text="Цена, руб")
        self.works_tree.heading("total", text="Сумма, руб")
        
        self.works_tree.column("name", width=300)
        self.works_tree.column("quantity", width=80)
        self.works_tree.column("price", width=100)
        self.works_tree.column("total", width=100)
        
        self.works_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(works_frame, text="🗑 Удалить выбранную работу", command=self.remove_work).pack(pady=2)
        
        # ===== Материалы =====
        materials_frame = ttk.LabelFrame(main_frame, text="Расходные материалы", padding=10)
        materials_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Верхняя панель добавления материалов
        add_material_frame = ttk.Frame(materials_frame)
        add_material_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(add_material_frame, text="Материал:").pack(side=tk.LEFT, padx=5)
        self.material_combo = ttk.Combobox(add_material_frame, width=40, state="readonly")
        self.material_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(add_material_frame, text="Кол-во:").pack(side=tk.LEFT, padx=5)
        self.material_quantity = ttk.Entry(add_material_frame, width=10)
        self.material_quantity.insert(0, "1")
        self.material_quantity.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(add_material_frame, text="➕ Добавить материал", command=self.add_material).pack(side=tk.LEFT, padx=10)
        
        # Таблица материалов
        self.materials_tree = ttk.Treeview(materials_frame, columns=("name", "quantity", "price", "total"), show="headings", height=2)
        self.materials_tree.heading("name", text="Наименование материала")
        self.materials_tree.heading("quantity", text="Кол-во")
        self.materials_tree.heading("price", text="Цена, руб")
        self.materials_tree.heading("total", text="Сумма, руб")
        
        self.materials_tree.column("name", width=300)
        self.materials_tree.column("quantity", width=80)
        self.materials_tree.column("price", width=100)
        self.materials_tree.column("total", width=100)
        
        self.materials_tree.pack(fill=tk.BOTH, expand=True, pady=5)
        
        ttk.Button(materials_frame, text="🗑 Удалить выбранный материал", command=self.remove_material).pack(pady=2)
        
        # ===== Мастера =====
        masters_frame = ttk.LabelFrame(main_frame, text="Мастера", padding=10)
        masters_frame.pack(fill=tk.X, pady=5)
        
        # Список мастеров с множественным выбором
        masters_list_frame = ttk.Frame(masters_frame)
        masters_list_frame.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(masters_list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.masters_listbox = tk.Listbox(masters_list_frame, selectmode=tk.MULTIPLE, 
                                           yscrollcommand=scrollbar.set, height=2)
        self.masters_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.masters_listbox.yview)
        
        # ===== Кнопки =====
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(btn_frame, text="💾 Сохранить", command=self.save_order).pack(side=tk.RIGHT, padx=5)
        ttk.Button(btn_frame, text="❌ Отмена", command=self.window.destroy).pack(side=tk.RIGHT, padx=5)
        
        # Загрузка данных
        self.load_clients()
        self.load_work_types()
        self.load_materials()
        self.load_masters()
        
        self.work_items = []
        self.material_items = []
    
    def load_clients(self):
        clients = self.db.get_clients_for_combo()
        self.clients_data = {}
        client_list = []
        for c in clients:
            display = f"{c['full_name']} (тел: {c.get('phone', '')})"
            self.clients_data[display] = c['id_client']
            client_list.append(display)
        self.client_combo['values'] = client_list
        if client_list:
            self.client_combo.current(0)
            self.on_client_selected()
    
    def on_client_selected(self, event=None):
        selected = self.client_combo.get()
        if selected:
            client_id = self.clients_data[selected]
            cars = self.db.get_cars_by_client(client_id)
            self.cars_data = {}
            car_list = []
            for c in cars:
                display = f"{c['car_info']}"
                self.cars_data[display] = c['id_car']
                car_list.append(display)
            self.car_combo['values'] = car_list
            if car_list:
                self.car_combo.current(0)
    
    def load_work_types(self):
        works = self.db.get_work_types_for_combo()
        self.works_data = {}
        work_list = []
        for w in works:
            price = float(w['price']) if w['price'] else 0
            hours = float(w['labor_hours']) if w['labor_hours'] else 0
            display = f"{w['name']} - {price} руб. ({hours} ч.)"
            self.works_data[display] = {
                'id_work_type': w['id_work_type'],
                'name': w['name'],
                'price': price,
                'labor_hours': hours
            }
            work_list.append(display)
        self.work_combo['values'] = work_list
        if work_list:
            self.work_combo.current(0)
    
    def load_materials(self):
        materials = self.db.get_materials_for_combo()
        self.materials_data = {}
        material_list = []
        for m in materials:
            sale_price = float(m['sale_price']) if m['sale_price'] else 0
            stock = float(m['stock_balance']) if m['stock_balance'] else 0
            display = f"{m['name']} - {sale_price} руб. (остаток: {stock})"
            self.materials_data[display] = {
                'id_material': m['id_material'],
                'name': m['name'],
                'sale_price': sale_price,
                'stock_balance': stock
            }
            material_list.append(display)
        self.material_combo['values'] = material_list
        if material_list:
            self.material_combo.current(0)
    
    def load_masters(self):
        masters = self.db.get_masters_for_combo()
        self.masters_data = {}
        for m in masters:
            display = f"{m['full_name']} (ID:{m['id_master']})"
            self.masters_data[display] = m['id_master']
            self.masters_listbox.insert(tk.END, display)
    
    def add_work(self):
        selected = self.work_combo.get()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите вид работы")
            return
        
        try:
            quantity = float(self.work_quantity.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество")
            return
        
        work = self.works_data[selected]
        # Преобразуем Decimal в float
        price = float(work['price']) if work['price'] else 0
        total = quantity * price
        
        self.work_items.append({
            'work_type_id': work['id_work_type'],
            'name': work['name'],
            'quantity': quantity,
            'price': price,
            'total': total
        })
        
        self.works_tree.insert("", tk.END, values=(work['name'], quantity, price, total))
        self.work_quantity.delete(0, tk.END)
        self.work_quantity.insert(0, "1")
    
    def remove_work(self):
        selection = self.works_tree.selection()
        if selection:
            index = self.works_tree.index(selection[0])
            self.works_tree.delete(selection[0])
            del self.work_items[index]
    
    def add_material(self):
        selected = self.material_combo.get()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите материал")
            return
        
        try:
            quantity = float(self.material_quantity.get())
            if quantity <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректное количество")
            return
        
        material = self.materials_data[selected]
        # Преобразуем Decimal в float
        price = float(material['sale_price']) if material['sale_price'] else 0
        total = quantity * price
        
        self.material_items.append({
            'material_id': material['id_material'],
            'name': material['name'],
            'quantity': quantity,
            'price': price,
            'total': total
        })
        
        self.materials_tree.insert("", tk.END, values=(material['name'], quantity, price, total))
        self.material_quantity.delete(0, tk.END)
        self.material_quantity.insert(0, "1")
    
    def remove_material(self):
        selection = self.materials_tree.selection()
        if selection:
            index = self.materials_tree.index(selection[0])
            self.materials_tree.delete(selection[0])
            del self.material_items[index]
    
    def load_order_data(self):
        """Загрузка данных заказа для редактирования"""
        # Получаем информацию о заказе
        order = self.db.get_order_summary(self.order_id)
        if order:
            # Выбираем клиента
            for display, cid in self.clients_data.items():
                if cid == order['id_client']:
                    self.client_combo.set(display)
                    break
            
            # Загружаем автомобили клиента и выбираем нужный
            self.on_client_selected()
            for display, cid in self.cars_data.items():
                if cid == order['id_car']:
                    self.car_combo.set(display)
                    break
            
            # Устанавливаем статус
            if hasattr(self, 'status_combo'):
                self.status_combo.set(order['status'])
        
        # Загружаем работы
        works = self.db.get_order_works_with_names(self.order_id)
        for w in works:
            price = float(w['price_at_moment']) if w['price_at_moment'] else 0
            quantity = float(w['quantity']) if w['quantity'] else 0
            self.work_items.append({
                'order_work_id': w.get('id_order_work'),
                'work_type_id': w['id_work_type'],
                'name': w['name'],
                'quantity': quantity,
                'price': price,
                'total': quantity * price
            })
            self.works_tree.insert("", tk.END, values=(w['name'], quantity, price, quantity * price))
        
        # Загружаем материалы
        materials = self.db.get_order_materials_with_names(self.order_id)
        for m in materials:
            price = float(m['price_at_moment']) if m['price_at_moment'] else 0
            quantity = float(m['quantity']) if m['quantity'] else 0
            self.material_items.append({
                'order_material_id': m.get('id_order_material'),
                'material_id': m['id_material'],
                'name': m['name'],
                'quantity': quantity,
                'price': price,
                'total': quantity * price
            })
            self.materials_tree.insert("", tk.END, values=(m['name'], quantity, price, quantity * price))
        
        # Загружаем мастеров
        masters = self.db.get_order_masters(self.order_id)
        master_ids = [m['id_master'] for m in masters]
        for i in range(self.masters_listbox.size()):
            master_name = self.masters_listbox.get(i)
            master_id = self.masters_data[master_name]
            if master_id in master_ids:
                self.masters_listbox.selection_set(i)
    
    def save_order(self):
        """Сохранение заказа"""
        # Проверка заполнения
        if not self.client_combo.get():
            messagebox.showerror("Ошибка", "Выберите клиента")
            return
        
        if not self.car_combo.get():
            messagebox.showerror("Ошибка", "Выберите автомобиль")
            return
        
        client_id = self.clients_data[self.client_combo.get()]
        car_id = self.cars_data[self.car_combo.get()]
        
        # Получаем выбранных мастеров
        selected_indices = self.masters_listbox.curselection()
        master_ids = []
        for idx in selected_indices:
            master_name = self.masters_listbox.get(idx)
            master_ids.append(self.masters_data[master_name])
        
        if not master_ids:
            messagebox.showerror("Ошибка", "Выберите хотя бы одного мастера")
            return
        
        try:
            if self.order_id:
                # === РЕДАКТИРОВАНИЕ (только статус) ===
                status = self.status_combo.get() if hasattr(self, 'status_combo') else "принят"
                self.db.update_order_status(self.order_id, status)
                messagebox.showinfo("Успех", f"Статус заказа №{self.order_id} изменён на '{status}'")
                
            else:
                # === СОЗДАНИЕ НОВОГО ЗАКАЗА ===
                # Проверяем, что добавлены работы или материалы
                if not self.work_items and not self.material_items:
                    if not messagebox.askyesno("Вопрос", "Заказ не содержит работ и материалов. Продолжить?"):
                        return
                
                # Подготавливаем работы
                work_items = []
                for w in self.work_items:
                    work_items.append({
                        'work_type_id': w['work_type_id'],
                        'quantity': float(w['quantity']),
                        'price': float(w['price'])
                    })
                
                # Подготавливаем материалы
                material_items = []
                for m in self.material_items:
                    material_items.append({
                        'material_id': m['material_id'],
                        'quantity': float(m['quantity']),
                        'price': float(m['price'])
                    })
                
                # Создаём заказ
                order_id = self.db.create_full_order(client_id, car_id, master_ids, work_items, material_items)
                messagebox.showinfo("Успех", f"Заказ №{order_id} успешно создан")
            
            self.window.destroy()
            
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", str(e))