import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "database.db")

conn = sqlite3.connect(db_path)

cursor = conn.cursor()

# Prediction History Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS history(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    crop TEXT,
    N REAL,
    P REAL,
    K REAL,
    temperature REAL,
    humidity REAL,
    ph REAL,
    rainfall REAL
)
""")

# Users Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()

print("Database Created Successfully!")