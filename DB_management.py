import sqlite3 
from datetime import datetime
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define constants for file paths and other configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_STUDENT_PATH = os.path.join(DATA_DIR, "students.db")

"""
    This class handles the administration of the SQLite database,
    including connecting to the database, executing SQL queries, 
    and initializing the student table.
"""
class DBmanagement: 
    # Connect to the database
    def db_connect(self):
        try:
            return sqlite3.connect(DB_STUDENT_PATH)
        except Exception as e:
            logging.error(f"Error: {e}")
            return None
        
    # Execute a database query
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
            
    # Initialize the students table
    def db_students_init(self):
        try:
            table = '''CREATE TABLE IF NOT EXISTS STUDENTS (
                        Id INTEGER PRIMARY KEY AUTOINCREMENT,
                        Student_name TEXT NOT NULL,
                        Date TEXT DEFAULT NULL 
                        );'''
            self.db_execute(table)
        except sqlite3.Error as e:
            logging.error(f"Error creating table: {e}")
            return None
    
    # Get all students from the database
    def db_get_students(self):
        try:
            return self.db_execute('SELECT * FROM STUDENTS ORDER BY Student_name ASC', fetch=True)
        except sqlite3.Error as e:
            logging.error(f"Error fetching students: {e}")
            return None

    # Delete a student from the database
    def db_delete_students(self, student_name):
        try:
            if not student_name:
                raise ValueError("Student name must be provided")
            self.student_name = student_name
            return self.db_execute('DELETE FROM STUDENTS WHERE Student_name = ?', (self.student_name,))
        except sqlite3.Error as e:
            logging.error(f"Error deleting student: {e}")
            return None

    # Check if a student exists in the database
    def db_check_student(self, name):
        try:
            self.name = name
            students = self.db_execute('SELECT Student_name FROM STUDENTS ORDER BY Student_name ASC', fetch=True)
            return any(student[0] == self.name for student in students)
        except sqlite3.Error as e:
            logging.error(f"Error checking student: {e}")
            return None

    # Add a new student to the database
    def db_add_student(self, name):
        try:
            date = None
            self.db_execute('INSERT INTO STUDENTS (Student_name, Date) VALUES (?, ?)', (name, date))
        except sqlite3.Error as e:
            logging.error(f"Error adding student: {e}")
            return None

    # Update a student's name in the database
    def db_update_student(self, old_name, new_name):
        try:
            self.old_name = old_name
            self.new_name = new_name
            params = (self.new_name, self.old_name)
            return self.db_execute('UPDATE STUDENTS SET Student_name = ? WHERE Student_name = ?', params)
        except sqlite3.Error as e:
            logging.error(f"Error updating the student name: {e}")
            return None

    # Record attendance for a student
    def db_record_attendance(self, student_name):
        try:
            date = datetime.now().strftime("%Y-%m-%d")
            check = self.db_execute('SELECT COUNT(*) FROM STUDENTS WHERE student_name = ? AND date = ?', (student_name, date), fetch=True)
            if not check[0][0]:
                self.db_execute('INSERT INTO STUDENTS (Student_name, Date) VALUES (?, ?)', (student_name, date))
                return True
            else:
                return False
        except sqlite3.Error as e:
            logging.error(f"Error recording attendance: {e}")
            return None
        
    # Record manual attendance for a student
    def db_record_manual_attendance(self, student_name, date):
        try:
            check = self.db_execute('SELECT COUNT(*) FROM STUDENTS WHERE student_name = ? AND date = ?', (student_name, date), fetch=True)
            if not check[0][0]:
                self.db_execute('INSERT INTO STUDENTS (Student_name, Date) VALUES (?, ?)', (student_name, date))
                return True
            else:
                return False
        except sqlite3.Error as e:
            logging.error(f"Error recording attendance: {e}")
        
    # Get attendance records from the database
    def db_get_attendance(self):
        try:
            return self.db_execute('SELECT Student_name, Date FROM STUDENTS', fetch=True)
        except sqlite3.Error as e:
            logging.error(f"Error getting attendance: {e}")
            return None