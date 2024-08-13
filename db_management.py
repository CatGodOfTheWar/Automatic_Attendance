import sqlite3
from datetime import datetime

class DBManagement:

    def db_connect(self):
        return sqlite3.connect('students.db')
        
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
        query = '''SELECT * FROM STUDENTS ORDER BY Student_name ASC;'''
        return self.db_execute(query, fetch=True)

    def db_delete_students(self, student_id):
        self.student_id = student_id
        query = '''DELETE FROM STUDENTS WHERE Id = ?'''
        return self.db_execute(query, (self.student_id,))

    def db_check_student(self, name):
        self.name = name
        query = '''SELECT Student_name FROM STUDENTS ORDER BY Student_name ASC;'''
        students = self.db_execute(query, fetch=True)
        return any(student[0] == self.name for student in students)

    def db_add_student(self, name):
        date = None
        query = '''INSERT INTO STUDENTS (Student_name, Date) VALUES (?, ?);'''
        self.db_execute(query, (name, date))

    def db_update_student(self, old_name, new_name):
        self.old_name = old_name
        self.new_name = new_name
        query = '''UPDATE STUDENTS SET Student_name = ? WHERE Student_name = ?;'''
        params = (self.new_name, self.old_name)
        return self.db_execute(query, params)

    def db_record_attendance(self, student_name):
        date = datetime.now().strftime("%Y-%m-%d")
        self.db_execute('INSERT INTO STUDENTS (Student_name, Date) VALUES (?, ?)', (student_name, date))

    def db_get_attendance(self):
        query = '''SELECT Student_name, Date FROM STUDENTS;'''
        return self.db_execute(query, fetch=True)