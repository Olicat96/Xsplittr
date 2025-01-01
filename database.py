import sqlite3

class Database:
    def __init__(self, db_name="splitwise.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.initialize_tables()

    def initialize_tables(self):
        """Initialize all necessary tables in the database."""
        with self.conn:
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS participants (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    first_name TEXT NOT NULL,
                    last_name TEXT NOT NULL,
                    nickname TEXT UNIQUE NOT NULL,
                    group_id INTEGER NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES groups(id)
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS bills (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    split_method TEXT NOT NULL,
                    paid_by INTEGER NOT NULL,
                    group_id INTEGER NOT NULL,
                    FOREIGN KEY (group_id) REFERENCES groups(id)
                )
            """)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS bill_splits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL,
                    participant_id INTEGER NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (bill_id) REFERENCES bills(id),
                    FOREIGN KEY (participant_id) REFERENCES participants(id)
                )
            """)

    def execute_query(self, query, params=None):
        """Execute a single query."""
        with self.conn:
            self.cursor.execute(query, params or ())
            self.conn.commit()
        return self.cursor

    def fetch_one(self, query, params=None):
        """Fetch a single result from a query."""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchone()

    def fetch_all(self, query, params=None):
        """Fetch all results from a query."""
        self.cursor.execute(query, params or ())
        return self.cursor.fetchall()

    def close_connection(self):
        """Close the database connection."""
        self.conn.close()
