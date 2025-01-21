import psycopg2
from dotenv import load_dotenv
import os
from datetime import datetime

# Загрузка переменных окружения из файла .env
load_dotenv()

# Получение значений из переменных окружения
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def connect():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

def insert_sales_data(name, number, cabins_id, total_sales, start_date, total_rental_price, end_date):
    """Функция для добавления новой записи о продажах."""
    try:
        # Устанавливаем соединение с базой данных
        conn = connect()
        cursor = conn.cursor()
        
        # SQL-запрос для вставки данных и получения id новой записи
        query = """
        INSERT INTO sales (name, number, cabins_id, total_sales, date, cabin_price, end_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """
        
        # Выполняем запрос
        cursor.execute(query, (name, number, cabins_id, total_sales, start_date, total_rental_price, end_date))
        
        # Получаем id вставленной записи
        sale_id = cursor.fetchone()[0]
        
        # Подтверждаем изменения
        conn.commit()
        
        # Закрываем курсор и соединение
        cursor.close()
        conn.close()
        
        # Возвращаем id
        return sale_id
    except Exception as e:
        # Обрабатываем ошибки и выводим их в консоль
        print(f"Ошибка при вставке данных о продажах: {e}")
        return None

def fetch_sales_data():
    """Функция для получения всех данных о продажах из таблицы."""
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, number, cabins_id, total_sales, date, cabin_price, end_date FROM sales ORDER BY date DESC")
        sales_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return sales_data
    except Exception as e:
        print(f"Ошибка при получении данных о продажах: {e}")
        return []

