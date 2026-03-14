import sqlite3
import time
import os

DB_PATH = "ai_optimizer.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Table to store execution logs (our custom pg_stat_statements)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS query_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query_text TEXT,
            execution_time_ms REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sample Application Table: Users
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            email TEXT,
            age INTEGER,
            signup_date DATETIME
        )
    ''')
    
    # Insert dummy data if table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("Populating dummy data. This might take a few seconds...")
        import random
        from datetime import datetime
        
        users_data = []
        for i in range(100000): # 100k rows
            username = f"user_{i}_{random.randint(1000, 9999)}"
            email = f"user_{i}@example.com"
            age = random.randint(18, 80)
            signup_date = datetime.now().isoformat()
            users_data.append((username, email, age, signup_date))
            
        cursor.executemany("INSERT INTO users (username, email, age, signup_date) VALUES (?, ?, ?, ?)", users_data)
        
    conn.commit()
    conn.close()
    
def execute_and_log(query, params=()):
    """
    Executes a query and logs its execution time.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    start_time = time.perf_counter()
    try:
        cursor.execute(query, params)
        results = cursor.fetchall()
    except Exception as e:
        results = None
        print(f"Error executing query: {e}")
    end_time = time.perf_counter()
    
    execution_time_ms = (end_time - start_time) * 1000
    
    # Log the execution
    # We only log SELECTs or specific queries to avoid logging simple inserts repeatedly if not needed
    if query.strip().upper().startswith("SELECT"):
        cursor.execute("INSERT INTO query_logs (query_text, execution_time_ms) VALUES (?, ?)", (query, execution_time_ms))
        conn.commit()
        
    conn.close()
    return results, execution_time_ms

def get_query_plan(query):
    """
    Retrieves the EXPLAIN QUERY PLAN for a given query.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"EXPLAIN QUERY PLAN {query}")
        plan = cursor.fetchall()
    except Exception as e:
        plan = str(e)
        
    conn.close()
    return plan

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully.")
