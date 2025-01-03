import bcrypt
import sqlite3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

"""
    This class handles the administration of the SQLite database,
    including connecting to the database,executing SQL queries,
    and initializing the admin table.
"""
class DBAdmin:
    # Connect to the SQLite database
    def db_connect(self):
        try:
            return sqlite3.connect('admin.db')
        except sqlite3.Error as e:
            logging.error(f"Error connecting to database: {e}")
            return None
        
    # Execute a SQL query
    def db_execute(self, query, params=None, fetch=False):
        try:
            with self.db_connect() as conn:
                cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            if fetch:
                return cursor.fetchall()
            conn.commit()
        except sqlite3.Error as e:
            logging.error(f"Error executing query: {e}")
            return None

    # Initialize the admin table in the database
    def init_admin_db(self):
        try:
            table = '''CREATE TABLE IF NOT EXISTS admin (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(255) NOT NULL,
                password VARCHAR(255) NOT NULL);'''
            self.db_execute(table)
        except sqlite3.Error as e:
            logging.error(f"Error creating table: {e}")
            return None

    # Add a new admin to the database
    def db_add_admin(self, username, password):
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.db_execute('INSERT INTO admin (username, password) VALUES (?, ?)', (username, hashed_password))
        except sqlite3.Error as e:
            logging.error(f"Error adding admin: {e}")
            return None
        
    # Delete an admin from the database
    def db_delete_admin(self, username):
        try:
            self.username = username
            return self.db_execute('DELETE FROM admin WHERE username = ?', (self.username,))
        except sqlite3.Error as e:
            logging.error(f"Error deleting admin: {e}")
            return None

    # Check if the provided username and password match an admin in the database
    def db_check_admin(self, username, password):
        try:
            result = self.db_execute('SELECT password FROM admin WHERE username = ?', (username,), fetch=True)
            if result:
                stored_hash = result[0][0]
                if isinstance(stored_hash, str):
                    stored_hash = stored_hash.encode('utf-8')  
                try:
                    if bcrypt.checkpw(password.encode('utf-8'), stored_hash):
                        return True
                except ValueError as e:
                    logging.error(f"Error: {e}") 
            return False
        except sqlite3.Error as e:
            logging.error(f"Error checking admin: {e}")
            return False

    # Check if any admins exist in the database
    def db_admin_exists(self):
        try:
            result = self.db_execute('SELECT COUNT(*) FROM admin', fetch=True)
            count = result[0][0] if result else 0
            return count > 0
        except sqlite3.Error as e:
            logging.error(f"Error checking admin: {e}")
            return False
    
    # List all admin usernames in the database
    def list_admins(self):
        try:
            result = self.db_execute('SELECT username FROM admin', fetch=True)
            admin_names = [row[0] for row in result]
            return admin_names
        except sqlite3.Error as e:
            logging.error(f"Error listing admins: {e}")
            return None
    
    # Update the password for an admin in the database
    def db_update_admin_password(self, username, password):
        try:
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            self.db_execute('UPDATE admin SET password = ? WHERE username = ?', (hashed_password, username))
        except sqlite3.Error as e:
            logging.error(f"Error updating admin password: {e}")
            return None