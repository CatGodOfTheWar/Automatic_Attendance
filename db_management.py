import sqlite3

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
            conn.commit()
            if fetch:
                return cursor.fetchall()

    def db_students_init(self):
        table = '''CREATE TABLE IF NOT EXISTS STUDENTS (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Last_Name CHAR(255) NOT NULL,
                    First_Name CHAR(255) NOT NULL,
                     Date DATE DEFAULT CURRENT_DATE
                    );'''
        self.db_execute(table)

    def db_get_students(self):
        query = '''SELECT * FROM STUDENTS ORDER BY Last_Name ASC;'''
        return self.db_execute(query, fetch=True)

    def db_delete_students(self, student_id):
        self.student_id = student_id
        query = '''DELETE FROM STUDENTS WHERE Id = ?'''
        return self.db_execute(query, (self.student_id,))

    def db_check_student(self, name):
        self.name = name
        query = '''SELECT Last_Name || ' ' || First_Name FROM STUDENTS ORDER BY Last_Name ASC;'''
        students = self._execute(query, fetch=True)
        return any(student[0] == self.name for student in students)

    def db_add_student(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name 
        query = '''INSERT INTO STUDENTS (Last_Name, First_Name) VALUES (?, ?);'''
        return self.db_execute(query, (self.last_name, self.first_name))

    def db_update_student(self, student_id, first_name, last_name, date = None):
        self.student_id = student_id
        self.first_name = first_name
        self.last_name = last_name
        self.date = date
        if date:
            query = '''UPDATE STUDENTS SET Last_Name = ?, First_Name = ?, Date = ? WHERE Id = ?;'''
            params = (self.last_name, self.first_name, self.date, self.student_id)
        else:
            query = '''UPDATE STUDENTS SET Last_Name = ?, First_Name = ? WHERE Id = ?;'''  
            params = (self.last_name, self.first_name, self.student_id)
        return self.db_execute(query, params)
