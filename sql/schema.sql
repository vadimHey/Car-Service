-- создание основных таблиц
CREATE TABLE client (
    id_client SERIAL PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    middle_name VARCHAR(30),
    phone VARCHAR(20) UNIQUE NOT NULL
);

CREATE TABLE car (
    id_car SERIAL PRIMARY KEY,
    plate_number VARCHAR(12) UNIQUE NOT NULL,
    brand VARCHAR(30) NOT NULL,
    model VARCHAR(30) NOT NULL,
    year INTEGER CHECK (year BETWEEN 1900 AND EXTRACT(YEAR FROM CURRENT_DATE)),
    vin VARCHAR(20) UNIQUE,
    id_client INTEGER NOT NULL REFERENCES client(id_client) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE position (
    id_position SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE master (
    id_master SERIAL PRIMARY KEY,
    first_name VARCHAR(30) NOT NULL,
    last_name VARCHAR(30) NOT NULL,
    middle_name VARCHAR(30),
    specialization VARCHAR(50),
    phone VARCHAR(20) UNIQUE NOT NULL,
    hire_date DATE NOT NULL DEFAULT CURRENT_DATE,
    id_position INTEGER NOT NULL REFERENCES position(id_position) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE work_type (
    id_work_type SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    labor_hours NUMERIC(5,2) CHECK (labor_hours > 0),
    price NUMERIC(10,2) CHECK (price > 0)
);

CREATE TABLE storage (
    id_storage SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE material (
    id_material SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    unit VARCHAR(10) NOT NULL,
    purchase_price NUMERIC(10,2) CHECK (purchase_price >= 0),
    sale_price NUMERIC(10,2) CHECK (sale_price >= 0),
    stock_balance INTEGER DEFAULT 0 CHECK (stock_balance >= 0),
    id_storage INTEGER NOT NULL REFERENCES storage(id_storage) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE supplier (
    id_supplier SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    inn VARCHAR(12) UNIQUE NOT NULL,
    phone VARCHAR(20),
    adress VARCHAR(100)
);

CREATE TABLE orders (
    id_order SERIAL PRIMARY KEY,
    accept_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completion_date TIMESTAMP,
    status VARCHAR(20) DEFAULT 'принят' CHECK (status IN ('принят', 'в работе', 'выполнен', 'закрыт')),
    total_cost NUMERIC(12,2) DEFAULT 0,
    id_client INTEGER NOT NULL REFERENCES client(id_client) ON DELETE CASCADE ON UPDATE CASCADE,
    id_car INTEGER NOT NULL REFERENCES car(id_car) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE supply (
    id_supply SERIAL PRIMARY KEY,
    supply_number VARCHAR(20) UNIQUE NOT NULL,
    supply_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    purchase_price NUMERIC(10,2) NOT NULL CHECK (purchase_price > 0),
    id_material INTEGER NOT NULL REFERENCES material(id_material) ON DELETE CASCADE ON UPDATE CASCADE,
    id_supplier INTEGER NOT NULL REFERENCES supplier(id_supplier) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE equipment (
    id_equipment SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE payment (
    id_payment SERIAL PRIMARY KEY,
    amount NUMERIC(12,2) NOT NULL CHECK (amount > 0),
    payment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_order INTEGER NOT NULL UNIQUE REFERENCES orders(id_order) ON DELETE CASCADE ON UPDATE CASCADE
);

-- создание промежуточных таблиц
CREATE TABLE master_order (
    id_master_order SERIAL PRIMARY KEY,
    id_master INTEGER NOT NULL REFERENCES master(id_master) ON DELETE CASCADE,
    id_order INTEGER NOT NULL REFERENCES orders(id_order) ON DELETE CASCADE,
    assignment_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_master, id_order)
);

CREATE TABLE order_work (
    id_order_work SERIAL PRIMARY KEY,
    id_order INTEGER NOT NULL REFERENCES orders(id_order) ON DELETE CASCADE,
    id_work_type INTEGER NOT NULL REFERENCES work_type(id_work_type),
    quantity INTEGER NOT NULL DEFAULT 1 CHECK (quantity > 0),
    price_at_moment NUMERIC(10,2) NOT NULL,
    UNIQUE(id_order, id_work_type)
);

CREATE TABLE order_material (
    id_order_material SERIAL PRIMARY KEY,
    id_order INTEGER NOT NULL REFERENCES orders(id_order) ON DELETE CASCADE,
    id_material INTEGER NOT NULL REFERENCES material(id_material),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    price_at_moment NUMERIC(10,2) NOT NULL,
    UNIQUE(id_order, id_material)
);

CREATE TABLE master_specialization (
    id_specialization SERIAL PRIMARY KEY,
    id_master INTEGER NOT NULL REFERENCES master(id_master) ON DELETE CASCADE,
    id_work_type INTEGER NOT NULL REFERENCES work_type(id_work_type),
    UNIQUE(id_master, id_work_type)
);

CREATE TABLE master_equipment (
    id_master_equipment SERIAL PRIMARY KEY,
    id_master INTEGER NOT NULL REFERENCES master(id_master) ON DELETE CASCADE,
    id_equipment INTEGER NOT NULL REFERENCES equipment(id_equipment) ON DELETE CASCADE,
    usage_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(id_master, id_equipment)
);

-- индексы внешних ключей для основных таблиц
CREATE INDEX idx_car_owner ON car(id_client);
CREATE INDEX idx_master_position ON master(id_position);
CREATE INDEX idx_material_storage ON material(id_storage);
CREATE INDEX idx_orders_client ON orders(id_client);
CREATE INDEX idx_orders_vehicle ON orders(id_car);
CREATE INDEX idx_supply_material ON supply(id_material);
CREATE INDEX idx_supply_supplier ON supply(id_supplier);
CREATE INDEX idx_payment_order ON payment(id_order);

-- индексы для промежуточных таблиц
CREATE INDEX idx_master_order_master ON master_order(id_master);
CREATE INDEX idx_master_order_order ON master_order(id_order);
CREATE INDEX idx_order_work_order ON order_work(id_order);
CREATE INDEX idx_order_work_work_type ON order_work(id_work_type);
CREATE INDEX idx_order_material_order ON order_material(id_order);
CREATE INDEX idx_order_material_material ON order_material(id_material);
CREATE INDEX idx_master_spec_master ON master_specialization(id_master);
CREATE INDEX idx_master_spec_work_type ON master_specialization(id_work_type);
CREATE INDEX idx_master_equipment_master ON master_equipment(id_master);
CREATE INDEX idx_master_equipment_equipment ON master_equipment(id_equipment);