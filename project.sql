CREATE INDEX idx_students_marks ON students(marks);
EXPLAIN ANALYZE
SELECT * FROM students WHERE marks > 90;
CREATE TABLE query_logs (
    id SERIAL PRIMARY KEY,
    query_text TEXT,
    execution_time_ms FLOAT,
    scan_type TEXT,
    optimization_applied BOOLEAN,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
INSERT INTO query_logs (
    query_text,
    execution_time_ms,
    scan_type,
    optimization_applied
)
VALUES (
    'SELECT * FROM students WHERE marks > 90',
    7.752,
    'Bitmap Index Scan',
    true
);
SELECT * FROM query_logs;

SET enable_bitmapscan = off;
SET enable_indexscan = off;

EXPLAIN ANALYZE
SELECT * FROM students WHERE marks > 90;

INSERT INTO query_logs (
    query_text,
    execution_time_ms,
    scan_type,
    optimization_applied
)
VALUES (
    'SELECT * FROM students WHERE marks > 90',
    1.382,
    'Sequential Scan',
    false
);

SELECT * FROM query_logs;