def update_sales_data(sale_id, new_name, new_number, selected_cabin_id, new_total_sales, new_cabin_price, extension_minutes, service_charge_applied, discount_applied):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE sales
            SET name = %s, number = %s, cabins_id = %s, total_sales = %s, cabin_price = %s, end_date = end_date + %s * INTERVAL '1 minute', service_charge_applied = %s, discount_applied = %s
            WHERE id = %s
            """,
            (new_name, new_number, selected_cabin_id, new_total_sales, new_cabin_price, extension_minutes, service_charge_applied, discount_applied,sale_id)
        )
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении данных о продажах: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def delete_sales(sale_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        # Получаем данные о продуктах, связанных с продажей
        cursor.execute("""
            SELECT product_id, quantity
            FROM sales_products
            WHERE sale_id = %s
        """, (sale_id,))
        products = cursor.fetchall()

        # Восстанавливаем количество продуктов
        for product in products:
            product_id, quantity_sold = product
            cursor.execute("""
                UPDATE products
                SET quantity = quantity + %s
                WHERE id = %s
            """, (quantity_sold, product_id))

        # Удаляем записи из sales_products
        cursor.execute("DELETE FROM sales_products WHERE sale_id = %s", (sale_id,))
        
        # Удаляем запись из sales
        cursor.execute("DELETE FROM sales WHERE id = %s", (sale_id,))

        # Подтверждаем изменения
        conn.commit()
        print("Запись успешно удалена, количество продуктов восстановлено.")
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при удалении записи: {e}")

# Функция для вставки данных о продуктах
def insert_product(name, price, quantity, image_path):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, quantity, image_path) VALUES (%s, %s, %s, %s)",
            (name, price, quantity, image_path)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Ошибка при вставке данных о продуктах:", e)

# Function to update product data
def update_product(product_id, name, price, quantity, image_path):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE products
            SET name = %s, price = %s, quantity = %s, image_path = %s
            WHERE id = %s
            """,
            (name, price, quantity, image_path, product_id)
        )
        conn.commit()
    except Exception as e:
        print("Ошибка при обновлении данных о продукте:", e)
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# Function to delete an expense entry by ID
def delete_product(product_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM products WHERE id = %s", (product_id,))
    conn.commit()
    cur.close()
    conn.close()

# Функция для извлечения данных о продуктах
def fetch_products():
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, price, quantity, image_path FROM products ORDER BY id")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Преобразуем результаты в список словарей
        return [
            {"id": row[0], "name": row[1], "price": row[2], "quantity": row[3], "image_path": row[4]}
            for row in products
        ]
    except Exception as e:
        print("Ошибка при извлечении данных о продуктах:", e)
        return []



# database.py

def get_cabins():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM cabins")
    cabins = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": row[0], "name": row[1], "price": row[2]} for row in cabins]

def add_cabin(name, price):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO cabins (name, price) VALUES (%s, %s)", (name, price))
    conn.commit()
    cursor.close()
    conn.close()

def update_cabin(cabin_id, new_name, new_price):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE cabins SET name = %s, price = %s WHERE id = %s", (new_name, new_price, cabin_id))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении кабинки: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def delete_cabin(cabin_id):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM cabins WHERE id = %s", (cabin_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении кабинки: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


# Function to fetch expenses data with optional filters
def fetch_expenses_data(name=None, min_amount=None, max_amount=None, start_date=None, end_date=None):
    query = "SELECT id, name, amount, date FROM expenses WHERE 1=1"
    params = []

    if name:
        query += " AND name ILIKE %s"
        params.append(f"%{name}%")
    if min_amount:
        query += " AND amount >= %s"
        params.append(min_amount)
    if max_amount:
        query += " AND amount <= %s"
        params.append(max_amount)
    if start_date:
        query += " AND date >= %s"
        params.append(start_date)
    if end_date:
        query += " AND date <= %s"
        params.append(end_date)

    conn = connect()
    cur = conn.cursor()
    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# Function to add an expense entry
def add_expense(name, amount, date=None):
    if not date:
        date = datetime.now()  # Получаем текущую дату и время

    conn = connect()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO expenses (name, amount, date) VALUES (%s, %s, %s)",
        (name, amount, date)
    )
    conn.commit()
    cur.close()
    conn.close()


def update_expense(expense_id, new_name, new_amount, new_date):
    try:
        conn = connect()
        cursor = conn.cursor()
        
        # SQL-запрос для обновления записи
        query = """
        UPDATE expenses
        SET name = %s, amount = %s, date = %s
        WHERE id = %s
        """
        
        # Выполнение запроса с новыми данными
        cursor.execute(query, (new_name, new_amount, new_date, expense_id))
        conn.commit()
        
        print("Запись успешно обновлена.")
    except Exception as e:
        print(f"Ошибка при обновлении записи: {e}")
    finally:
        cursor.close()
        conn.close()

# Function to delete an expense entry by ID
def remove_expense(expense_id):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = %s", (expense_id,))
    conn.commit()
    cur.close()
    conn.close()


# Function to insert an expense
def insert_expense(expense_name, expense_amount, expense_date=None):
    if expense_date is None:
        expense_date = datetime.now()  # Default to current date and time

    try:
        connection = connect()
        cursor = connection.cursor()

        # Insert expense data into the expenses table
        cursor.execute(
            """
            INSERT INTO expenses (name, amount, date)
            VALUES (%s, %s, %s)
            """,
            (expense_name, expense_amount, expense_date)
        )
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        print("Error inserting expense:", e)


def update_product_stock(product_id, quantity_sold):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET quantity = quantity - %s WHERE id = %s AND quantity >= %s",
            (quantity_sold, product_id, quantity_sold)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Ошибка при обновлении количества продукта:", e)

def insert_order_product(sale_id, product_id, quantity, price):
    conn = connect()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO sales_products (sale_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
                (sale_id, product_id, quantity, price)
            )
    conn.close()

def get_products_for_sale(sale_id):
    try:
        conn = connect()
        cursor = conn.cursor()
        query = """
        SELECT p.id, p.name, sp.quantity, sp.price
        FROM sales_products sp
        JOIN products p ON sp.product_id = p.id
        WHERE sp.sale_id = %s
        """
        cursor.execute(query, (sale_id,))
        results = cursor.fetchall()
        cursor.close()
        conn.close()

        # Преобразуем результаты в список словарей
        return [{"id": row[0], "name": row[1], "quantity": row[2], "price": row[3]} for row in results]
    except Exception as e:
        print(f"Ошибка при получении товаров для продажи: {e}")
        return []

def update_product_quantity(sale_id, product_id, new_quantity):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE sales_products
            SET quantity = %s
            WHERE sale_id = %s AND product_id = %s
            """,
            (new_quantity, sale_id, product_id)
        )
        conn.commit()
    except psycopg2.Error as e:
        conn.rollback()
        print(f"Database error: {e}")
    finally:
        cursor.close()
        conn.close()


def delete_product_from_sale(sale_id, product_id):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM sales_products WHERE sale_id = %s AND product_id = %s",
        (sale_id, product_id)
    )
    conn.commit()
    conn.close()


def get_cabin_data():
    conn = connect()
    cursor = conn.cursor()
    query = """
        SELECT id, cabins_id, total_sales, customer_count, date
        FROM sales
        """
    cursor.execute(query)


def get_cabin_info_from_sale(sale_id):
    """Получает ID кабинки и её текущую стоимость (cabin_price), связанную с записью."""
    try:
        conn = connect()
        cursor = conn.cursor()

        query = """
            SELECT cabins_id, cabin_price
            FROM sales
            WHERE id = %s;
        """
        cursor.execute(query, (sale_id,))
        result = cursor.fetchone()

        cursor.close()
        conn.close()

        if result:
            cabin_id, cabin_price = result
            return cabin_id, cabin_price
        else:
            return None, None  # Если запись не найдена
    except Exception as e:
        print(f"Ошибка при получении информации о кабинке: {e}")
        return None, None


def recalculate_cabin_price(sale_id):
    """Пересчитывает стоимость кабинки на основе конкретной продажи."""
    try:
        conn = connect()
        cursor = conn.cursor()

        # Получаем ID кабинки, связанной с данной продажей
        query_cabin = "SELECT cabins_id FROM sales WHERE id = %s;"
        cursor.execute(query_cabin, (sale_id,))
        cabin_id = cursor.fetchone()
        if not cabin_id:
            print(f"Продажа с ID {sale_id} не найдена.")
            return
        cabin_id = cabin_id[0]

        # Суммируем стоимость товаров, связанных с конкретной продажей
        query = """
            SELECT COALESCE(SUM(sp.price * sp.quantity), 0) AS sale_total_price
            FROM sales_products sp
            WHERE sp.sale_id = %s;
        """
        cursor.execute(query, (sale_id,))
        new_cabin_price = cursor.fetchone()[0]

        # Обновляем cabin_price только для текущей записи продажи
        update_query = """
            UPDATE sales SET cabin_price = %s WHERE id = %s;
        """
        cursor.execute(update_query, (new_cabin_price, sale_id))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Cabin price recalculated for sale {sale_id}: {new_cabin_price}")
    except Exception as e:
        print(f"Ошибка при пересчете стоимости кабинки: {e}")


def get_products_data_for_sale(sale_id):
    """
    Получает данные о продуктах, связанных с конкретной продажей.
    Возвращает список словарей с `product_id`, `price`, `quantity`.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = """
            SELECT p.id AS product_id, sp.price, sp.quantity
            FROM sales_products sp
            JOIN products p ON sp.product_id = p.id
            WHERE sp.sale_id = %s;
        """
        cursor.execute(query, (sale_id,))
        products = [
            {"product_id": row[0], "price": row[1], "quantity": row[2]} for row in cursor.fetchall()
        ]
        cursor.close()
        conn.close()
        return products
    except Exception as e:
        print(f"Ошибка при получении данных о продуктах для продажи {sale_id}: {e}")
        return []


def update_total_sales(sale_id, total_price):
    """
    Обновляет общую сумму продажи в таблице sales.
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        query = "UPDATE sales SET total_sales = %s WHERE id = %s;"
        cursor.execute(query, (total_price, sale_id))
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Обновлена общая сумма продажи {sale_id}: {total_price}")
    except Exception as e:
        print(f"Ошибка при обновлении общей суммы продажи {sale_id}: {e}")


# Product adding function

def get_all_products():
    """
    Получить список всех продуктов из таблицы products.
    Возвращает список словарей с полями: id, name, price, quantity.
    """
    query = """
        SELECT id, name, price, quantity 
        FROM products
        WHERE quantity > 0
        ORDER BY name;
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            # Преобразуем результат в список словарей
            products = [
                {"id": row[0], "name": row[1], "price": row[2], "quantity": row[3]}
                for row in rows
            ]
        conn.close()
        return products
    except Exception as e:
        print(f"Ошибка получения продуктов: {e}")
        return []

def add_product_to_sale(sale_id, product_id, quantity, product_price):
    """
    Добавить продукт в продажу. Если продукт уже существует, обновить количество.
    """
    query_insert = """
        INSERT INTO sales_products (sale_id, product_id, quantity, price)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (sale_id, product_id)
        DO UPDATE SET quantity = sales_products.quantity + EXCLUDED.quantity;
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query_insert, (sale_id, product_id, quantity, product_price))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка добавления продукта в продажу: {e}")


def update_sale_total_price(sale_id, product_price):
    """
    Обновить общую стоимость продажи, добавив стоимость нового продукта.
    """
    query = """
        UPDATE sales
        SET total_sales = total_sales + %s
        WHERE id = %s;
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (product_price, sale_id))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Ошибка обновления общей стоимости продажи: {e}")


