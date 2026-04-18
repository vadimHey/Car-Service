# database.py
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
                        COALESCE(c.last_name || ' ' || c.first_name || ' ' || c.middle_name, c.last_name || ' ' || c.first_name) as client_name,
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
                        COALESCE(c.last_name || ' ' || c.first_name || ' ' || c.middle_name, c.last_name || ' ' || c.first_name) as client_name,
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
    
    def create_order(self, client_id, car_id, status='принят'):
        """Создать новый заказ"""
        with self.get_cursor() as cur:
            cur.execute("""
                INSERT INTO orders (id_client, id_car, accept_date, status, total_cost)
                VALUES (%s, %s, CURRENT_DATE, %s, 0)
                RETURNING id_order
            """, (client_id, car_id, status))
            order_id = cur.fetchone()['id_order']
            self.commit()
            return order_id
    
    def add_work_to_order(self, order_id, work_type_id, quantity=1, price_at_moment=None):
        """Добавить работу в заказ"""
        with self.get_cursor() as cur:
            # Если цена не указана, берём из справочника
            if price_at_moment is None:
                cur.execute("SELECT cost FROM work_type WHERE id_work_type = %s", (work_type_id,))
                price_at_moment = cur.fetchone()['cost']
            
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