import psycopg2
from dotenv import load_dotenv
import os

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
        conn = connect()
        cursor = conn.cursor()
        query = """
        INSERT INTO sales (name, number, cabins_count, total_sales, date)
        VALUES (%s, %s, %s, %s, NOW())
        """
        cursor.execute(query, (name, number, cabins_count, total_sales))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Ошибка при вставке данных о продажах: {e}")

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
    
# Функция для вставки данных о продуктах
def insert_product(name, price, quantity):
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO products (name, price, quantity) VALUES (%s, %s, %s)",
            (name, price, quantity)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print("Ошибка при вставке данных о продуктах:", e)

# Функция для извлечения данных о продуктах
def fetch_products():
    try:
        conn = connect()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM products ORDER BY id")
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        return products
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

def update_cabin(cabin_id, new_price):
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("UPDATE cabins SET price = %s WHERE id = %s", (new_price, cabin_id))
    conn.commit()
    cursor.close()
    conn.close()