def fetch_all_bookings():
    """Получает все бронирования из базы данных."""
    query = """
        SELECT 
            b.id, 
            b.customer_name, 
            b.customer_phone, 
            b.cabin_id, 
            c.name AS cabin_name,
            b.booking_date, 
            b.start_date, 
            b.end_date, 
            b.total_price, 
            b.status
        FROM bookings b
        LEFT JOIN cabins c ON b.cabin_id = c.id
        ORDER BY b.booking_date ASC;
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()
    except Exception as e:
        print("Ошибка при получении бронирований:", e)
        return []
    finally:
        conn.close()


def confirm_booking_to_sale(booking_id):
    """Подтверждает бронирование и создает продажу."""
    fetch_booking_query = """
        SELECT 
            customer_name, 
            customer_phone, 
            cabin_id, 
            total_price, 
            start_date,
            end_date
        FROM bookings
        WHERE id = %s AND status = 'Ожидание';
    """
    insert_sale_query = """
        INSERT INTO sales (name, number, cabins_id, total_sales, date, cabin_price, end_date)
        VALUES (%s, %s, %s, %s, NOW()::timestamp(0), %s, %s)
        RETURNING id;
    """
    update_booking_status_query = """
        UPDATE bookings
        SET status = 'Подтверждено'
        WHERE id = %s;
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            # Получаем данные бронирования
            cursor.execute(fetch_booking_query, (booking_id,))
            booking = cursor.fetchone()
            if not booking:
                raise ValueError("Бронирование не найдено или уже подтверждено.")
            
            # Добавляем продажу
            cursor.execute(
                insert_sale_query, 
                (
                    booking[0],  # customer_name
                    booking[1],  # customer_phone
                    booking[2],  # cabin_id
                    booking[3],  # total_price
                    booking[3],   # cabin_price
                    booking[5]   # end_date
                )
            )
            sale_id = cursor.fetchone()[0]

            # Обновляем статус бронирования
            cursor.execute(update_booking_status_query, (booking_id,))
            conn.commit()
            return sale_id
    except Exception as e:
        conn.rollback()
        print("Ошибка при подтверждении бронирования:", e)
        return None
    finally:
        conn.close()


