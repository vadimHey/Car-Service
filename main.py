# main.py
import tkinter as tk
from tkinter import ttk, messagebox
from database import Database

class CarServiceApp:
    """Главное приложение автосервиса"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Автосервис - Система управления заказами")
        self.root.geometry("1300x750")
        
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
        
        # Меню "Файл"
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Файл", menu=file_menu)
        file_menu.add_command(label="Обновить все данные", command=self.refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Выход", command=self.root.quit)
        
        # Меню "Справка"
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Справка", menu=help_menu)
        help_menu.add_command(label="О программе", command=self.show_about)
    
    def create_notebook(self):
        """Создание вкладок"""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Вкладка 1: Заказы
        self.orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_frame, text="📋 Заказы")
        self.create_orders_tab()
        
        # Вкладка 2: Склад и материалы
        self.materials_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.materials_frame, text="📦 Склад")
        self.create_materials_tab()
        
        # Вкладка 3: Отчёты и аналитика
        self.reports_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.reports_frame, text="📊 Аналитика")
        self.create_reports_tab()
        
        # Вкладка 4: Справочники
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
        ttk.Button(top_frame, text="🔄 Обновить", command=self.refresh_orders_tab).pack(side=tk.LEFT, padx=2)
        
        # Фильтр по статусу
        ttk.Label(top_frame, text="Фильтр:").pack(side=tk.LEFT, padx=(20, 5))
        self.status_filter = ttk.Combobox(top_frame, values=["все", "принят", "в работе", "выполнен", "закрыт"], width=15)
        self.status_filter.set("все")
        self.status_filter.bind("<<ComboboxSelected>>", lambda e: self.refresh_orders_tab())
        self.status_filter.pack(side=tk.LEFT, padx=2)
        
        # Таблица заказов
        columns = ("id", "client", "car", "accept_date", "completion_date", "status", "total_cost")
        self.orders_tree = ttk.Treeview(self.orders_frame, columns=columns, show="headings", height=20)
        
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
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.orders_tree.bind("<Double-1>", lambda e: self.view_order_details())
    
    def create_materials_tab(self):
        """Вкладка складского учёта"""
        top_frame = ttk.Frame(self.materials_frame)
        top_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Button(top_frame, text="🔄 Обновить", command=self.refresh_materials_tab).pack(side=tk.LEFT)
        
        columns = ("id", "name", "unit", "stock", "purchase_price", "sale_price", "markup", "markup_percent", 
                   "stock_cost_purchase", "stock_cost_sale", "last_supply")
        self.materials_tree = ttk.Treeview(self.materials_frame, columns=columns, show="headings", height=20)
        
        self.materials_tree.heading("id", text="ID")
        self.materials_tree.heading("name", text="Наименование")
        self.materials_tree.heading("unit", text="Ед.изм.")
        self.materials_tree.heading("stock", text="Остаток")
        self.materials_tree.heading("purchase_price", text="Закупка, руб")
        self.materials_tree.heading("sale_price", text="Продажа, руб")
        self.materials_tree.heading("markup", text="Наценка, руб")
        self.materials_tree.heading("markup_percent", text="Наценка, %")
        self.materials_tree.heading("stock_cost_purchase", text="Стоимость остатков (закупка)")
        self.materials_tree.heading("stock_cost_sale", text="Стоимость остатков (продажа)")
        self.materials_tree.heading("last_supply", text="Дата последней поставки")
        
        self.materials_tree.column("id", width=50)
        self.materials_tree.column("name", width=200)
        self.materials_tree.column("unit", width=70)
        self.materials_tree.column("stock", width=80)
        self.materials_tree.column("purchase_price", width=100)
        self.materials_tree.column("sale_price", width=100)
        self.materials_tree.column("markup", width=90)
        self.materials_tree.column("markup_percent", width=90)
        self.materials_tree.column("stock_cost_purchase", width=150)
        self.materials_tree.column("stock_cost_sale", width=150)
        self.materials_tree.column("last_supply", width=120)
        
        v_scroll = ttk.Scrollbar(self.materials_frame, orient=tk.VERTICAL, command=self.materials_tree.yview)
        h_scroll = ttk.Scrollbar(self.materials_frame, orient=tk.HORIZONTAL, command=self.materials_tree.xview)
        self.materials_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.materials_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_reports_tab(self):
        """Вкладка аналитики - функции и процедура"""
        # Функция 1: Расчёт со скидкой
        frame1 = ttk.LabelFrame(self.reports_frame, text="1. Функция: Расчёт стоимости со скидкой", padding=10)
        frame1.pack(fill=tk.X, padx=10, pady=5)
        
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
        frame2 = ttk.LabelFrame(self.reports_frame, text="2. Функция: Расчёт рентабельности заказа", padding=10)
        frame2.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame2, text="ID заказа:").grid(row=0, column=0, padx=5, pady=5)
        self.profit_order_id = ttk.Entry(frame2, width=10)
        self.profit_order_id.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame2, text="Рассчитать рентабельность", command=self.calc_profitability).grid(row=0, column=2, padx=10, pady=5)
        self.profit_result = ttk.Label(frame2, text="Результат: ", font=("Arial", 10))
        self.profit_result.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        
        # Процедура
        frame3 = ttk.LabelFrame(self.reports_frame, text="3. Процедура: Обновление итоговой стоимости заказа", padding=10)
        frame3.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(frame3, text="ID заказа:").grid(row=0, column=0, padx=5, pady=5)
        self.update_order_id = ttk.Entry(frame3, width=10)
        self.update_order_id.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(frame3, text="Обновить стоимость", command=self.update_order_total_proc).grid(row=0, column=2, padx=10, pady=5)
        self.update_result = ttk.Label(frame3, text="Результат: ", font=("Arial", 10))
        self.update_result.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="w")
        
        # Представление
        frame4 = ttk.LabelFrame(self.reports_frame, text="4. Представление: Детальная информация о заказах", padding=10)
        frame4.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            
        columns = ("id", "client", "car", "plate", "master", "status", "total_cost", "works_count", "materials_count")
        self.order_info_tree = ttk.Treeview(frame4, columns=columns, show="headings", height=10)
        
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
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_references_tab(self):
        """Вкладка справочников"""
        # Создаём фрейм для вкладки справочников
        references_frame = ttk.Frame(self.refs_frame)
        references_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        ttk.Label(references_frame, text="Справочники", font=("Arial", 14, "bold")).pack(pady=10)
        
        btn_frame = ttk.Frame(references_frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Клиенты", width=20, command=self.show_clients).pack(pady=2)
        ttk.Button(btn_frame, text="Автомобили", width=20, command=self.show_cars).pack(pady=2)
        ttk.Button(btn_frame, text="Виды работ", width=20, command=self.show_work_types).pack(pady=2)
        ttk.Button(btn_frame, text="Материалы", width=20, command=self.show_materials).pack(pady=2)
        ttk.Button(btn_frame, text="Мастера", width=20, command=self.show_masters).pack(pady=2)
        
        ttk.Label(references_frame, text="(Функционал в разработке)", font=("Arial", 10)).pack(pady=20)
    
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
            messagebox.showerror("Ошибка БД", f"Заказ с таким ID не существует: {e}")
    
    def view_order_details(self):
        selection = self.orders_tree.selection()
        if selection:
            item = self.orders_tree.item(selection[0])
            order_id = item['values'][0]
            messagebox.showinfo("Детали заказа", f"Заказ №{order_id}\n\nФункционал просмотра деталей будет добавлен в следующей версии.")
    
    def new_order_window(self):
        messagebox.showinfo("Новый заказ", "Окно создания заказа будет добавлено в следующей версии.")
    
    def edit_order(self):
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ для редактирования")
            return
        messagebox.showinfo("Редактирование", "Функционал редактирования в разработке")
    
    def refresh_all(self):
        self.refresh_orders_tab()
        self.refresh_materials_tab()
        self.refresh_order_full_info()
        self.statusbar.config(text="Все данные обновлены")
    
    def show_about(self):
        messagebox.showinfo("О программе",
            "Автосервис - Система управления заказами\n\n"
            "Версия 1.0\n"
            "Разработано в рамках практической работы №5\n\n"
            "Используемые технологии:\n"
            "- Python 3\n"
            "- Tkinter (GUI)\n"
            "- PostgreSQL\n"
            "- psycopg2 (без ORM)")
    
    def show_clients(self):
        messagebox.showinfo("Справочник", "Справочник клиентов будет добавлен в следующей версии")
    
    def show_cars(self):
        messagebox.showinfo("Справочник", "Справочник автомобилей будет добавлен в следующей версии")
    
    def show_work_types(self):
        messagebox.showinfo("Справочник", "Справочник видов работ будет добавлен в следующей версии")
    
    def show_materials(self):
        messagebox.showinfo("Справочник", "Справочник материалов будет добавлен в следующей версии")
    
    def show_masters(self):
        messagebox.showinfo("Справочник", "Справочник мастеров будет добавлен в следующей версии")


def main():
    root = tk.Tk()
    app = CarServiceApp(root)
    app.refresh_materials_tab()
    app.refresh_order_full_info()
    root.mainloop()


if __name__ == "__main__":
    main()