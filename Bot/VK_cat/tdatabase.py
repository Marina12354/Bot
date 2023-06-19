import psycopg2
# from config import db_name, db_user, db_password, db_host

conn = psycopg2.connect(dbname=db_name, user=db_user, password=db_password, host=db_host)
cursor = conn.cursor()


def create_table_users():
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, vk_id VARCHAR(15) NOT NULL UNIQUE)")
    conn.commit()


def insert_data(vk_user_id_):
    try:
        cursor.execute("INSERT INTO users (vk_id) VALUES (%s)", (vk_user_id_,))
        conn.commit()
        print("Данные добавлены")
    except psycopg2.IntegrityError:
        print("Данные уже существуют")


def select_data():
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()


def drop_data():
    cursor.execute('''DROP table IF EXISTS users ''')
    conn.commit()