def update_booking_status(booking_id, new_status):
    """Обновляет статус бронирования."""
    query = """
        UPDATE bookings
        SET status = %s
        WHERE id = %s;
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (new_status, booking_id))
            conn.commit()
            return cursor.rowcount  # Возвращает количество обновленных строк
    except Exception as e:
        conn.rollback()
        print("Ошибка при обновлении статуса бронирования:", e)
        return 0
    finally:
        conn.close()


def add_booking(customer_name, customer_phone, cabin_id, start_date, end_date, total_price):
    """Добавляет новое бронирование."""
    query = """
        INSERT INTO bookings (customer_name, customer_phone, cabin_id, start_date, end_date, total_price, status)
        VALUES (%s, %s, %s, %s, %s, %s, 'Ожидание')
        RETURNING id;
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (customer_name, customer_phone, cabin_id, start_date, end_date, total_price))
            booking_id = cursor.fetchone()[0]
            conn.commit()
            return booking_id
    except Exception as e:
        conn.rollback()
        print("Ошибка при добавлении бронирования:", e)
        return None
    finally:
        conn.close()

def get_cabin_price(cabin_id):
    """Получает цену кабины по ID."""
    query = "SELECT price FROM cabins WHERE id = %s;"
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (cabin_id,))
            result = cursor.fetchone()
            if result:
                return result[0]
            else:
                return None  # Если кабина с таким ID не найдена
    except Exception as e:
        print("Ошибка при получении цены кабины:", e)
        return None
    finally:
        conn.close()

