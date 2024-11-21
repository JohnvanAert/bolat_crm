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

def insert_sales_data(name, number, cabins_count, total_sales):
    """Функция для добавления новой записи о продажах."""
    try:
        # Устанавливаем соединение с базой данных
        conn = connect()
        cursor = conn.cursor()
        
        # SQL-запрос для вставки данных и получения id новой записи
        query = """
        INSERT INTO sales (name, number, cabins_count, total_sales, date)
        VALUES (%s, %s, %s, %s, NOW()::timestamp(0))
        RETURNING id
        """
        
        # Выполняем запрос
        cursor.execute(query, (name, number, cabins_count, total_sales))
        
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
        cursor.execute("SELECT id, name, number, cabins_count, total_sales, date FROM sales ORDER BY date DESC")
        sales_data = cursor.fetchall()
        cursor.close()
        conn.close()
        return sales_data
    except Exception as e:
        print(f"Ошибка при получении данных о продажах: {e}")
        return []

def update_sales_data(sale_id, new_name, new_number, new_cabin_id, new_total_sales):
    conn = connect()
    cursor = conn.cursor()
    try:
        cursor.execute(
            """
            UPDATE sales
            SET name = %s, number = %s, cabins_count = %s, total_sales = %s
            WHERE id = %s
            """,
            (new_name, new_number, new_cabin_id, new_total_sales, sale_id)
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
    
def get_products_data():
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT id, name FROM products"
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    conn.close()
    return [{"id": row[0], "name": row[1]} for row in results]

def get_product_price(product_id):
    conn = connect()
    cursor = conn.cursor()
    query = "SELECT price FROM products WHERE id = %s"
    cursor.execute(query, (product_id,))
    price = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return price

def update_products_for_sale(sale_id, products):
    conn = connect()
    cursor = conn.cursor()

    # Удаляем старые товары
    delete_query = "DELETE FROM sales_products WHERE sale_id = %s"
    cursor.execute(delete_query, (sale_id,))

    # Добавляем новые товары
    insert_query = "INSERT INTO sales_products (sale_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)"
    for product in products:
        cursor.execute(insert_query, (sale_id, product["id"], product["quantity"], product["price"]))

    conn.commit()
    cursor.close()
    conn.close()


def get_all_products():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, price FROM products")
    products = [{"id": row[0], "name": row[1], "price": row[2]} for row in cursor.fetchall()]
    conn.close()
    return products


def update_product_quantity(sale_id, product_id, quantity):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE sales_products SET quantity = %s WHERE sale_id = %s AND product_id = %s",
        (quantity, sale_id, product_id)
    )
    conn.commit()
    conn.close()


def add_product_to_sale(sale_id, product_id, quantity, price):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO sales_products (sale_id, product_id, quantity, price) VALUES (%s, %s, %s, %s)",
        (sale_id, product_id, quantity, price)
    )
    conn.commit()
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


def refresh_products_tree(tree, sale_id):
    for item in tree.get_children():
        tree.delete(item)

    products = get_products_for_sale(sale_id)
    for product in products:
        tree.insert("", "end", values=(product['id'], product['name'], product['quantity'], product['price']))
