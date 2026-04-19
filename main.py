import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class CarServiceApp:
    """Главное приложение автосервиса"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Автосервис - система управления заказами")
        self.root.geometry("1200x600")
        
        # Подключение к БД
        self.db = Database()
        
        # Создание интерфейса
        self.create_menu()
        self.create_notebook()
        self.create_statusbar()
        
        # Загрузка данных в активную вкладку
        self.refresh_orders_tab()
    
    def create_menu(self):
        """Создание главного меню"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
    
    def create_notebook(self):
        """Создание вкладок"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="📋 Заказы")
        self.create_orders_tab()
        
        self.materials_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.materials_frame, text="📦 Склад")
        self.create_materials_tab()
        
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="📊 Аналитика")
        self.create_reports_tab()
        
        self.refs_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.refs_frame, text="📚 Справочники")
        self.create_references_tab()
    
    def create_orders_tab(self):
        """Вкладка управления заказами"""
        # Верхняя панель с кнопками
        top_frame = ttk.Frame(self.orders_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(top_frame, text="➕ Новый заказ", command=self.new_order_window).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="✏️ Редактировать", command=self.edit_order).pack(side=tk.LEFT, padx=2)
        ttk.Button(top_frame, text="❌ Удалить заказ", command=self.delete_order).pack(side=tk.LEFT, padx=2)

        # Фильтр по статусу
        ttk.Label(top_frame, text="Фильтр:").pack(side=tk.LEFT, padx=(20, 5))
        self.status_filter = ttk.Combobox(top_frame, values=["все", "принят", "в работе", "выполнен", "закрыт"], width=15)
        self.status_filter.set("все")
        self.status_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_orders_tab())
        self.status_filter.pack(side=tk.LEFT, padx=2)
        
        # Таблица заказов
        columns = ("id", "client", "car", "accept_date", "completion_date", "status", "total_cost")
        self.orders_tree = ttk.Treeview(self.orders_frame, columns=columns, show="headings", height=8)
        
        self.orders_tree.heading("id", text="№ заказа")
        self.orders_tree.heading("client", text="Клиент")
        self.orders_tree.heading("car", text="Автомобиль")
        self.orders_tree.heading("accept_date", text="Дата приёма")
        self.orders_tree.heading("completion_date", text="Дата выполнения")
        self.orders_tree.heading("status", text="Статус")
        self.orders_tree.heading("total_cost", text="Стоимость, руб")
        
        self.orders_tree.column("id", width=70)
        self.orders_tree.column("client", width=200)
        self.orders_tree.column("car", width=150)
        self.orders_tree.column("accept_date", width=100)
        self.orders_tree.column("completion_date", width=100)
        self.orders_tree.column("status", width=100)
        self.orders_tree.column("total_cost", width=100)
        
        v_scroll = ttk.Scrollbar(self.orders_frame, orient=tk.VERTICAL, command=self.orders_tree.yview)
        h_scroll = ttk.Scrollbar(self.orders_frame, orient=tk.HORIZONTAL, command=self.orders_tree.xview)
        self.orders_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.orders_tree.bind("<Double-1>", lambda e: self.view_order_details())
    
    def create_materials_tab(self):
        """Вкладка складского учёта"""
        top_frame = ttk.Frame(self.materials_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        columns = ("id", "name", "unit", "stock", "purchase_price", "sale_price", "markup", "markup_percent", 
                   "stock_cost_purchase", "stock_cost_sale", "last_supply")
        self.materials_tree = ttk.Treeview(self.materials_frame, columns=columns, show="headings", height=8)
        
        self.materials_tree.heading("id", text="ID")
        self.materials_tree.heading("name", text="Наименование")
        self.materials_tree.heading("unit", text="Ед.изм.")
        self.materials_tree.heading("stock", text="Остаток")
        self.materials_tree.heading("purchase_price", text="Закупка, руб")
        self.materials_tree.heading("sale_price", text="Продажа, руб")
        self.materials_tree.heading("markup", text="Наценка, руб")
        self.materials_tree.heading("markup_percent", text="Наценка, %")
        self.materials_tree.heading("stock_cost_purchase", text="Остатки закупок, руб")
        self.materials_tree.heading("stock_cost_sale", text="Остатки продажи, руб")
        self.materials_tree.heading("last_supply", text="Дата посл. поставки")
        
        self.materials_tree.column("id", width=50)
        self.materials_tree.column("name", width=200)
        self.materials_tree.column("unit", width=70)
        self.materials_tree.column("stock", width=70)
        self.materials_tree.column("purchase_price", width=90)
        self.materials_tree.column("sale_price", width=100)
        self.materials_tree.column("markup", width=85)
        self.materials_tree.column("markup_percent", width=90)
        self.materials_tree.column("stock_cost_purchase", width=140)
        self.materials_tree.column("stock_cost_sale", width=140)
        self.materials_tree.column("last_supply", width=120)
        
        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def update_order_total_proc(self):
        """Вызов процедуры update_order_total"""
        try:
            order_id = int(self.update_order_id.get())
            
            if order_id <= 0:
                messagebox.showerror("Ошибка", "ID заказа должен быть положительным числом")
                return
            
            # Получаем старую стоимость
            old_order = self.db.get_order_by_id(order_id)
            
            if old_order is None:
                self.update_result.config(text=f"❌ Заказ №{order_id} не найден")
                return
            
            old_total = old_order['total_cost']
            
            # Вызываем процедуру
            self.db.update_order_total(order_id)
            
            # Получаем новую стоимость
            new_order = self.db.get_order_by_id(order_id)
            new_total = new_order['total_cost']
            
            self.update_result.config(
                text=f"🔄 Заказ №{order_id}: стоимость обновлена с {old_total} руб. на {new_total} руб."
            )
            self.statusbar.config(text=f"Процедура обновления выполнена для заказа {order_id}")
            
            # Обновляем таблицы
            self.refresh_orders_tab()
            self.refresh_order_full_info()
            
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный ID заказа")
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Ошибка БД", f"Ошибка выполнения процедуры: {e}")
    
    def create_reports_tab(self):
        """Вкладка аналитики - функции и процедура"""
        # Функция 1: Расчёт со скидкой
        frame1 = ttk.LabelFrame(self.reports_frame, text="1. Функция: Расчёт стоимости со скидкой", padding=5)
        frame1.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(frame1, text="ID заказа:").grid(row=0, column=0, padx=5, pady=5)
        self.discount_order_id = ttk.Entry(frame1, width=10)
        self.discount_order_id.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(frame1, text="Скидка (%):").grid(row=0, column=2, padx=5, pady=5)
        self.discount_percent = ttk.Entry(frame1, width=10)
        self.discount_percent.grid(row=0, column=3, padx=5, pady=5)
        self.discount_percent.insert(0, "10")
        
        ttk.Button(frame1, text="Рассчитать", command=self.calc_discount).grid(row=0, column=4, padx=10, pady=5)
        self.discount_result = ttk.Label(frame1, text="Результат: ", font=("Arial", 10, "bold"))
        self.discount_result.grid(row=1, column=0, columnspan=5, padx=5, pady=5, sticky="w")
        
        # Функция 2: Рентабельность
        frame2 = ttk.LabelFrame(self.reports_frame, text="2. Функция: Расчёт рентабельности заказа", padding=5)
        frame2.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(frame2, text="ID заказа:").grid(row=0, column=0, padx=5, pady=5)
        self.profit_order_id = ttk.Entry(frame2, width=10)
        self.profit_order_id.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame2, text="Рассчитать рентабельность", command=self.calc_profitability).grid(row=0, column=2, padx=10, pady=5)
        self.profit_result = ttk.Label(frame2, text="Результат: ", font=("Arial", 10))
        self.profit_result.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        
        # Процедура
        frame3 = ttk.LabelFrame(self.reports_frame, text="3. Процедура: Обновление итоговой стоимости заказа", padding=5)
        frame3.pack(fill=tk.X, padx=10, pady=2)
        
        ttk.Label(frame3, text="ID заказа:").grid(row=0, column=0, padx=5, pady=5)
        self.update_order_id = ttk.Entry(frame3, width=10)
        self.update_order_id.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame3, text="Обновить стоимость", command=self.update_order_total_proc).grid(row=0, column=2, padx=10, pady=5)
        self.update_result = ttk.Label(frame3, text="Результат: ", font=("Arial", 10))
        self.update_result.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        
        # Представление
        frame4 = ttk.LabelFrame(self.reports_frame, text="4. Представление: Детальная информация о заказах", padding=5)
        frame4.pack(fill=tk.BOTH, expand=True, padx=10, pady=2)
            
        columns = ("id", "client", "car", "plate", "master", "status", "total_cost", "works_count", "materials_count")
        self.order_info_tree = ttk.Treeview(frame4, columns=columns, show="headings", height=8)
        
        self.order_info_tree.heading("id", text="№ заказа")
        self.order_info_tree.heading("client", text="Клиент")
        self.order_info_tree.heading("car", text="Автомобиль")
        self.order_info_tree.heading("plate", text="Госномер")
        self.order_info_tree.heading("master", text="Мастер")
        self.order_info_tree.heading("status", text="Статус")
        self.order_info_tree.heading("total_cost", text="Стоимость, руб")
        self.order_info_tree.heading("works_count", text="Кол-во работ")
        self.order_info_tree.heading("materials_count", text="Кол-во материалов")
        
        self.order_info_tree.column("id", width=70)
        self.order_info_tree.column("client", width=180)
        self.order_info_tree.column("car", width=150)
        self.order_info_tree.column("plate", width=100)
        self.order_info_tree.column("master", width=150)
        self.order_info_tree.column("status", width=100)
        self.order_info_tree.column("total_cost", width=100)
        self.order_info_tree.column("works_count", width=100)
        self.order_info_tree.column("materials_count", width=120)
        
        v_scroll = ttk.Scrollbar(frame4, orient=tk.VERTICAL, command=self.order_info_tree.yview)
        self.order_info_tree.configure(yscrollcommand=v_scroll.set)
        self.order_info_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    def create_statusbar(self):
        self.statusbar = ttk.Label(self.root, text="Готово", relief=tk.SUNKEN, anchor=tk.W)
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def refresh_orders_tab(self):
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)
        
        status = self.status_filter.get()
        if status == "все":
            orders = self.db.get_all_orders()
        else:
            orders = self.db.get_all_orders(status)
        
        for order in orders:
            self.orders_tree.insert("", tk.END, values=(
                order['id_order'],
                order.get('client_name', ''),
                order.get('car_name', ''),
                order['accept_date'],
                order.get('completion_date', ''),
                order['status'],
                order['total_cost']
            ))
        
        self.statusbar.config(text=f"Загружено заказов: {len(orders)}")
    
    def refresh_materials_tab(self):
        for item in self.materials_tree.get_children():
            self.materials_tree.delete(item)
        
        materials = self.db.get_material_inventory()
        
        for mat in materials:
            self.materials_tree.insert("", tk.END, values=(
                mat['ID'],
                mat['Наименование'],
                mat['Ед.изм.'],
                mat['Остаток, шт'],
                mat['Закупочная цена, руб'],
                mat['Продажная цена, руб'],
                mat['Наценка, руб'],
                mat['Наценка, %'],
                mat['Стоимость остатков (закупка), руб'],
                mat['Стоимость остатков (продажа), руб'],
                mat['Дата последней поставки']
            ))
        
        self.statusbar.config(text=f"Загружено материалов: {len(materials)}")
    
    def refresh_order_full_info(self):
        for item in self.order_info_tree.get_children():
            self.order_info_tree.delete(item)
        
        orders = self.db.get_order_full_info()
        
        for order in orders:
            self.order_info_tree.insert("", tk.END, values=(
                order['Номер заказа'],
                order['Клиент'],
                order['Автомобиль'],
                order['Госномер'],
                order['Мастер'] or 'Не назначен',
                order['Статус'],
                order['Стоимость, руб'],
                order['Кол-во работ'],
                order['Кол-во материалов']
            ))
        
        self.statusbar.config(text=f"Загружено заказов: {len(orders)}")
    
    def calc_discount(self):
        """Вызов функции calculate_order_total_with_discount"""
        try:
            order_id = int(self.discount_order_id.get())
            discount = float(self.discount_percent.get())
            
            if order_id <= 0:
                messagebox.showerror("Ошибка", "ID заказа должен быть положительным числом")
                return
            
            result = self.db.calculate_discount(order_id, discount)
            
            if result is not None:
                self.discount_result.config(
                    text=f"✅ Результат: Заказ №{order_id} со скидкой {discount}% = {result} руб."
                )
                self.statusbar.config(text=f"Функция выполнена: скидка {discount}% для заказа {order_id}")
            else:
                self.discount_result.config(text=f"❌ Ошибка: Заказ №{order_id} не найден")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректные ID заказа и процент скидки")
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Ошибка БД", f"Заказ с таким ID не существует или ошибка данных: {e}")
    
    def calc_profitability(self):
        """Вызов функции calculate_order_profitability"""
        try:
            order_id = int(self.profit_order_id.get())
            
            if order_id <= 0:
                messagebox.showerror("Ошибка", "ID заказа должен быть положительным числом")
                return
            
            result = self.db.calculate_profitability(order_id)
            
            if result:
                self.profit_result.config(
                    text=f"📊 Заказ №{order_id}: Выручка={result['total_revenue']} руб | "
                        f"Себестоимость={result['total_cost_price']} руб | "
                        f"Прибыль={result['profit']} руб | "
                        f"Рентабельность={result['profitability_percent']}%"
                )
                self.statusbar.config(text=f"Функция рентабельности выполнена для заказа {order_id}")
            else:
                self.profit_result.config(text=f"❌ Заказ №{order_id} не найден")
        except ValueError:
            messagebox.showerror("Ошибка", "Введите корректный ID заказа")
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Ошибка БД", f"Заказ с таким ID не существует: {e}")
    
    def new_order_window(self):
        """Открытие окна создания нового заказа"""
        from dialogs.order_dialog import OrderDialog
        dialog = OrderDialog(self.root, self.db)
        self.root.wait_window(dialog.window)
        self.refresh_orders_tab()
        self.refresh_order_full_info()

    def edit_order(self):
        """Редактирование статуса заказа"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ для редактирования")
            return
        
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        from dialogs.order_dialog import OrderDialog
        dialog = OrderDialog(self.root, self.db, order_id)
        self.root.wait_window(dialog.window)
        self.refresh_orders_tab()
        self.refresh_order_full_info()

    def delete_order(self):
        """Удаление заказа"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")
            return
        
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        if not messagebox.askyesno("Подтверждение", f"Удалить заказ №{order_id}?\nЭто действие необратимо!"):
            return
        
        try:
            self.db.delete_order(order_id)
            messagebox.showinfo("Успех", f"Заказ №{order_id} удалён")
            self.refresh_orders_tab()
            self.refresh_order_full_info()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить заказ: {e}")

    def view_order_details(self):
        """Просмотр деталей заказа (двойной клик)"""
        selection = self.orders_tree.selection()
        if not selection:
            return
        
        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]
        
        try:
            order = self.db.get_order_summary(order_id)
            works = self.db.get_order_works_with_names(order_id)
            materials = self.db.get_order_materials_with_names(order_id)
            masters = self.db.get_order_masters(order_id)
            
            details = f"=== Заказ №{order_id} ===\n\n"
            details += f"Клиент: {order.get('client_name', 'Неизвестно')}\n"
            details += f"Автомобиль: {order.get('car_name', 'Неизвестно')}\n"
            details += f"Статус: {order.get('status', 'Неизвестно')}\n"
            details += f"Дата приёма: {order.get('accept_date', 'Неизвестно')}\n"
            details += f"Стоимость: {order.get('total_cost', 0)} руб.\n\n"
            
            details += "--- Выполненные работы ---\n"
            if works:
                for w in works:
                    price = float(w['price_at_moment']) if w['price_at_moment'] else 0
                    quantity = float(w['quantity']) if w['quantity'] else 0
                    details += f"  {w['name']}: {quantity} шт. x {price} руб. = {quantity * price} руб.\n"
            else:
                details += "  Нет работ\n"
            
            details += "\n--- Использованные материалы ---\n"
            if materials:
                for m in materials:
                    price = float(m['price_at_moment']) if m['price_at_moment'] else 0
                    quantity = float(m['quantity']) if m['quantity'] else 0
                    details += f"  {m['name']}: {quantity} {m.get('unit', 'шт.')} x {price} руб. = {quantity * price} руб.\n"
            else:
                details += "  Нет материалов\n"
            
            details += "\n--- Мастера ---\n"
            if masters:
                for m in masters:
                    details += f"  {m['full_name']}\n"
            else:
                details += "  Нет мастеров\n"
            
            messagebox.showinfo("Детали заказа", details)
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить детали заказа: {e}")
    
    def refresh_all(self):
        self.refresh_orders_tab()
        self.refresh_materials_tab()
        self.refresh_order_full_info()
        self.statusbar.config(text="Все данные обновлены")
    
    def create_references_tab(self):
        """Вкладка справочников"""
        self.references_frame = ttk.Frame(self.refs_frame)
        self.references_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Верхняя панель с кнопками выбора справочника
        selector_frame = ttk.Frame(self.references_frame)
        selector_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(selector_frame, text="Клиенты", command=lambda: self.show_reference("client")).pack(side=tk.LEFT, padx=5)
        ttk.Button(selector_frame, text="Автомобили", command=lambda: self.show_reference("car")).pack(side=tk.LEFT, padx=5)
        ttk.Button(selector_frame, text="Виды работ", command=lambda: self.show_reference("work_type")).pack(side=tk.LEFT, padx=5)
        ttk.Button(selector_frame, text="Материалы", command=lambda: self.show_reference("material")).pack(side=tk.LEFT, padx=5)
        ttk.Button(selector_frame, text="Мастера", command=lambda: self.show_reference("master")).pack(side=tk.LEFT, padx=5)
        
        # Фрейм для кнопок управления (будет обновляться)
        self.ref_buttons_frame = ttk.Frame(self.references_frame)
        self.ref_buttons_frame.pack(fill=tk.X, pady=5)
        
        # Фрейм для таблицы
        self.ref_table_frame = ttk.Frame(self.references_frame)
        self.ref_table_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Таблица
        self.ref_table = ttk.Treeview(self.ref_table_frame, show="headings", height=8)
        self.ref_table.pack(fill=tk.BOTH, expand=True)

    def show_reference(self, ref_type):
        """Показать выбранный справочник"""
        self.current_ref_type = ref_type
        
        # Очищаем старые кнопки
        for widget in self.ref_buttons_frame.winfo_children():
            widget.destroy()
        
        # Создаём новые кнопки
        ttk.Button(self.ref_buttons_frame, text="➕ Добавить", command=self.add_ref_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.ref_buttons_frame, text="✏️ Редактировать", command=self.edit_ref_item).pack(side=tk.LEFT, padx=5)
        ttk.Button(self.ref_buttons_frame, text="🗑 Удалить", command=self.delete_ref_item).pack(side=tk.LEFT, padx=5)
        
        # Очищаем таблицу
        for item in self.ref_table.get_children():
            self.ref_table.delete(item)
        
        # Загружаем данные в зависимости от типа
        if ref_type == "client":
            self.ref_table["columns"] = ("id", "lastname", "firstname", "middlename", "phone")
            self.ref_table.heading("id", text="ID")
            self.ref_table.heading("lastname", text="Фамилия")
            self.ref_table.heading("firstname", text="Имя")
            self.ref_table.heading("middlename", text="Отчество")
            self.ref_table.heading("phone", text="Телефон")
            
            self.ref_table.column("id", width=50)
            self.ref_table.column("lastname", width=150)
            self.ref_table.column("firstname", width=150)
            self.ref_table.column("middlename", width=150)
            self.ref_table.column("phone", width=120)
            
            data = self.db.get_all_clients()
            for item in data:
                self.ref_table.insert("", tk.END, values=(
                    item['id_client'], item['last_name'], item['first_name'],
                    item.get('middle_name', ''), item.get('phone', '')
                ))
        
        elif ref_type == "car":
            self.ref_table["columns"] = ("id", "brand", "model", "plate", "year", "vin", "client")
            self.ref_table.heading("id", text="ID")
            self.ref_table.heading("brand", text="Марка")
            self.ref_table.heading("model", text="Модель")
            self.ref_table.heading("plate", text="Госномер")
            self.ref_table.heading("year", text="Год")
            self.ref_table.heading("vin", text="VIN")
            self.ref_table.heading("client", text="Владелец")
            
            for col in self.ref_table["columns"]:
                self.ref_table.column(col, width=100)
            
            data = self.db.get_all_cars()
            for item in data:
                self.ref_table.insert("", tk.END, values=(
                    item['id_car'], item['brand'], item['model'], item['plate_number'],
                    item.get('year', ''), item.get('vin', ''), item.get('owner_name', '')
                ))
        
        elif ref_type == "work_type":
            self.ref_table["columns"] = ("id", "name", "labor_hours", "price")
            self.ref_table.heading("id", text="ID")
            self.ref_table.heading("name", text="Наименование")
            self.ref_table.heading("labor_hours", text="Трудоёмкость (час)")
            self.ref_table.heading("price", text="Стоимость, руб")
            
            self.ref_table.column("id", width=50)
            self.ref_table.column("name", width=250)
            self.ref_table.column("labor_hours", width=120)
            self.ref_table.column("price", width=120)
            
            data = self.db.get_all_work_types()
            for item in data:
                self.ref_table.insert("", tk.END, values=(
                    item['id_work_type'], item['name'], item.get('labor_hours', 0), item.get('price', 0)
                ))
        
        elif ref_type == "material":
            self.ref_table["columns"] = ("id", "name", "unit", "id_storage", "stock", "purchase_price", "sale_price")
            self.ref_table.heading("id", text="ID")
            self.ref_table.heading("name", text="Наименование")
            self.ref_table.heading("unit", text="Ед.изм.")
            self.ref_table.heading("id_storage", text="ID склада")
            self.ref_table.heading("stock", text="Остаток")
            self.ref_table.heading("purchase_price", text="Закупка, руб")
            self.ref_table.heading("sale_price", text="Продажа, руб")
            
            for col in self.ref_table["columns"]:
                self.ref_table.column(col, width=100)
            
            data = self.db.get_all_materials()
            for item in data:
                self.ref_table.insert("", tk.END, values=(
                    item['id_material'], item['name'], item.get('unit', ''),
                    item.get('id_storage', ''), item.get('stock_balance', 0),
                    item.get('purchase_price', 0), item.get('sale_price', 0)
                ))
        
        elif ref_type == "master":
            self.ref_table["columns"] = ("id", "lastname", "firstname", "middlename", "id_position", "specialization", "phone", "hire_date")
            self.ref_table.heading("id", text="ID")
            self.ref_table.heading("lastname", text="Фамилия")
            self.ref_table.heading("firstname", text="Имя")
            self.ref_table.heading("middlename", text="Отчество")
            self.ref_table.heading("id_position", text="ID должности")
            self.ref_table.heading("specialization", text="Специализация")
            self.ref_table.heading("phone", text="Телефон")
            self.ref_table.heading("hire_date", text="Дата приёма")
            
            for col in self.ref_table["columns"]:
                self.ref_table.column(col, width=100)
            
            data = self.db.get_all_masters()
            for item in data:
                self.ref_table.insert("", tk.END, values=(
                    item['id_master'], item['last_name'], item['first_name'],
                    item.get('middle_name', ''), item.get('id_position', ''),
                    item.get('specialization', ''), item.get('phone', ''),
                    item.get('hire_date', '')
                ))

    def add_ref_buttons(self, ref_type):
        """Добавить кнопки управления справочником"""
        btn_frame = ttk.Frame(self.refs_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="➕ Добавить", command=lambda: self.add_ref_item(ref_type)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="✏️ Редактировать", command=lambda: self.edit_ref_item(ref_type)).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="🗑 Удалить", command=lambda: self.delete_ref_item(ref_type)).pack(side=tk.LEFT, padx=5)
        
        self.current_ref_type = ref_type

    def add_ref_item(self):
        """Добавление элемента справочника"""
        if self.current_ref_type == "client":
            from dialogs.client_dialog import ClientDialog
            dialog = ClientDialog(self.root, self.db)
        elif self.current_ref_type == "car":
            from dialogs.car_dialog import CarDialog
            dialog = CarDialog(self.root, self.db)
        elif self.current_ref_type == "work_type":
            from dialogs.work_type_dialog import WorkTypeDialog
            dialog = WorkTypeDialog(self.root, self.db)
        elif self.current_ref_type == "material":
            from dialogs.material_dialog import MaterialDialog
            dialog = MaterialDialog(self.root, self.db)
        elif self.current_ref_type == "master":
            from dialogs.master_dialog import MasterDialog
            dialog = MasterDialog(self.root, self.db)
        else:
            messagebox.showinfo("В разработке", f"Добавление {self.current_ref_type} в разработке")
            return
        
        self.root.wait_window(dialog.window)
        self.show_reference(self.current_ref_type)

    def edit_ref_item(self):
        """Редактирование элемента справочника"""
        selection = self.ref_table.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите элемент для редактирования")
            return
        
        item = self.ref_table.item(selection[0])
        item_id = item['values'][0]
        
        if self.current_ref_type == "client":
            from dialogs.client_dialog import ClientDialog
            dialog = ClientDialog(self.root, self.db, item_id)
        elif self.current_ref_type == "car":
            from dialogs.car_dialog import CarDialog
            dialog = CarDialog(self.root, self.db, item_id)
        elif self.current_ref_type == "work_type":
            from dialogs.work_type_dialog import WorkTypeDialog
            dialog = WorkTypeDialog(self.root, self.db, item_id)
        elif self.current_ref_type == "material":
            from dialogs.material_dialog import MaterialDialog
            dialog = MaterialDialog(self.root, self.db, item_id)
        elif self.current_ref_type == "master":
            from dialogs.master_dialog import MasterDialog
            dialog = MasterDialog(self.root, self.db, item_id)
        else:
            messagebox.showinfo("В разработке", f"Редактирование {self.current_ref_type} в разработке")
            return
        
        self.root.wait_window(dialog.window)
        self.show_reference(self.current_ref_type)

    def delete_ref_item(self):
        """Удаление элемента справочника"""
        selection = self.ref_table.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите элемент для удаления")
            return
        
        if not messagebox.askyesno("Подтверждение", "Удалить выбранный элемент?\n(Если есть связанные данные, удаление будет невозможно)"):
            return
        
        item = self.ref_table.item(selection[0])
        item_id = item['values'][0]
        
        try:
            with self.db.get_cursor() as cur:
                if self.current_ref_type == "client":
                    cur.execute("DELETE FROM client WHERE id_client = %s", (item_id,))
                elif self.current_ref_type == "car":
                    cur.execute("DELETE FROM car WHERE id_car = %s", (item_id,))
                elif self.current_ref_type == "work_type":
                    cur.execute("DELETE FROM work_type WHERE id_work_type = %s", (item_id,))
                elif self.current_ref_type == "material":
                    cur.execute("DELETE FROM material WHERE id_material = %s", (item_id,))
                elif self.current_ref_type == "master":
                    cur.execute("DELETE FROM master WHERE id_master = %s", (item_id,))
                self.db.commit()
            
            messagebox.showinfo("Успех", "Элемент удалён")
            self.show_reference(self.current_ref_type)
        except Exception as e:
            self.db.rollback()
            messagebox.showerror("Ошибка", f"Нельзя удалить, есть связанные данные: {e}")


def main():
    root = tk.Tk()
    app = CarServiceApp(root)
    app.refresh_materials_tab()
    app.refresh_order_full_info()
    root.mainloop()


if __name__ == "__main__":
    main()