def check_booking_conflict(cabin_id, start_date, end_date):
    """Проверяет пересечение бронирования для выбранной кабины."""
    query = """
        SELECT COUNT(*)
        FROM bookings
        WHERE cabin_id = %s 
          AND (start_date < %s AND end_date > %s)
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (cabin_id, end_date, start_date))
            result = cursor.fetchone()
            return result[0] > 0  # True, если есть пересечение
    except Exception as e:
        print("Ошибка при проверке конфликта бронирования:", e)
        return True
    finally:
        conn.close()

def fetch_filtered_bookings(name, date, status, cabin, limit, page):
    offset = (page - 1) * limit

    # Если cabin пустой, передаем None
    cabin_id = int(cabin) if cabin else None

    query = """
        SELECT * FROM bookings
        WHERE (%s = '' OR customer_name ILIKE %s)
          AND (%s = '' OR booking_date::text LIKE %s)
          AND (%s = 'Все' OR status = %s)
          AND (%s IS NULL OR cabin_id = %s)
        ORDER BY booking_date DESC
        LIMIT %s OFFSET %s
    """
    params = (name, f"%{name}%", date, f"%{date}%", status, status, cabin_id, cabin_id, limit, offset)

    with connect() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            rows = cursor.fetchall()

            # Подсчет общего количества записей с учетом фильтров
            count_query = """
                SELECT COUNT(*)
                FROM bookings
                WHERE (%s = '' OR customer_name ILIKE %s)
                  AND (%s = '' OR booking_date::text LIKE %s)
                  AND (%s = 'Все' OR status = %s)
                  AND (%s IS NULL OR cabin_id = %s)
            """
            cursor.execute(count_query, params[:-2])  # Исключаем limit и offset
            total_count = cursor.fetchone()[0]

    return rows, total_count


def is_cabin_busy(cabin_id, current_time):
    """
    Проверяет, занята ли кабина на момент времени current_time.
    Возвращает True, если кабина занята, иначе False.
    """
    query = """
        SELECT COUNT(*) 
        FROM sales 
        WHERE cabins_id = %s AND end_date > %s
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (cabin_id, current_time))
            result = cursor.fetchone()
            return result[0] > 0  # Если есть записи, значит кабина занята
    finally:
        if conn:
            conn.close()

