import sqlite3
from hashlib import sha256

class LocalDB:
    def __init__(self, db_path="finance.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL
            )
        """)
        cur.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                date TEXT,
                description TEXT,
                amount REAL,
                category TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        """)
        conn.commit()
        conn.close()

    def register_user(self, username: str, password: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        user_id = sha256(username.encode()).hexdigest()[:16]
        pw_hash = sha256(password.encode()).hexdigest()
        cur.execute("INSERT INTO users (user_id, username, password_hash) VALUES (?, ?, ?)",
                    (user_id, username, pw_hash))
        conn.commit()
        conn.close()
        return user_id

    def authenticate(self, username: str, password: str):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("SELECT user_id, password_hash FROM users WHERE username=?", (username,))
        row = cur.fetchone()
        conn.close()
        if row and sha256(password.encode()).hexdigest() == row[1]:
            return row[0]
        return None

    def put(self, item: dict):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO transactions (transaction_id, user_id, date, description, amount, category)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            item['transaction_id'],
            item['user_id'],
            item['date'],
            item['description'],
            float(item['amount']),
            item['category']
        ))
        conn.commit()
        conn.close()

    def get_transactions(self, user_id: str, filters: dict = None):
        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        query = "SELECT transaction_id, date, description, amount, category FROM transactions WHERE user_id=?"
        params = [user_id]
        if filters:
            if "category" in filters:
                query += " AND category=?"
                params.append(filters["category"])
            if "month" in filters:
                query += " AND strftime('%m', date)=?"
                params.append(filters["month"])
            if "year" in filters:
                query += " AND strftime('%Y', date)=?"
                params.append(filters["year"])
        cur.execute(query, params)
        rows = cur.fetchall()
        conn.close()
        return [{"transaction_id": r[0], "date": r[1], "description": r[2], "amount": r[3], "category": r[4]} for r in rows]
