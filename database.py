import sqlite3
import os

# Шлях до бази (у тій самій папці)
DB_PATH = os.path.join(os.path.dirname(__file__), "farmers.db")

def init_db():
    """Створює таблицю, якщо її ще немає."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS farmers (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            city TEXT,
            crops TEXT
        )
    ''')
    conn.commit()
    conn.close()

def save_farmer(user_id, username=None, first_name=None, city=None, crops=None):
    """
    Зберігає або оновлює дані фермера.
    Оновлює тільки ті поля, які не None.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Створюємо запис, якщо його ще немає
    cursor.execute('''
        INSERT OR IGNORE INTO farmers (user_id, username, first_name, city, crops)
        VALUES (?, ?, ?, ?, ?)
    ''', (user_id, username, first_name, city, crops))
    
    # Підготовка оновлення лише для непорожніх значень
    updates = []
    params = []
    
    if username is not None:
        updates.append("username = ?")
        params.append(username)
    if first_name is not None:
        updates.append("first_name = ?")
        params.append(first_name)
    if city is not None:
        updates.append("city = ?")
        params.append(city)
    if crops is not None:
        updates.append("crops = ?")
        params.append(crops)
    
    # Виконуємо UPDATE, якщо є що оновлювати
    if updates:
        params.append(user_id)
        query = f"UPDATE farmers SET {', '.join(updates)} WHERE user_id = ?"
        cursor.execute(query, params)
    
    conn.commit()
    conn.close()

def get_farmer(user_id):
    """Повертає дані фермера за ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT city, crops FROM farmers WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    conn.close()
    return row  # (city, crops) або None