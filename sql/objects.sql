-- функция расчета стоимости со скидкой
CREATE OR REPLACE FUNCTION calculate_order_total_with_discount(
    p_id_order INTEGER,
    p_discount_percent NUMERIC DEFAULT 0
)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC;
    v_discounted_total NUMERIC;
BEGIN
    IF p_discount_percent < 0 OR p_discount_percent > 100 THEN
        RAISE EXCEPTION 'Скидка должна быть от 0 до 100 процентов';
    END IF;
    
    -- расчет суммы работ по заказу
    WITH work_sum AS (
        SELECT COALESCE(SUM(ow.price_at_moment * ow.quantity), 0) as sum_work
        FROM order_work ow
        WHERE ow.id_order = p_id_order
    ),
    -- расчет суммы материалов по заказу
    material_sum AS (
        SELECT COALESCE(SUM(om.price_at_moment * om.quantity), 0) as sum_material
        FROM order_material om
        WHERE om.id_order = p_id_order
    )
    SELECT work_sum.sum_work + material_sum.sum_material INTO v_total
    FROM work_sum, material_sum;

    v_discounted_total := v_total * (1 - p_discount_percent / 100);
    v_discounted_total := ROUND(v_discounted_total, 2);
    
    RETURN v_discounted_total;
END;
$$;

-- функция расчета себестоимости и рентабельности заказа
CREATE OR REPLACE FUNCTION calculate_order_profitability(
    p_id_order INTEGER,
    OUT total_revenue NUMERIC,
    OUT total_cost_price NUMERIC,
    OUT profit NUMERIC,
    OUT profitability_percent NUMERIC
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_labor_cost NUMERIC;
    v_materials_cost_price NUMERIC;
    v_work_revenue NUMERIC;
    v_materials_revenue NUMERIC;
BEGIN
    IF NOT EXISTS(SELECT 1 FROM orders WHERE id_order = p_id_order) THEN
        RAISE EXCEPTION 'Заказ с id = % не найден', p_id_order;
    END IF;
    
    -- выручка по работам
    SELECT COALESCE(SUM(ow.price_at_moment * ow.quantity), 0)
    INTO v_work_revenue
    FROM order_work ow
    WHERE ow.id_order = p_id_order;
    
    -- выручка по материалам 
    SELECT COALESCE(SUM(om.price_at_moment * om.quantity), 0)
    INTO v_materials_revenue
    FROM order_material om
    WHERE om.id_order = p_id_order;
    
    total_revenue := v_work_revenue + v_materials_revenue;
    
    -- себестоимость материалов
    SELECT COALESCE(SUM(om.quantity * m.purchase_price), 0)
    INTO v_materials_cost_price
    FROM order_material om
    JOIN material m ON om.id_material = m.id_material
    WHERE om.id_order = p_id_order;
    
    -- себестоимость работ (почасовая ставка мастера 500 руб/час)
    SELECT COALESCE(SUM(wt.labor_hours * ow.quantity * 500), 0)
    INTO v_labor_cost
    FROM order_work ow
    JOIN work_type wt ON ow.id_work_type = wt.id_work_type
    WHERE ow.id_order = p_id_order;
    
    total_cost_price := v_materials_cost_price + v_labor_cost;
    profit := total_revenue - total_cost_price;
    
    IF total_revenue > 0 THEN
        profitability_percent := ROUND((profit / total_revenue) * 100, 2);
    ELSE
        profitability_percent := 0;
    END IF;
END;
$$;

-- хранимая процедура обновления стоимости заказа
CREATE OR REPLACE PROCEDURE update_order_total(
    p_id_order INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    v_new_total NUMERIC;
    v_old_total NUMERIC;
BEGIN
    IF NOT EXISTS(SELECT 1 FROM orders WHERE id_order = p_id_order) THEN
        RAISE EXCEPTION 'Заказ с id = % не найден', p_id_order;
    END IF;
    
    SELECT total_cost INTO v_old_total 
    FROM orders 
    WHERE id_order = p_id_order;
    
    -- расчет новой стоимости
    SELECT COALESCE((
        SELECT SUM(price_at_moment * quantity) 
        FROM order_work 
        WHERE id_order = p_id_order), 0) 
        + COALESCE((
        SELECT SUM(price_at_moment * quantity) 
        FROM order_material 
        WHERE id_order = p_id_order), 0)
    INTO v_new_total;
    
    UPDATE orders 
    SET total_cost = v_new_total
    WHERE id_order = p_id_order;
END;
$$;

-- представление детальной информации о заказах
CREATE OR REPLACE VIEW order_full_info AS
SELECT 
    o.id_order AS "Номер заказа",
    o.accept_date AS "Дата принятия",
    o.completion_date AS "Дата выполнения",
    o.status AS "Статус",
    o.total_cost AS "Стоимость, руб",
    c.last_name || ' ' || c.first_name || COALESCE(' ' || c.middle_name, '') AS "Клиент",
    c.phone AS "Телефон клиента",
    car.brand || ' ' || car.model AS "Автомобиль",
    car.plate_number AS "Госномер",
    car.year AS "Год выпуска",
    car.vin AS "VIN",
    m.last_name || ' ' || m.first_name || COALESCE(' ' || m.middle_name, '') AS "Мастер",
    m.specialization AS "Специализация мастера",
    (
        SELECT COUNT(*) 
        FROM order_work ow 
        WHERE ow.id_order = o.id_order
    ) AS "Кол-во работ",
    (
        SELECT COUNT(*) 
        FROM order_material om 
        WHERE om.id_order = o.id_order
    ) AS "Кол-во материалов"
FROM orders o
JOIN client c ON o.id_client = c.id_client
JOIN car ON o.id_car = car.id_car
LEFT JOIN master_order mo ON o.id_order = mo.id_order
LEFT JOIN master m ON mo.id_master = m.id_master
ORDER BY o.accept_date DESC;

-- представление складочной ведомости материалов 
CREATE OR REPLACE VIEW material_inventory AS
SELECT 
    m.id_material AS "ID",
    m.name AS "Наименование",
    m.unit AS "Ед.изм.",
    m.stock_balance AS "Остаток, шт",
    m.purchase_price AS "Закупочная цена, руб",
    m.sale_price AS "Продажная цена, руб",
    ROUND((m.sale_price - m.purchase_price), 2) AS "Наценка, руб",
    ROUND(((m.sale_price - m.purchase_price) / m.purchase_price * 100), 2) AS "Наценка, %",
    ROUND((m.stock_balance * m.purchase_price), 2) AS "Стоимость остатков (закупка), руб",
    ROUND((m.stock_balance * m.sale_price), 2) AS "Стоимость остатков (продажа), руб",
    (
        SELECT s.supply_date 
        FROM supply s 
        WHERE s.id_material = m.id_material 
        ORDER BY s.supply_date DESC 
        LIMIT 1
    ) AS "Дата последней поставки"
FROM material m
WHERE m.stock_balance > 0 OR m.stock_balance IS NULL
ORDER BY m.name;