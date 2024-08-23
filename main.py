import logging
from time import sleep
import os
import pandas # type: ignore

from photo_management import PhotoManagement
from recognition import Recognition
from db_management import DBManagement

import customtkinter
import tkinter.font as tkFont

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("green")

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

class App(customtkinter.CTk):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Automated Attendance System PreAlpha Release")
        self.width = self.winfo_screenwidth()
        self.height = self.winfo_screenheight()
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        default_font = tkFont.nametofont("TkDefaultFont")
        default_font.configure(family="Roboto", size=12)
        self.option_add("*Font", default_font)
        self.configure(bg="black")

        self.login_frame = customtkinter.CTkFrame(self, corner_radius=30, height=int(self.height * 0.75), width=int(self.width * 0.5),)
        self.login_frame.place(relx=0.5, rely=0.45, anchor="center")

        self.login_label = customtkinter.CTkLabel(self.login_frame, text="Admin Panel",
                                                  font=customtkinter.CTkFont(family="Roboto", size=50, weight="normal", slant="italic"),)
        self.login_label.grid(row=0, column=0, padx=200, pady=100)
        self.username_entry = customtkinter.CTkEntry(self.login_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), placeholder_text="Username",
                                                     font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"),justify="center")
        self.username_entry.grid(row=1, column=0, padx=200, pady=20)
        self.password_entry = customtkinter.CTkEntry(self.login_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), show="*", placeholder_text="Password",
                                                     font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"),justify="center")
        self.password_entry.grid(row=2, column=0, padx=200, pady=20)
        self.login_button = customtkinter.CTkButton(self.login_frame, text="Login", command=self.login_event, width=int(self.width * 0.25), height=int(self.height * 0.05),
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"),)
        self.login_button.grid(row=3, column=0, padx=200, pady=20)
        self.remember_me_checkbox = customtkinter.CTkCheckBox(self.login_frame, text="Remember Me",
                                                      font=customtkinter.CTkFont(family="Roboto", size=20, weight="normal", slant="italic"))
        self.remember_me_checkbox.grid(row=4, column=0, padx=200, pady=(20, 100))
    
        self.login_frame.configure(border_color=self.login_button.cget("fg_color"), border_width=2)
        self.login_frame.grid_rowconfigure(0, weight=1, minsize=50)
        self.login_frame.grid_rowconfigure(1, weight=1, minsize=50)
        self.login_frame.grid_rowconfigure(2, weight=1, minsize=50)
        self.login_frame.grid_rowconfigure(3, weight=1, minsize=50)
        self.login_frame.grid_rowconfigure(4, weight=1, minsize=50)
        self.login_frame.grid_columnconfigure(0, weight=1)


    def login_event(self):
        pass

if __name__ == '__main__':
    app = App()
    app.mainloop()