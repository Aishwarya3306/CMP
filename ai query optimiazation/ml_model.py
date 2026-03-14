import psycopg2
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

# Connect to PostgreSQL
conn = psycopg2.connect(
    dbname="ai_query_optimiazation",
    user="postgres",
    password="Aish1311",
    host="localhost",
    port="5432"
)

# Load query_logs table
query = """
SELECT execution_time_ms, scan_type, optimization_applied
FROM query_logs;
"""

df = pd.read_sql(query, conn)
conn.close()

print("Total rows loaded:", len(df))

# Remove missing values (if any)
df = df.dropna()

print("After cleaning:", len(df))

# Convert scan_type to numeric
# Sequential Scan = 1 (bad)
# Index Scan = 0 (good)

df["scan_type"] = df["scan_type"].apply(
    lambda x: 1 if "Sequential" in x else 0
)

# Features and target
X = df[["execution_time_ms", "scan_type"]]
y = df["optimization_applied"]

# Stratified split (important)
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.3,
    stratify=y,
    random_state=42
)

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Predict
predictions = model.predict(X_test)

# Evaluate
accuracy = accuracy_score(y_test, predictions)

print("\nModel Accuracy:", round(accuracy * 100, 2), "%")
print("\nClassification Report:\n")
print(classification_report(y_test, predictions))

# -------- TEST ON NEW QUERY --------

print("\n--- Testing ML Model on New Query ---")

# Example: simulate a new query execution
new_execution_time = 6.3   # example value (ms)
new_scan_type = 0          # 1 = Sequential Scan, 0 = Index Scan

new_data = pd.DataFrame({
    "execution_time_ms": [new_execution_time],
    "scan_type": [new_scan_type]
})

prediction = model.predict(new_data)

print("Input Features:")
print("Execution Time:", new_execution_time)
print("Scan Type:", "Sequential Scan" if new_scan_type == 1 else "Index Scan")

print("\nML Prediction:")
if prediction[0]:
    print("Optimization needed: TRUE")
else:
    print("Optimization needed: FALSE")