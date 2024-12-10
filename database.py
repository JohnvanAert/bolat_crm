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

def insert_sales_data(name, number, cabins_id, total_sales, cabin_price):
    """Функция для добавления новой записи о продажах."""
    try:
        # Устанавливаем соединение с базой данных
        conn = connect()
        cursor = conn.cursor()
        
        # SQL-запрос для вставки данных и получения id новой записи
        query = """
        INSERT INTO sales (name, number, cabins_id, total_sales, date, cabin_price)
        VALUES (%s, %s, %s, %s, NOW()::timestamp(0), %s)
        RETURNING id
        """
        
        # Выполняем запрос
        cursor.execute(query, (name, number, cabins_id, total_sales, cabin_price))
        
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
        cursor.execute("SELECT id, name, number, cabins_id, total_sales, date, cabin_price FROM sales ORDER BY date DESC")
        sales_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return sales_data
    except Exception as e:
        print(f"Ошибка при получении данных о продажах: {e}")
        return []

def update_sales_data(sale_id, new_name, new_number, selected_cabin_id, new_total_sales, new_cabin_price):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE sales
            SET name = %s, number = %s, cabins_id = %s, total_sales = %s, cabin_price = %s
            WHERE id = %s
            """,
            (new_name, new_number, selected_cabin_id, new_total_sales, new_cabin_price, sale_id)
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
        ORDER BY b.booking_date DESC;
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
            start_date
        FROM bookings
        WHERE id = %s AND status = 'Pending';
    """
    insert_sale_query = """
        INSERT INTO sales (name, number, cabins_id, total_sales, date, cabin_price)
        VALUES (%s, %s, %s, %s, NOW(), %s)
        RETURNING id;
    """
    update_booking_status_query = """
        UPDATE bookings
        SET status = 'Confirmed'
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
                    booking[3]   # cabin_price
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
        VALUES (%s, %s, %s, %s, %s, %s, 'Pending')
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
