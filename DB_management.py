import sqlite3 
from datetime import datetime
import logging

# Configurare logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class DBmanagement: 
    def db_connect(self):
        try:
            return sqlite3.connect('students.db')
        except Exception as e:
            print(f"Error: {e}")
            return None
        
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
            
    def db_students_init(self):
        table = '''CREATE TABLE IF NOT EXISTS STUDENTS (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Student_name TEXT NOT NULL,
                    Date TEXT DEFAULT NULL 
                    );'''
        self.db_execute(table)
    
    def db_get_students(self):
        return self.db_execute('SELECT * FROM STUDENTS ORDER BY Student_name ASC', fetch=True)

    def db_delete_students(self, student_name):
        if not student_name:
            raise ValueError("Student name must be provided")
        self.student_name = student_name
        return self.db_execute('DELETE FROM STUDENTS WHERE Student_name = ?', (self.student_name,))

    def db_check_student(self, name):
        self.name = name
        students = self.db_execute('SELECT Student_name FROM STUDENTS ORDER BY Student_name ASC', fetch=True)
        return any(student[0] == self.name for student in students)

    def db_add_student(self, name):
        date = None
        self.db_execute('INSERT INTO STUDENTS (Student_name, Date) VALUES (?, ?)', (name, date))

    def db_update_student(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name
        params = (self.new_name, self.old_name)
        return self.db_execute('UPDATE STUDENTS SET Student_name = ? WHERE Student_name = ?', params)

    def db_record_attendance(self, student_name):
        date = datetime.now().strftime("%Y-%m-%d")
        check = self.db_execute('SELECT COUNT(*) FROM STUDENTS WHERE student_name = ? AND date = ?', (student_name, date), fetch=True)
        if not check[0][0]:
            self.db_execute('INSERT INTO STUDENTS (Student_name, Date) VALUES (?, ?)', (student_name, date))
            return True
        else:
            return False
        
    def db_get_attendance(self):
        return self.db_execute('SELECT Student_name, Date FROM STUDENTS', fetch=True)