import logging
from time import sleep
import os
import pandas # type: ignore

from photo_management import PhotoManagement
from recognition import Recognition
from db_management import DBManagement

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

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
        os.system("rm -rf attendance_report.xlsx")
        os.system("rm -rf __pycache__")
        print("Reset done")
        
    def generate_attendance_report(self, file_path='attendance_report.xlsx'):
        attendance_data = self.dBManagement.db_get_attendance()
        dataFrame = pandas.DataFrame(attendance_data, columns=['student_name','date'])
        dataFrame = dataFrame[dataFrame['date'].notna()]
        groupData = dataFrame.groupby('student_name').agg({
            'date': ['count', lambda x: list(x)]
            }).reset_index()
        groupData.columns = ['student_name', 'attendance_count', 'dates']
        groupData.to_excel(file_path, index=False)

    def register_multiple_students(self, file_path):
        with open(file_path, 'r') as file:
            students = file.read().splitlines()
            for student in students:
                if not self.dBManagement.db_check_student(student):
                    self.dBManagement.db_add_student(student)
                else:
                    print(f"Student {student} already registered")
        
def main():

    username = input("Enter student name: ")    
    student_obj = Student(username)
    while True:
        student_obj.dBManagement.db_students_init()
        user_input = int(input("Choose option(0 - add / 1 - add_temp / 2 - check / 3 - DB / 4 - reset / 5 - close): "))
        if user_input == 0:
            if not student_obj.dBManagement.db_check_student(username):
                student_obj.photoManagement.take_picture(student_obj.name, Student.images_folder())
                student_obj.dBManagement.db_add_student(username)
        elif user_input == 1:
            student_obj.photoManagement.take_picture(student_obj.name, Student.temporary_folder())
        elif user_input == 2:
            if student_obj.dBManagement.db_check_student(username):
                if student_obj.recognition.check(f"{Student.images_folder()}/{username}.jpg", f"{Student.temporary_folder()}/{username}.jpg"):
                    print("Fetele se potrivesc")
                    student_obj.dBManagement.db_record_attendance(username)
                else:
                    print("Fetele nu se potrivesc")
            else:
                print("Studentul nu este inregistrat")
        elif user_input == 3:
            print("DB options")
            db_choice = int(input("Choose option(0 - get_students / 1 - get_attendance_report / 2 - update_name): "))
            if db_choice == 0:
                print(student_obj.dBManagement.db_get_students())
            elif db_choice == 1:  
                student_obj.generate_attendance_report()
            elif db_choice == 2:
                old_name = input("Enter the old name: ")
                new_name = input("Enter the new name: ")
                student_obj.dBManagement.db_update_student(old_name, new_name)
        elif user_input == 4:
            Student.reset()
            break
        elif user_input == 5:
            os.system(f"rm -rf {Student.temporary_folder()}/*")
            print("System shutdown")
            break
        else:
            print("Invalid option")
            continue

if __name__ == '__main__':
    main()

    