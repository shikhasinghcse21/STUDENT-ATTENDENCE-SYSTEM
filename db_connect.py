import mysql.connector

def get_connection():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="123456",
            database="teacher_db"
        )
        return conn
    except Exception as e:
        print("Database connection failed:", e)
        return None
