from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import database
import re
from typing import List, Optional

app = FastAPI(title="AI DB Query Optimizer")

class HealRequest(BaseModel):
    sql_command: str

@app.get("/api/slow_queries")
def get_slow_queries(limit: int = 50):
    """
    Simulates pg_stat_statements. Fetches queries with high execution times.
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT query_text, AVG(execution_time_ms) as avg_time, COUNT(*) as exec_count 
        FROM query_logs 
        GROUP BY query_text 
        ORDER BY avg_time DESC 
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [{"query": row[0], "avg_time_ms": round(row[1], 2), "count": row[2]} for row in results]

@app.post("/api/analyze")
def analyze_query(query: str):
    """
    The "AI Engine". Analyzes a query and its execution plan and returns recommendations.
    """
    plan_rows = database.get_query_plan(query)
    
    # We will build a simple heuristic AI analysis
    # SQLite EXPLAIN QUERY PLAN format often looks like: 
    # (id, parent, notused, detail) -> e.g., (2, 0, 0, 'SCAN TABLE users')
    
    plan_details = [row[3] for row in plan_rows] if isinstance(plan_rows, list) else []
    
    recommendation = None
    bottleneck = "No major issues detected."
    
    for detail in plan_details:
        if "SCAN TABLE" in detail:
            bottleneck = "Full table scan detected."
            # Attempt to extract table name
            match = re.search(r"SCAN TABLE (\w+)", detail)
            if match:
                table_name = match.group(1)
                
                # [NEW FEATURE] Anti-Pattern 1: Leading Wildcard
                wildcard_match = re.search(r"(\w+)\s+LIKE\s+'%([^']+)'", query, re.IGNORECASE)
                if wildcard_match:
                    col = wildcard_match.group(1)
                    val = wildcard_match.group(2)
                    recommendation = {
                        "type": "Query Rewrite (Anti-Pattern)",
                        "sql": query.replace(f"LIKE '%{val}'", f"LIKE '{val}%'"),
                        "description": f"Leading wildcards (`LIKE '%text'`) prevent the database from using indexes. If possible, rewrite to trailing wildcards (`LIKE 'text%'`) or use Full Text Search."
                    }
                    bottleneck = "Anti-Pattern: Leading Wildcard prevents index usage."
                    break

                # [NEW FEATURE] Anti-Pattern 2: Negative Conditions (!= or <>)
                neg_match = re.search(r"(\w+)\s*(!=|<>)\s*([^ ]+)", query, re.IGNORECASE)
                if neg_match:
                    col = neg_match.group(1)
                    val = neg_match.group(3)
                    recommendation = {
                        "type": "Query Rewrite (Anti-Pattern)",
                        "sql": query.replace(neg_match.group(0), f"{col} > {val} OR {col} < {val}"), # Simplistic rewrite suggestion
                        "description": f"Negative conditions (`!=` or `<>`) often cause full table scans. Consider rewriting using positive ranges (`>` and `<`) if applicable."
                    }
                    bottleneck = "Anti-Pattern: Negative condition prevents index usage."
                    break
                
                # Try to extract the WHERE column from the query to suggest an index
                # This is a basic NLP heuristic for our academic AI engine
                where_match = re.search(r"WHERE\s+(\w+)\s*[=><]", query, re.IGNORECASE)
                if where_match:
                    column = where_match.group(1)
                    suggestion = f"CREATE INDEX idx_{table_name}_{column} ON {table_name}({column});"
                    recommendation = {
                        "type": "Missing Index",
                        "sql": suggestion,
                        "description": f"Creating an index on {table_name}.{column} will prevent full table scans and speed up queries matching this column."
                    }
                else:
                    recommendation = {
                        "type": "Optimize Query",
                        "sql": None,
                        "description": f"The query performs a full scan on {table_name}. Consider adding a WHERE clause filtering on indexed columns to improve performance."
                    }
                    
    return {
        "query": query,
        "plan": plan_details,
        "bottleneck": bottleneck,
        "recommendation": recommendation
    }

@app.post("/api/heal")
def apply_healing(request: HealRequest):
    """
    The Self-Healing Agent. Automatically applies the recommended fix (like creating an index).
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(request.sql_command)
        conn.commit()
        success = True
        msg = "Optimization applied successfully!"
    except Exception as e:
        success = False
        msg = f"Error applying optimization: {e}"
    finally:
        conn.close()
        
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {"status": "success", "message": msg}

@app.get("/api/index_maintenance")
def get_index_maintenance():
    """
    [NEW FEATURE] Unused Index Identification.
    Simulates finding indexes that are redundant or never used to declutter the database.
    """
    conn = database.get_connection()
    cursor = conn.cursor()
    
    # Query SQLite for all custom indexes (excluding sqlite auto-indexes)
    cursor.execute('''
        SELECT name, tbl_name 
        FROM sqlite_master 
        WHERE type='index' AND name NOT LIKE 'sqlite_autoindex%'
    ''')
    indexes = cursor.fetchall()
    conn.close()
    
    suggestions = []
    for idx_name, tbl_name in indexes:
        # In a real system, we'd check pg_stat_user_indexes for idx_scan == 0
        # Here we simulate the AI flagging an index called 'test_idx' or randomly flagging one for demonstration
        if "test_idx" in idx_name or "redundant" in idx_name:
            suggestions.append({
                "index_name": idx_name,
                "table": tbl_name,
                "reason": "This index has 0 scans in the last 30 days. It slows down INSERT/UPDATE operations.",
                "sql": f"DROP INDEX {idx_name};"
            })
            
    return suggestions

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