def get_cabin_statuses():
    query = """
        SELECT 
            c.id,
            c.name,
            CASE 
                WHEN EXISTS (
                    SELECT 1 
                    FROM sales s
                    WHERE s.cabins_id = c.id 
                      AND CURRENT_TIMESTAMP BETWEEN s.date AND s.end_date
                ) THEN TRUE
                ELSE FALSE
            END AS is_occupied
        FROM cabins c
        LEFT JOIN sales s ON c.id = s.cabins_id
        GROUP BY c.id, c.name;
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchall()
        statuses = [{"id": row[0], "name": row[1], "is_occupied": row[2]} for row in result]
        cursor.close()
        conn.close()
        return statuses
    except Exception as e:
        print(f"Ошибка при получении статуса кабинок: {e}")
        return []
    
def get_cabin_status_from_sales(cabin_id):
    query = """
        SELECT COUNT(*) 
        FROM sales 
        WHERE cabins_id = %s AND date <= NOW() AND (end_date IS NULL OR end_date >= NOW())
    """
    conn = connect()
    cursor = conn.cursor()
    result = cursor.execute(query, (cabin_id,))
    return "Занята" if result[0][0] > 0 else "Свободна"

def add_rental_extension(order_id, extended_minutes):
    """
    Добавляет запись о продлении времени аренды в таблицу rental_extensions.
    """
    query = """
        INSERT INTO rental_extensions (sale_id, extended_minutes, timestamp)
        VALUES (%s, %s, NOW())
    """
    try:
        conn = connect()
        with conn.cursor() as cursor:
            cursor.execute(query, (order_id, extended_minutes))
        conn.commit()
        conn.close()
    except Exception as e:
        raise RuntimeError(f"Ошибка при добавлении данных о продлении времени: {e}")

def get_extensions_for_sale(sale_id):
    """Получить данные о продлениях для текущей продажи."""
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT extension_id, extended_minutes, timestamp FROM rental_extensions WHERE sale_id = %s"
    cursor.execute(query, (sale_id,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_cabin_statistics(period):
    """Функция для получения статистики по кабинкам за определенный период."""
    try:
        conn = connect()  # Соединение с БД
        cursor = conn.cursor()

        # SQL-запрос с параметризованным периодом
        query = f"""
        SELECT
            c.id AS cabin_id,
            c.name AS cabin_name,
            COUNT(s.id) AS rental_count,
            SUM(s.total_sales) AS total_profit,
            AVG(s.total_sales) AS average_check
        FROM
            cabins c
        LEFT JOIN
            sales s ON c.id = s.cabins_id
        WHERE
            s.date >= NOW() - INTERVAL '1 {period}'
        GROUP BY
            c.id, c.name
        ORDER BY
            rental_count DESC
        """
        cursor.execute(query)
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return []

def get_total_income(period):
    """Получает общий доход за указанный период."""
    query = f"""
    SELECT SUM(total_sales)
    FROM sales
    WHERE date >= NOW() - INTERVAL '1 {period}';
    """
    return fetch_single_value(query)


def get_total_expenses(period):
    """Получает общие расходы за указанный период."""
    query = f"""
    SELECT SUM(amount)
    FROM expenses
    WHERE date >= NOW() - INTERVAL '1 {period}';
    """
    return fetch_single_value(query)

def fetch_single_value(query):
    """Выполняет запрос и возвращает единственное значение."""
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(query)
        result = cursor.fetchone()[0] or 0.0  # Если None, возвращаем 0.0
        return result
    except Exception as e:
        print(f"Ошибка при выполнении запроса: {e}")
        return 0.0
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_cabin_statistics_by_date_range(start_date, end_date):
    """Получает статистику по кабинам за указанный диапазон дат."""
    query = """
    SELECT 
        c.id AS cabin_id,
        c.name AS cabin_name,
        COUNT(s.id) AS rentals_count,
        COALESCE(SUM(s.total_sales), 0) AS total_income,
        CASE 
            WHEN COUNT(s.id) > 0 THEN ROUND(COALESCE(SUM(s.total_sales), 0) / COUNT(s.id), 2) 
            ELSE 0 
        END AS avg_check
    FROM cabins c
    LEFT JOIN sales s ON c.id = s.cabins_id AND s.date BETWEEN %s AND %s
    GROUP BY c.id, c.name
    HAVING
    COUNT(s.id) > 0 OR SUM(s.total_sales) > 0
    ORDER BY rentals_count DESC;
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        return result
    except Exception as e:
        print(f"Ошибка при выполнении запроса get_cabin_statistics_by_date_range: {e}")
        return []

