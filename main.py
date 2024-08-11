import logging
from time import sleep
import cv2  # type: ignore
import numpy as np  # type: ignore
from picamera2 import MappedArray, Picamera2, Preview  # type: ignore
import face_recognition  # type: ignore
import sqlite3
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Student:

    def __init__(self, name):
        self.name = name
        self.photoManagement = self.PhotoManagement()
        self.recognition = self.Recognition()
        self.dBManagement = self.DBManagement()
    
    @classmethod
    def images_folder(cls):
        student_img = "student_images_saved"
        if not os.path.exists(student_img):
            os.makedirs(student_img)
        return student_img
        
    @classmethod
    def temporary_folder(cls):
        temp_img = "temporary_images_saved"
        if not os.path.exists(temp_img):
            os.makedirs(temp_img)
        return temp_img
    
    @classmethod
    def reset(cls):
        os.system(f"rm -rf {cls.images_folder()}/*")
        os.system(f"rm -rf {cls.temporary_folder()}/*")
        os.system("rm -rf students.db")
    
    class PhotoManagement:
        
        def take_picture(self, name, path):
            self.name = name
            self.path = path         
            try:
                self.picam2 = Picamera2()
                self.camera_config = self.picam2.create_preview_configuration(
                                        main={"size": (4096, 2592)},
                                        lores={"size": (640, 480), "format": "YUV420"})
                self.picam2.configure(self.camera_config)
                self.picam2.start_preview(Preview.QT)
                self.picam2.start()
                sleep(5)
                self.picam2.capture_file(f"{self.path}/{self.name}.jpg")
                self.picam2.stop()
            except RuntimeError as e:
                print(f"Failed to acquire camera: {e}")
                print("Retrying in 5 seconds...")
                sleep(5)
                self.take_picture(self.name, self.folder) 
            finally:
                if hasattr(self, 'picam2'):
                    self.picam2.close()    
            
    class Recognition:

        def load_and_convert(self, path):
            img = cv2.imread(path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img
        
        def encode(self, img):
            if img is not None:
                face_encoding = face_recognition.face_encodings(img)
                if face_encoding:
                    return face_encoding[0]
            return None

        def check(self, student_img_path, temp_img_path):
            self.student_img_path = student_img_path
            self.temp_img_path = temp_img_path
            self.student_img = self.load_and_convert(self.student_img_path)
            self.temp_img = self.load_and_convert(self.temp_img_path)
            self.student_encoding = self.encode(self.student_img)
            self.temp_encoding = self.encode(self.temp_img)
            if self.student_encoding is not None:
                if self.temp_encoding is not None:
                    return face_recognition.compare_faces([self.student_encoding], self.temp_encoding)[0]
                else:
                    logging.error("temp_encoding empty")
            else:
                logging.error("student_encoding empty")
            return False

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

def main():

    first_name = input("Enter your first name: ").strip()
    last_name = input("Enter your last name: ").strip()
    username = last_name + " " + first_name
    while True:
        student_obj = Student(username)
        user_input = int(input("Choose option(0 - add / 1 - add_temp / 2 - check / 3 - DB / 4 - reset): "))
        if user_input == 0:
            student_obj.photoManagement.take_picture(student_obj.name, Student.images_folder())
        elif user_input == 1:
            student_obj.photoManagement.take_picture(student_obj.name, Student.temporary_folder())
        elif user_input == 2:
            if student_obj.recognition.check(f"{Student.images_folder()}/{username}.jpg", f"{Student.temporary_folder()}/{username}.jpg"):
                print("Fetele se potrivesc")
            else:
                print("Fetele nu se potrivesc")
        elif user_input == 3:
            student_obj.dBManagement.db_students_init()
            student_obj.dBManagement.db_add_student(first_name, last_name)
            print(student_obj.dBManagement.db_get_students())  
        elif user_input == 4:
            Student.reset()
            break
        del student_obj


if __name__ == '__main__':
    main()

    