import database
import random
import time

def simulate_workload():
    """
    Simulates a heavy workload that triggers full table scans on the users table.
    """
    print("Simulating query workload...")
    database.init_db() # Ensures db exists and is populated
    
    queries_to_test = [
        # Original test query
        f"SELECT * FROM users WHERE age = {random.randint(18, 80)}",
        f"SELECT * FROM users WHERE age = {random.randint(18, 80)}",
        
        # New Query 1: Search by exact email
        f"SELECT * FROM users WHERE email = 'user_{random.randint(1, 99999)}@example.com'",
        
        # New Query 2: Search by username
        f"SELECT username, signup_date FROM users WHERE username = 'user_{random.randint(1, 99999)}_{random.randint(1000, 9999)}'",
        
        # Anti-Pattern 1: Leading Wildcard
        f"SELECT * FROM users WHERE email LIKE '%example.com'",
        
        # Anti-Pattern 2: Negative Condition
        f"SELECT * FROM users WHERE age != 30"
    ]
    
    for query in queries_to_test:
        print(f"Executing: {query}")
        results, exec_time = database.execute_and_log(query)
        print(f"Time taken: {exec_time:.2f} ms")
        print("-" * 30)

if __name__ == "__main__":
    simulate_workload()
    print("Workload generation complete! You can now check the Streamlit dashboard for slow queries.")
