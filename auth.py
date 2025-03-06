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

def create_user(username, password_hash, role):
    """Создает нового пользователя с хешированным паролем."""
    conn = create_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)",
                       (username, password_hash, role))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при создании пользователя: {e}")
    finally:
        conn.close()


def authenticate(username, password):
    """Проверяет логин и пароль пользователя."""
    conn = create_connection()
    cursor = conn.cursor()

    # Запрашиваем id и хеш пароля из БД
    cursor.execute("SELECT id, password_hash FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, stored_hash = user  # user[0] - это id, user[1] - хэш пароля
        if bcrypt.checkpw(password.encode(), stored_hash.encode()):
            return user_id  # Возвращаем id вместо хэша пароля

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


def get_user_details(user_id):
    """Получает детальную информацию о пользователе"""
    conn = create_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT id, username, role, created_at 
            FROM users 
            WHERE id = %s
        """, (user_id,))
        user = cursor.fetchone()
        
        if user:
            return {
                "id": user[0],
                "username": user[1],
                "role": user[2],
                "created_at": user[3].strftime("%Y-%m-%d %H:%M") if user[3] else "N/A"
            }
        return {}
    except Exception as e:
        print(f"Ошибка при получении данных пользователя: {e}")
        return {}
    finally:
        conn.close()


def delete_user(user_id):
    """Удаляет пользователя по ID"""
    query = "DELETE FROM users WHERE id = %s;"
    
    try:
        conn = create_connection()
        with conn.cursor() as cursor:
            cursor.execute(query, (user_id,))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении пользователя: {e}")
    finally:
        conn.close()
