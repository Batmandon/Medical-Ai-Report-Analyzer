import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from config import DATABASE_URL


# ~~~~~~~~~~~~~~~~~~~~~~ DB connection context manager ~~~~~~~~~~~~~~~~~~~~~~~
@contextmanager
def get_cursor():
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cursor:
            yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()    

# Create Tables
def create_database():
    try:
        with psycopg2.connect(DATABASE_URL) as conn:
            with conn.cursor() as cursor:

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS users(
                    id SERIAL PRIMARY KEY,
                    name TEXT,
                    email TEXT UNIQUE,
                    password TEXT
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS files(
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER,
                    filename TEXT,
                    path TEXT
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS summaries(
                    id SERIAL PRIMARY KEY,
                    file_id INTEGER,
                    summary TEXT,
                    tokens_used INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_chunks(
                    id SERIAL PRIMARY KEY,
                    file_id INTEGER,
                    chunk_text TEXT,
                    embedding VECTOR(3072)
                )
                """)

                cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_history(
                    id SERIAL PRIMARY KEY,
                    file_id INTEGER,
                    history JSONB             
                )
                """)
        print("Tables created successfully!")

    except psycopg2.Error as e:
        print("Database Error:", e)