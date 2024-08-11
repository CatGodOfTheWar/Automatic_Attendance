import logging
from time import sleep
import cv2  # type: ignore
from picamera2 import Picamera2, Preview  # type: ignore
import face_recognition  # type: ignore
import sqlite3
import os

from photo_management import PhotoManagement
from recognition import Recognition
from db_management import DBManagement


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Student:

    def __init__(self, name):
        self.name = name
        self.photoManagement = PhotoManagement()
        self.recognition = Recognition()
        self.dBManagement = DBManagement()
    
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

 
def main():

    first_name = input("Enter your first name: ").strip()
    last_name = input("Enter your last name: ").strip()
    username = last_name + " " + first_name
    while True:
        student_obj = Student(username)
        student_obj.dBManagement.db_students_init()
        user_input = int(input("Choose option(0 - add / 1 - add_temp / 2 - check / 3 - DB / 4 - reset): "))
        if user_input == 0:
            student_obj.photoManagement.take_picture(student_obj.name, Student.images_folder())
            student_obj.dBManagement.db_add_student(first_name, last_name)
        elif user_input == 1:
            student_obj.photoManagement.take_picture(student_obj.name, Student.temporary_folder())
        elif user_input == 2:
            if student_obj.recognition.check(f"{Student.images_folder()}/{username}.jpg", f"{Student.temporary_folder()}/{username}.jpg"):
                print("Fetele se potrivesc")
            else:
                print("Fetele nu se potrivesc")
        elif user_input == 3:
            print(student_obj.dBManagement.db_get_students())  
        elif user_input == 4:
            Student.reset()
            break
        del student_obj


if __name__ == '__main__':
    main()

    