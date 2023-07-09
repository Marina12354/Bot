import psycopg2
from config import db_name, db_user, db_password, db_host

conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
cursor = conn.cursor()


def create_table_users():
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (vk_user_owner VARCHAR(20), vk_user_finded VARCHAR(20) NOT NULL UNIQUE)")
    conn.commit()

def insert_data(vk_user_owner_id, vk_user_finded_id):
    try:
        cursor.execute("INSERT INTO users (vk_user_owner, vk_user_finded) VALUES (%s, %s)", (vk_user_owner_id, vk_user_finded_id,))
        conn.commit()
        print("Данные добавлены")
    except psycopg2.IntegrityError:
        print("Данные уже существуют")

def find_data(vk_user_owner_id):
    result = []
    cursor.execute("SELECT * FROM users")
    for person in cursor.fetchall():
        if vk_user_owner_id == int(person[0]):
            result.append(person[1])
    return result

def select_data():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

def drop_data():
    cursor.execute('''DROP table IF EXISTS users ''')
    conn.commit()