def get_total_income_by_date_range(start_date, end_date):
    """
    Получает общий доход за указанный диапазон дат.
    """
    query = """
        SELECT COALESCE(SUM(total_sales), 0)
        FROM sales
        WHERE date BETWEEN %s AND %s
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    except Exception as e:
        print(f"Ошибка при выполнении запроса get_total_income_by_date_range: {e}")
        return 0.0

def get_total_expenses_by_date_range(start_date, end_date):
    """
    Получает общие расходы за указанный диапазон дат.
    """
    query = """
        SELECT COALESCE(SUM(amount), 0)
        FROM expenses
        WHERE date BETWEEN %s AND %s
    """
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(query, (start_date, end_date))
        result = cursor.fetchone()[0]
        return float(result) if result else 0.0
    except Exception as e:
        print(f"Ошибка при выполнении запроса get_total_expenses_by_date_range: {e}")
        return 0.0


def fetch_statistics(start_date, end_date):
    """
    Функция для получения статистики за указанный диапазон дат.
    """
    # Пример SQL-запроса
    query = f"""
    SELECT * FROM statistics
    WHERE date >= '{start_date}' AND date <= '{end_date}'
    """
    # Выполнение запроса и получение данных
    # Например: cursor.execute(query) ...
    return query  # или результат данных


def fetch_products_from_db():
    """Получение списка продуктов из базы данных."""
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, name, price, quantity FROM products")
            return cursor.fetchall()
    finally:
        connection.close()


def decrease_product_stock(product_id, quantity):
    """Уменьшение количества продукта на складе."""
    connection = connect()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE products SET quantity = quantity - %s WHERE id = %s AND quantity >= %s",
                (quantity, product_id, quantity)
            )
            if cursor.rowcount == 0:
                raise ValueError("Недостаточно товара на складе")
        connection.commit()
    finally:
        connection.close()

def increase_product_stock(product_id, quantity):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute(
        "UPDATE products SET quantity = quantity + %s WHERE id = %s",
        (quantity, product_id)
    )
    connection.commit()
    cursor.close()
    connection.close()

def update_product_stocks(product_id, new_quantity):
    connection = connect()
    cursor = connection.cursor()
    """
    Обновляет количество доступного продукта в базе данных.
    """
    query = "UPDATE products SET quantity = %s WHERE id = %s"
    cursor.execute(query, (new_quantity, product_id))
    connection.commit()
    connection.close()


def get_product_stock(product_id):
    """Получает текущее количество товара на складе."""
    connection = connect()
    cursor = connection.cursor()
    query = "SELECT quantity FROM products WHERE id = %s"
    cursor.execute(query, (product_id,))
    result = cursor.fetchone()
    connection.close()

    if result:
        return result[0]
    else:
        return 0  # Если товара нет, возвращаем 0

def get_available_quantity(product_id):
    try:
        # Установите соединение с базой данных PostgreSQL
        connection = connect()
        cursor = connection.cursor()
        # Выполните запрос
        query = "SELECT quantity FROM products WHERE id = %s;"
        cursor.execute(query, (product_id,))
        result = cursor.fetchone()
        
        # Возвратите результат
        return result[0] if result else 0
    except Exception as e:
        print(f"Ошибка: {e}")
        return 0
    finally:
        if connection:
            cursor.close()
            connection.close()


def fetch_rental_data():
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, number, cabins_id, total_sales, date, cabin_price, end_date FROM sales ORDER BY date DESC")
    rows = cursor.fetchall()
    connection.close()
    return [
        {"id": row[0], "name": row[1], "number": row[2], "cabins_id": row[3],
         "total_sales": row[4], "date": row[5], "cabin_price": row[6], "end_date": row[7]}
        for row in rows
    ]

def get_service_state(sale_id):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT service_charge_applied FROM sales WHERE id = %s", (sale_id,))
    result = cursor.fetchone()
    return result[0] if result else False

def get_discount_state(sale_id):
    connection = connect()
    cursor = connection.cursor()
    cursor.execute("SELECT discount_applied FROM sales WHERE id = %s", (sale_id,))
    result = cursor.fetchone()
    return result[0] if result else False


def fetch_rental_cost(rental_id):
    try:
        connection = connect()  # Функция для подключения к базе данных
        cursor = connection.cursor()
        query = """
            SELECT cabin_price
            FROM sales
            WHERE id = %s;
        """
        cursor.execute(query, (rental_id,))
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        return result[0] if result else None
    except Exception as e:
        print(f"Ошибка при получении суммы аренды: {e}")
        return None
