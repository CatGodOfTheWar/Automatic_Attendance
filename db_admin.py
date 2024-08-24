import bcrypt
import sqlite3

class DBAdmin:
    def db_connect(self):
        return sqlite3.connect('admin.db')
        
    def db_execute(self, query, params=None, fetch=False):
        with self.db_connect() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                return cursor.fetchall()
            conn.commit()

    def init_admin_db(self):
        table = '''CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL);'''
        self.db_execute(table)

    def db_add_admin(self, username, password):
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self.db_execute('INSERT INTO admin (username, password) VALUES (?, ?)', (username, hashed_password))

    def db_check_admin(self, username, password):
        result = self.db_execute('SELECT password FROM admin WHERE username = ?', (username,), fetch=True)
        if result:
            stored_hash = result[0][0]
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')  
            try:
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                    return True
            except ValueError as e:
                print(f"Error: {e}") 
        return False

    def db_admin_exists(self):
        result = self.db_execute('SELECT COUNT(*) FROM admin', fetch=True)
        count = result[0][0] if result else 0
        return count > 0