import psycopg2
from psycopg2 import sql, extras
from config import DB_CONFIG

class Database:
    """Класс для работы с БД PostgreSQL без использования ORM"""
    
    def __init__(self):
        self.conn = None
        self.connect()
    
    def connect(self):
        """Установка соединения с БД"""
        try:
            self.conn = psycopg2.connect(**DB_CONFIG)
            self.conn.autocommit = False  # ручное управление транзакциями
            print("Подключение к БД установлено")
        except Exception as e:
            print(f"Ошибка подключения: {e}")
            raise
    
    def get_cursor(self):
        """Получить курсор с поддержкой словарей"""
        return self.conn.cursor(cursor_factory=extras.RealDictCursor)
    
    def commit(self):
        """Фиксация транзакции"""
        self.conn.commit()
    
    def rollback(self):
        """Откат транзакции"""
        self.conn.rollback()
    
    def close(self):
        """Закрытие соединения"""
        if self.conn:
            self.conn.close()
    
    # вызов функции вычисления стоимости заказа с учётом скидки
    def calculate_discount(self, order_id, discount_percent):
        """
        Вызов скалярной функции calculate_order_total_with_discount
        Возвращает стоимость заказа с учётом скидки
        """
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    "SELECT calculate_order_total_with_discount(%s, %s) as total",
                    (order_id, discount_percent)
                )
                result = cur.fetchone()
                self.conn.commit()
                return result['total'] if result else None
        except Exception as e:
            self.conn.rollback()
            raise e
    
    # вызов табличной функции для получения рентабельности заказа
    def calculate_profitability(self, order_id):
        """
        Вызов табличной функции calculate_order_profitability
        
        """
        try:
            with self.get_cursor() as cur:
                cur.execute(
                    "SELECT * FROM calculate_order_profitability(%s)",
                    (order_id,)
                )
                result = cur.fetchone()
                self.conn.commit()
                return result if result else None
        except Exception as e:
            self.conn.rollback()
            raise e
    
    # вызов хранимой процедуры для обновления итоговой стоимости заказа
    def update_order_total(self, order_id):
        """
        Вызов хранимой процедуры update_order_total
        """
        try:
            with self.get_cursor() as cur:
                cur.execute("CALL update_order_total(%s)", (order_id,))
                self.conn.commit()
                return True
        except Exception as e:
            self.conn.rollback()
            raise e
    
    # получение данных из представления order_full_info
    def get_order_full_info(self, limit=100):
        """
        Получение данных из представления order_full_info
        """
        with self.get_cursor() as cur:
            cur.execute(
                "SELECT * FROM order_full_info LIMIT %s",
                (limit,)
            )
            return cur.fetchall()
    
    def get_material_inventory(self):
        """
        Получение данных из представления material_inventory
        """
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM material_inventory")
            return cur.fetchall()
    
    # основные операции CRUD
    def get_all_orders(self, status=None):
        """Получить список заказов с возможной фильтрацией по статусу"""
        with self.get_cursor() as cur:
            if status and status != "все":
                cur.execute("""
                    SELECT o.*, 
                        COALESCE(c.last_name || ' ' || c.first_name || ' ' || c.middle_name, 
                                    c.last_name || ' ' || c.first_name) as client_name,
                        COALESCE(car.brand || ' ' || car.model, car.brand) as car_name
                    FROM orders o
                    LEFT JOIN client c ON o.id_client = c.id_client
                    LEFT JOIN car ON o.id_car = car.id_car
                    WHERE o.status = %s 
                    ORDER BY o.accept_date DESC
                """, (status,))
            else:
                cur.execute("""
                    SELECT o.*, 
                        COALESCE(c.last_name || ' ' || c.first_name || ' ' || c.middle_name, 
                                    c.last_name || ' ' || c.first_name) as client_name,
                        COALESCE(car.brand || ' ' || car.model, car.brand) as car_name
                    FROM orders o
                    LEFT JOIN client c ON o.id_client = c.id_client
                    LEFT JOIN car ON o.id_car = car.id_car
                    ORDER BY o.accept_date DESC
                """)
            return cur.fetchall()
    
    def get_order_by_id(self, order_id):
        """Получить заказ по ID"""
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM orders WHERE id_order = %s", (order_id,))
            return cur.fetchone()
    
    def get_all_clients(self):
        """Получить всех клиентов"""
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM client ORDER BY last_name, first_name")
            return cur.fetchall()
    
    def get_all_cars(self):
        """Получить все автомобили"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT c.*, cl.last_name || ' ' || cl.first_name as owner_name
                FROM car c
                JOIN client cl ON c.id_client = cl.id_client
                ORDER BY c.brand, c.model
            """)
            return cur.fetchall()
    
    def get_all_masters(self):
        """Получить всех мастеров"""
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM master ORDER BY last_name, first_name")
            return cur.fetchall()
    
    def get_all_work_types(self):
        """Получить все виды работ"""
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM work_type ORDER BY name")
            return cur.fetchall()
    
    def get_all_materials(self):
        """Получить все расходные материалы"""
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM material ORDER BY name")
            return cur.fetchall()
    
    def get_order_works(self, order_id):
        """Получить работы по заказу"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT ow.*, wt.name, wt.labor_hours
                FROM order_work ow
                JOIN work_type wt ON ow.id_work_type = wt.id_work_type
                WHERE ow.id_order = %s
            """, (order_id,))
            return cur.fetchall()
    
    def get_order_materials(self, order_id):
        """Получить материалы по заказу"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT om.*, m.name, m.unit
                FROM order_material om
                JOIN material m ON om.id_material = m.id_material
                WHERE om.id_order = %s
            """, (order_id,))
            return cur.fetchall()
    
    def add_work_to_order(self, order_id, work_type_id, quantity=1, price_at_moment=None):
        """Добавить работу в заказ"""
        with self.get_cursor() as cur:
            # Если цена не указана, берём из справочника
            if price_at_moment is None:
                cur.execute("SELECT price FROM work_type WHERE id_work_type = %s", (work_type_id,))
                price_at_moment = cur.fetchone()['price']
            
            cur.execute("""
                INSERT INTO order_work (id_order, id_work_type, quantity, price_at_moment)
                VALUES (%s, %s, %s, %s)
            """, (order_id, work_type_id, quantity, price_at_moment))
            self.commit()
    
    def add_material_to_order(self, order_id, material_id, quantity, price_at_moment=None):
        """Добавить материал в заказ"""
        with self.get_cursor() as cur:
            if price_at_moment is None:
                cur.execute("SELECT sale_price FROM material WHERE id_material = %s", (material_id,))
                price_at_moment = cur.fetchone()['sale_price']
            
            cur.execute("""
                INSERT INTO order_material (id_order, id_material, quantity, price_at_moment)
                VALUES (%s, %s, %s, %s)
            """, (order_id, material_id, quantity, price_at_moment))
            self.commit()
    
    def assign_master_to_order(self, order_id, master_id):
        """Назначить мастера на заказ (связь master_order)"""
        with self.get_cursor() as cur:
            # Проверяем, существует ли уже связь
            cur.execute("""
                SELECT 1 FROM master_order WHERE id_order = %s AND id_master = %s
            """, (order_id, master_id))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO master_order (id_order, id_master)
                    VALUES (%s, %s)
                """, (order_id, master_id))
                self.commit()
    
    def get_order_summary(self, order_id):
        """Получить сводку по заказу (для отображения)"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT 
                    o.*,
                    c.last_name || ' ' || c.first_name as client_name,
                    car.brand || ' ' || car.model as car_name,
                    car.plate_number
                FROM orders o
                JOIN client c ON o.id_client = c.id_client
                JOIN car ON o.id_car = car.id_car
                WHERE o.id_order = %s
            """, (order_id,))
            return cur.fetchone()
        
    def get_client_by_id(self, client_id):
        """Получить клиента по ID"""
        with self.get_cursor() as cur:
            cur.execute("SELECT * FROM client WHERE id_client = %s", (client_id,))
            return cur.fetchone()
        
    def get_cars_by_client(self, client_id):
        """Получить автомобили клиента"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_car, brand || ' ' || model || ' (' || plate_number || ')' as car_info
                FROM car 
                WHERE id_client = %s
                ORDER BY brand, model
            """, (client_id,))
            return cur.fetchall()
        
    def get_clients_for_combo(self):
        """Получить список клиентов для выпадающего списка"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_client, 
                    last_name || ' ' || first_name || COALESCE(' ' || middle_name, '') as full_name,
                    phone
                FROM client 
                ORDER BY last_name, first_name
            """)
            return cur.fetchall()
        
    def get_work_types_for_combo(self):
        """Получить виды работ для выпадающего списка"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_work_type, name, price, labor_hours
                FROM work_type 
                ORDER BY name
            """)
            return cur.fetchall()

    def get_materials_for_combo(self):
        """Получить материалы для выпадающего списка"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_material, name, sale_price, stock_balance
                FROM material 
                WHERE stock_balance > 0 OR stock_balance IS NULL
                ORDER BY name
            """)
            return cur.fetchall()

    def get_masters_for_combo(self):
        """Получить список мастеров"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT id_master, 
                    last_name || ' ' || first_name || COALESCE(' ' || middle_name, '') as full_name
                FROM master 
                ORDER BY last_name, first_name
            """)
            return cur.fetchall()
        
    def get_order_works_with_names(self, order_id):
        """Получить работы заказа с названиями"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT ow.*, wt.name, wt.labor_hours
                FROM order_work ow
                JOIN work_type wt ON ow.id_work_type = wt.id_work_type
                WHERE ow.id_order = %s
            """, (order_id,))
            return cur.fetchall()

    def get_order_materials_with_names(self, order_id):
        """Получить материалы заказа с названиями"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT om.*, m.name, m.unit
                FROM order_material om
                JOIN material m ON om.id_material = m.id_material
                WHERE om.id_order = %s
            """, (order_id,))
            return cur.fetchall()

    def get_order_masters(self, order_id):
        """Получить мастеров заказа"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT m.id_master, m.last_name || ' ' || m.first_name || COALESCE(' ' || m.middle_name, '') as full_name
                FROM master_order mo
                JOIN master m ON mo.id_master = m.id_master
                WHERE mo.id_order = %s
            """, (order_id,))
            return cur.fetchall()

    def get_order_summary(self, order_id):
        """Получить сводку по заказу"""
        with self.get_cursor() as cur:
            cur.execute("""
                SELECT o.*, c.id_client, c.last_name, c.first_name, car.id_car
                FROM orders o
                JOIN client c ON o.id_client = c.id_client
                JOIN car ON o.id_car = car.id_car
                WHERE o.id_order = %s
            """, (order_id,))
            return cur.fetchone()
        
    def create_full_order(self, client_id, car_id, master_ids, work_items, material_items):
        """Создание полного заказа"""
        from datetime import datetime

        with self.get_cursor() as cur:
            # Получаем текущую дату и время (без долей секунд)
            current_datetime = datetime.now().replace(microsecond=0)

            # Создаём заказ
            cur.execute("""
                INSERT INTO orders (id_client, id_car, accept_date, status, total_cost)
                VALUES (%s, %s, %s, 'принят', 0)
                RETURNING id_order
            """, (client_id, car_id, current_datetime))
            order_id = cur.fetchone()['id_order']
            
            # Добавляем работы
            for w in work_items:
                cur.execute("""
                    INSERT INTO order_work (id_order, id_work_type, quantity, price_at_moment)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, w['work_type_id'], w['quantity'], w['price']))
            
            # Добавляем материалы
            for m in material_items:
                cur.execute("""
                    INSERT INTO order_material (id_order, id_material, quantity, price_at_moment)
                    VALUES (%s, %s, %s, %s)
                """, (order_id, m['material_id'], m['quantity'], m['price']))
            
            # Добавляем мастеров
            for master_id in master_ids:
                cur.execute("""
                    INSERT INTO master_order (id_order, id_master)
                    VALUES (%s, %s)
                """, (order_id, master_id))
            
            # Обновляем стоимость через процедуру
            cur.execute("CALL update_order_total(%s)", (order_id,))
            
            self.commit()
            return order_id
        
    def update_order_status(self, order_id, new_status):
        """Обновить статус заказа"""
        from datetime import datetime

        with self.get_cursor() as cur:
            # Получаем текущую дату и время (без долей секунд)
            current_datetime = datetime.now().replace(microsecond=0)
            
            # Обновляем статус
            cur.execute("""
                UPDATE orders 
                SET status = %s
                WHERE id_order = %s
            """, (new_status, order_id))
            
            # Если заказ выполнен или закрыт, обновляем дату выполнения
            if new_status in ('выполнен', 'закрыт'):
                cur.execute("""
                    UPDATE orders 
                    SET completion_date = %s
                    WHERE id_order = %s AND completion_date IS NULL
                """, (current_datetime, order_id))
            
            self.commit()

    def delete_order(self, order_id):
        """Полное удаление заказа"""
        with self.get_cursor() as cur:
            # Удаляем связи с мастерами
            cur.execute("DELETE FROM master_order WHERE id_order = %s", (order_id,))
            # Удаляем работы заказа
            cur.execute("DELETE FROM order_work WHERE id_order = %s", (order_id,))
            # Удаляем материалы заказа
            cur.execute("DELETE FROM order_material WHERE id_order = %s", (order_id,))
            # Удаляем оплату (если есть)
            cur.execute("DELETE FROM payment WHERE id_order = %s", (order_id,))
            # Удаляем сам заказ
            cur.execute("DELETE FROM orders WHERE id_order = %s", (order_id,))
            self.commit()
            return True