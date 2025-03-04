import psycopg2
from hashlib import sha256
from dotenv import load_dotenv
import os
import bcrypt

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

def create_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )   

def create_user(username, password):
    conn = create_connection()
    cursor = conn.cursor()
    password_hash = sha256(password.encode()).hexdigest()
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)",
        (username, password_hash))
    conn.commit()
    conn.close()

def authenticate(username, password):
    """Проверяет логин и пароль пользователя."""
    conn = create_connection()
    cursor = conn.cursor()

    # Запрашиваем хеш пароля из БД
    cursor.execute("SELECT password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        stored_hash = user[0]  # Достаем хэш из результата запроса
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return username  # Если пароль верный, возвращаем имя пользователя

    return None

def get_users():
    """Получает список всех пользователей"""
    query = "SELECT id, username, role FROM users ORDER BY id;"
    
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute(query)
            users = cursor.fetchall()
        return users
    except Exception as e:
        print(f"Ошибка при получении пользователей: {e}")
        return []
    finally:
        conn.close()


def update_user(user_id, name, role):
    """Обновляет имя и роль пользователя"""
    query = """
        UPDATE users 
        SET username = %s, role = %s
        WHERE id = %s;
    """
    
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, (name, role, user_id))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении пользователя: {e}")
    finally:
        conn.close()
