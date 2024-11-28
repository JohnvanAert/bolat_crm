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

def update_sales_data(sale_id, new_name, new_number, new_cabin_id, new_total_sales, new_cabin_price):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE sales
            SET name = %s, number = %s, cabins_id = %s, total_sales = %s, cabin_price = %s
            WHERE id = %s
            """,
            (new_name, new_number, new_cabin_id, new_total_sales, new_cabin_price, sale_id)
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


def recalculate_cabin_price(cabin_id):
    """Пересчитывает стоимость кабинки на основе связанных продаж."""
    try:
        conn = connect()
        cursor = conn.cursor()

        # Суммируем цены всех товаров, связанных с продажами этой кабинки
        query = """
            SELECT COALESCE(SUM(sp.price * sp.quantity), 0) AS cabin_total_price
            FROM sales_products sp
            JOIN sales s ON sp.sale_id = s.id
            WHERE s.cabins_id = %s;
        """
        cursor.execute(query, (cabin_id,))
        new_cabin_price = cursor.fetchone()[0]

        # Обновляем цену кабинки
        update_query = "UPDATE sales SET cabin_price = %s WHERE id = %s;"
        cursor.execute(update_query, (new_cabin_price, cabin_id))

        conn.commit()
        cursor.close()
        conn.close()

        print(f"Cabin price recalculated: {new_cabin_price}")
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
