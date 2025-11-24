import sqlite3


class AppDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id TEXT PRIMARY KEY,
                name TEXT,
                position TEXT,
                department TEXT,
                salary REAL
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                employee_id TEXT,
                date TEXT,
                time_in TEXT,
                time_out TEXT,
                PRIMARY KEY (employee_id, date)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payroll (
                employee_id TEXT,
                month_year TEXT,
                gross_pay REAL,
                total_deductions REAL,
                net_pay REAL,
                PRIMARY KEY (employee_id, month_year)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS leaves (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT,
                date TEXT,
                leave_type TEXT,
                status TEXT,
                UNIQUE (employee_id, date),
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS loans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT,
                amount REAL,
                remaining_balance REAL,
                date_requested TEXT,
                status TEXT,
                FOREIGN KEY (employee_id) REFERENCES employees(id)
            )
        """)
        self.conn.commit()