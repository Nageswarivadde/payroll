-- schema.sql

CREATE TABLE IF NOT EXISTS employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    position TEXT NOT NULL,
    salary REAL NOT NULL,
    department TEXT
);

CREATE TABLE IF NOT EXISTS payslips (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    employee_name TEXT NOT NULL,
    position TEXT NOT NULL,
    department TEXT NOT NULL,
    salary REAL NOT NULL,
    tax REAL NOT NULL,
    benefits REAL NOT NULL,
    net_pay REAL NOT NULL,
    period TEXT NOT NULL,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
