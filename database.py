import psycopg2
from psycopg2 import sql

def connect():
    return psycopg2.connect(
        host="localhost",       # Замените на свой хост
        port="5432",            # Замените на свой порт
        database="bolat_project",      # Замените на имя вашей базы данных
        user="crm_bolat",   # Замените на имя пользователя
        password="root" # Замените на пароль
    )

def insert_sales_data(cabins_count, total_sales, customer_count):
    conn = connect()
    cursor = conn.cursor()
    query = """
        INSERT INTO sales (cabins_count, total_sales, customer_count, date)
        VALUES (%s, %s, %s, CURRENT_DATE)
    """
    
    cursor.execute(query, (cabins_count, total_sales, customer_count))
    conn.commit()
    cursor.close()
    conn.close()


