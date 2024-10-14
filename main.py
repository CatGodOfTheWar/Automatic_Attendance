import logging
from time import sleep
import os
import pandas as pd
import sys
import customtkinter
import tkinter.font as tkFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from picamera2 import Picamera2
import subprocess
from recognition import Recognition
from db_management import DBManagement
from db_admin import DBAdmin

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')
customtkinter.set_appearance_mode("system")
customtkinter.set_default_color_theme("green")

class Student:

    def __init__(self, name):
        self.name = name
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
        os.system("rm -rf admin.db")
        os.system("rm -rf attendance_report.xlsx")
        os.system("rm -rf __pycache__")
        print("Reset done")
        
    def generate_attendance_report(self, file_path='attendance_report.xlsx'):
        attendance_data = self.dBManagement.db_get_attendance()
        dataFrame = pd.DataFrame(attendance_data, columns=['student_name','date'])
        dataFrame['date'] = dataFrame['date'].fillna("")
        groupData = dataFrame.groupby('student_name').agg({
            'date': [lambda x: max(0, len(x) - 1), lambda x: list(x)]
        }).reset_index()
        groupData.columns = ['student_name', 'attendance_count', 'dates']
        groupData.to_excel(file_path, index=False)
        
    def show_student_db(self):
        def wrap_text(text, max_chars_per_line=60):
            words = text.split(', ')
            wrapped_text = ""
            line_length = 0

            for word in words:
                if line_length + len(word) + 2 > max_chars_per_line: 
                    wrapped_text += "\n" + word
                    line_length = len(word)
                else:
                    if wrapped_text:  
                        wrapped_text += ", " + word
                    else:
                        wrapped_text += word
                    line_length += len(word) + 2

            return wrapped_text
        
        attendance_data = self.dBManagement.db_get_attendance()
        dataFrame = pd.DataFrame(attendance_data, columns=['student_name','date'])
        dataFrame['date'] = dataFrame['date'].fillna("")
        groupData = dataFrame.groupby('student_name').agg({
            'date': [lambda x: max(0, len(x) - 1), lambda x: list(x)]
        }).reset_index()
        groupData.columns = ['student_name', 'attendance_count', 'dates']
        attendance_list = groupData.to_dict(orient='records')
        formatted_output = [
            (record['student_name'], record['attendance_count'], wrap_text(", ".join(record['dates'])))
            for record in attendance_list
        ]
        return formatted_output

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
        self.camera = Picamera2()
        self.camera.configure(self.camera.create_preview_configuration(main={"size": (640, 480)}))
        self.camera.start()
        self.student = Student("Student")
        self.dBAdmin = DBAdmin()
        self.dBAdmin.init_admin_db()

        if not self.dBAdmin.db_admin_exists():
            self.show_registration_frame() 
        else:
            self.show_login_frame()

    def show_registration_frame(self):
        self.registration_frame = customtkinter.CTkFrame(self, corner_radius=30, height=int(self.height * 0.75), width=int(self.width * 0.5))
        self.registration_frame.place(relx=0.5, rely=0.45, anchor="center")
        self.registration_label = customtkinter.CTkLabel(self.registration_frame, text="Register Admin",
                                                        font=customtkinter.CTkFont(family="Roboto", size=50, weight="normal", slant="italic"))
        self.registration_label.grid(row=0, column=0, padx=200, pady=100)
        self.reg_username_entry = customtkinter.CTkEntry(self.registration_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), placeholder_text="Username",
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        self.reg_username_entry.grid(row=1, column=0, padx=200, pady=20)
        self.reg_username_entry.bind("<Return>", lambda event: self.register_event())
        self.reg_password_entry = customtkinter.CTkEntry(self.registration_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), show="*", placeholder_text="Password",
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        self.reg_password_entry.grid(row=2, column=0, padx=200, pady=20)
        self.reg_password_entry.bind("<Return>", lambda event: self.register_event())
        self.register_button = customtkinter.CTkButton(self.registration_frame, text="Register", command=self.register_event, width=int(self.width * 0.25), height=int(self.height * 0.05),
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.register_button.grid(row=3, column=0, padx=200, pady=(0, 100))
        self.registration_frame.configure(border_color=self.register_button.cget("fg_color"), border_width=2)
        self.registration_frame.grid_rowconfigure(0, weight=1, minsize=50)
        self.registration_frame.grid_rowconfigure(1, weight=1, minsize=50)
        self.registration_frame.grid_rowconfigure(2, weight=1, minsize=50)
        self.registration_frame.grid_rowconfigure(3, weight=1, minsize=50)
        self.registration_frame.grid_rowconfigure(4, weight=1, minsize=50)
        self.registration_frame.grid_columnconfigure(0, weight=1)
        self.error_label = customtkinter.CTkLabel(self.registration_frame, text="", text_color="red",
                                                font=customtkinter.CTkFont(family="Roboto", size=22, weight="normal", slant="italic"))
        self.error_label.grid(row=5, column=0, padx=200, pady=(20, 20))

    def show_login_frame(self):
        self.login_frame = customtkinter.CTkFrame(self, corner_radius=30, height=int(self.height * 0.75), width=int(self.width * 0.5))
        self.login_frame.place(relx=0.5, rely=0.45, anchor="center")
        self.login_label = customtkinter.CTkLabel(self.login_frame, text="Admin Panel",
                                                font=customtkinter.CTkFont(family="Roboto", size=50, weight="normal", slant="italic"))
        self.login_label.grid(row=0, column=0, padx=200, pady=100)
        self.username_entry = customtkinter.CTkEntry(self.login_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), placeholder_text="Username",
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        self.username_entry.grid(row=1, column=0, padx=200, pady=20)
        self.username_entry.bind("<Return>", lambda event: self.login_event())
        self.password_entry = customtkinter.CTkEntry(self.login_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), show="*", placeholder_text="Password",
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        self.password_entry.grid(row=2, column=0, padx=200, pady=20)
        self.password_entry.bind("<Return>", lambda event: self.login_event())  
        self.login_button = customtkinter.CTkButton(self.login_frame, text="Login", command=self.login_event, width=int(self.width * 0.25), height=int(self.height * 0.05),
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
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
        self.error_label = customtkinter.CTkLabel(self.login_frame, text="", text_color="red",
                                                font=customtkinter.CTkFont(family="Roboto", size=22, weight="normal", slant="italic"))
        self.error_label.grid(row=5, column=0, padx=200, pady=(20, 20))

    def show_main_frame(self):
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.side_frame = customtkinter.CTkFrame(self.main_frame, corner_radius=20, border_width=2, border_color="#3BA55D")  # Set height here
        self.admin_label = customtkinter.CTkLabel(self.side_frame, text="", anchor="center",
                                                font=customtkinter.CTkFont(family="Roboto", size=30, weight="normal", slant="italic"))
        self.back_button = customtkinter.CTkButton(self.side_frame, text="Advenced Settings", command=self.show_advanced_settings, corner_radius=20,
                                                font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.show_student = customtkinter.CTkButton(self.side_frame, text="Student Mode", command=self.show_student_mode, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.generate_report = customtkinter.CTkButton(self.side_frame, text="Generate Report", command=self.generate_report_event, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.refresh = customtkinter.CTkButton(self.side_frame, text="Refresh", command=self.refresh_attendance_event, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.web_view_btn = customtkinter.CTkButton(self.side_frame, text="Web View", command=self.web_view, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.log_out = customtkinter.CTkButton(self.side_frame, text="Log Out", command=self.back_event, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.close = customtkinter.CTkButton(self.side_frame, text="Close", command=self.close_window_event, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))

        self.side_frame.grid(row=0, column=1, rowspan=3, padx=(0, 50), pady=50, sticky="nsew")
        self.side_frame.grid_rowconfigure(0, weight=1, minsize=50)
        self.side_frame.grid_rowconfigure(1, weight=1, minsize=50)
        self.side_frame.grid_rowconfigure(2, weight=1, minsize=50)
        self.side_frame.grid_rowconfigure(3, weight=1, minsize=50)
        self.side_frame.grid_rowconfigure(4, weight=1, minsize=50)
        self.side_frame.grid_rowconfigure(5, weight=1, minsize=50)
        self.side_frame.grid_rowconfigure(6, weight=1, minsize=50)
        self.side_frame.grid_rowconfigure(7, weight=1, minsize=50)
        self.side_frame.grid_columnconfigure(0, weight=1)

        self.admin_label.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.back_button.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.show_student.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        self.generate_report.grid(row=3, column=0, padx=15, pady=15, sticky="nsew")
        self.refresh.grid(row=4, column=0, padx=15, pady=15, sticky="nsew")
        self.web_view_btn.grid(row=5, column=0, padx=15, pady=15, sticky="nsew")
        self.log_out.grid(row=6, column=0, padx=15, pady=15, sticky="nsew")
        self.close.grid(row=7, column=0, padx=15, pady=15, sticky="nsew")
        self.create_attendance_graphic()
        self.create_attendance_table()
        self.protocol("WM_DELETE_WINDOW", self.close_window_event)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.place(relx=0.5, rely=0.47, anchor="center")
            
    def create_attendance_graphic(self):
        primary_color = "#212325"
        color = "#3BA55D"
        students = [0] * 16 
        attendance = list(range(0, 16))  
        db_content = self.student.show_student_db()
        for row in db_content:
            index = row[1]  
            if 0 <= index < len(students):
                students[index] += 1
        plt.style.use('grayscale')
        self.fig, self.ax = plt.subplots(figsize=(10, 5)) 
        self.ax.bar(attendance, students, color=color, edgecolor=primary_color)
        self.ax.set_title('Attendance Average', color=primary_color)
        self.ax.set_xlabel('Number of Attendances', color=primary_color)
        self.ax.set_ylabel('Number of Students', color=primary_color)
        self.ax.tick_params(colors=primary_color)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=2, padx=50, pady=(50, 25))
      
    def create_attendance_table(self):
        attendance_data = self.student.show_student_db()
        color = "#3BA55D"  
        headers = ["Student", "Count of Attendance", "Every Date"]
        header_widths = [200, 200, 600]
        self.table_frame = customtkinter.CTkFrame(self.main_frame, border_color=color, border_width=2, corner_radius=20)
        self.table_frame.grid(row=2, column=0, padx=50, pady=(25, 50), sticky="nsew")
        scrollable_frame = customtkinter.CTkScrollableFrame(self.table_frame, width=1000, height=300, border_color=color, border_width=2)
        scrollable_frame.pack(expand=True, fill='both')
        row_font = customtkinter.CTkFont(size=18)
        for col, width in enumerate(header_widths):
            scrollable_frame.grid_columnconfigure(col, minsize=width)

        for col, (header, width) in enumerate(zip(headers, header_widths)):
            frame = customtkinter.CTkFrame(scrollable_frame, width=width, height=75, corner_radius=10, fg_color=color)
            frame.grid(row=0, column=col, padx=5, pady=5, sticky="nsew")
            label = customtkinter.CTkLabel(frame, text=header, text_color="white", font=customtkinter.CTkFont(weight="bold", slant="italic", size=20))
            label.pack(expand=True, fill='both', padx=10, pady=10)

        for row, (username, count, dates) in enumerate(attendance_data, start=1):
            username_label = customtkinter.CTkLabel(scrollable_frame, text=username, width=200, height=75, font=row_font)
            username_label.grid(row=row, column=0, padx=5, pady=5)
            count_label = customtkinter.CTkLabel(scrollable_frame, text=count, width=150, height=75, font=row_font)
            count_label.grid(row=row, column=1, padx=5, pady=5)
            dates_label = customtkinter.CTkLabel(scrollable_frame, text=dates, width=600, height=75, font=row_font, anchor="center")  # Use anchor="w" for left alignment
            dates_label.grid(row=row, column=2, padx=5, pady=5)

    def show_student_mode(self):
        self.main_frame.destroy()  
        self.show_student_frame = customtkinter.CTkFrame(self, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.show_student_frame.place(relx=0.5, rely=0.47, anchor="center")
        self.show_student_frame.grid_rowconfigure(0, weight=1)
        self.show_student_frame.grid_columnconfigure(0, weight=1)
        self.show_student_frame.grid_columnconfigure(1, weight=1)

        self.video_frame = customtkinter.CTkFrame(self.show_student_frame, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.video_frame.grid(row=0, column=0, padx=50, pady=50, sticky="nsew")

        self.buttons_frame = customtkinter.CTkFrame(self.show_student_frame, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.buttons_frame.grid(row=0, column=1, rowspan=2, padx=50, pady=50, sticky="nsew")

        self.student_label = customtkinter.CTkLabel(self.buttons_frame, text="Welcome \n Students!", anchor="center",
                                                    font=customtkinter.CTkFont(family="Roboto", size=30, weight="normal", slant="italic"))
        self.add_attendance = customtkinter.CTkButton(self.buttons_frame, text="Add\nAttendance", command=self.add_attendance_event, corner_radius=20, 
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.register_student = customtkinter.CTkButton(self.buttons_frame, text="Register\nStudent", command=self.register_student_event, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.exit = customtkinter.CTkButton(self.buttons_frame, text="Exit", command=self.back_event_student, corner_radius=20, 
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.close = customtkinter.CTkButton(self.buttons_frame, text="Close", command=self.close_window_event, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.add_attendance_label = customtkinter.CTkLabel(self.show_student_frame, text="Select Student:", justify="center", 
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.attendance_entry = customtkinter.CTkEntry(self.show_student_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), placeholder_text="Name",
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        all_students = self.student.show_student_db()
        students = [row[0] for row in all_students]
        self.student_dropdown = customtkinter.CTkOptionMenu(self.show_student_frame, values=students, anchor="center",
                                                            font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.add_student_label = customtkinter.CTkLabel(self.show_student_frame, text="Register Student:", justify="center",
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        
        
        self.buttons_frame.grid_rowconfigure(0, weight=1)
        self.buttons_frame.grid_rowconfigure(1, weight=1)
        self.buttons_frame.grid_rowconfigure(2, weight=1)
        self.buttons_frame.grid_rowconfigure(3, weight=1)
        self.buttons_frame.grid_rowconfigure(4, weight=1)
        self.buttons_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)
        self.video_frame.grid_columnconfigure(0, weight=1)

        self.student_label.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.add_attendance.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.register_student.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")
        self.exit.grid(row=3, column=0, padx=15, pady=15, sticky="nsew")
        self.close.grid(row=4, column=0, padx=15, pady=15, sticky="nsew")
        self.add_attendance_label.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.student_dropdown.grid(row=2, column=0, padx=15, pady=(15, 50), sticky="nsew")
        self.add_student_label.grid(row=3, column=0, padx=15, pady=15, sticky="nsew")
        self.attendance_entry.grid(row=4, column=0, padx=(50, 15), pady=(15, 50), sticky="nsew")

        self.video_label = customtkinter.CTkLabel(self.video_frame, text="")
        self.video_label.pack(expand=True, fill="both")
        self.update_frame()
            
    def update_frame(self):
        frame = self.camera.capture_array()
        image = Image.fromarray(frame)
        image = ImageTk.PhotoImage(image)
        self.video_label.configure(image=image)
        self.video_label.image = image
        self.after(1000 // 24, self.update_frame)   
        
    def add_attendance_event(self):
        student_name = self.student_dropdown.get()
        self.frame = self.camera.capture_array()
        if self.frame is not None:
            image = Image.fromarray(self.frame)
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            filename = f"{student_name}.jpg"
            image.save(filename)
            subprocess.run(['mv', filename, Student.temporary_folder()])
            if self.student.recognition.check(f"{Student.images_folder()}/{student_name}.jpg", f"{Student.temporary_folder()}/{student_name}.jpg"):
                if self.student.dBManagement.db_record_attendance(student_name):
                    self.show_popup(f"Attendance added for {student_name}.")
                else:
                    self.show_popup(f"Attendance already recorded for {student_name}.")
            else:
                self.show_popup(f"Student {student_name} not registered.")
        else:
            self.show_popup("No frame available to save.")
        
    def register_student_event(self):
        student_name = self.attendance_entry.get()
        self.frame = self.camera.capture_array()
        if not self.student.dBManagement.db_check_student(student_name):
            if self.frame is not None:
                image = Image.fromarray(self.frame)
                if image.mode == 'RGBA':
                    image = image.convert('RGB')
                filename = f"{student_name}.jpg"
                image.save(filename)
                subprocess.run(['mv', filename, Student.images_folder()])
                self.student.dBManagement.db_add_student(student_name)
                self.show_popup(f"Student {student_name} registered.")
                self.student_dropdown.configure(values=[student[0] for student in self.student.show_student_db()])
            else:
                self.show_popup("No frame available to save.")
        else:
            self.show_popup(f"Student {student_name} already registered.")
            
    def show_popup(self, message):
        popup = tk.Toplevel()
        popup.title("Notification")
        popup.geometry("750x300")
        popup.configure(bg="#696880")
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        x = (popup.winfo_screenwidth() // 2) - (width // 2)
        y = (popup.winfo_screenheight() // 2) - (height // 2)
        popup.geometry(f'{width}x{height}+{x}+{y}')
        label = customtkinter.CTkLabel(popup, text=message, bg_color="#696880", text_color="white", font=("Roboto", 25, "bold"))
        label.pack(expand=True, padx=20, pady=20)
        popup.after(5000, popup.destroy)
    
    def show_advanced_settings(self):
        

        # Main frame setup
        self.main_frame.destroy()
        self.show_advanced_frame = customtkinter.CTkFrame(self, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.show_advanced_frame.place(relx=0.5, rely=0.47, anchor="center")
        
        # Configure the grid weights for the show_advanced_frame
        self.show_advanced_frame.grid_rowconfigure(0, weight=1)
        self.show_advanced_frame.grid_rowconfigure(1, weight=1)
        self.show_advanced_frame.grid_rowconfigure(2, weight=1)
        self.show_advanced_frame.grid_rowconfigure(3, weight=1)
        self.show_advanced_frame.grid_columnconfigure(0, weight=1)
        self.show_advanced_frame.grid_columnconfigure(1, weight=1)

        # Frames inside show_advanced_frame
        self.name_frame = customtkinter.CTkFrame(self.show_advanced_frame, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.name_frame.grid(row=0, column=0, padx=50, pady=(50, 30), sticky="nsew")
        self.admin_add_frame = customtkinter.CTkFrame(self.show_advanced_frame, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.admin_add_frame.grid(row=1, column=0, padx=50, pady=30, sticky="nsew")
        self.admin_select_frame = customtkinter.CTkFrame(self.show_advanced_frame, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.admin_select_frame.grid(row=2, column=0, padx=50, pady=30, sticky="nsew")
        self.delete_frame = customtkinter.CTkFrame(self.show_advanced_frame, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.delete_frame.grid(row=3, column=0, padx=50, pady=(30, 50), sticky="nsew")
        self.advanced_admin_frame = customtkinter.CTkFrame(self.show_advanced_frame, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.advanced_admin_frame.grid(row=0, column=1, rowspan=4, padx=(0, 50), pady=50, sticky="nsew")

        # Configure the grid weights for the inner frames
        for frame in [self.name_frame, self.admin_add_frame, self.admin_select_frame, self.delete_frame]:
            frame.grid_rowconfigure(0,weight=1)
            frame.grid_rowconfigure(1, weight=1)
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=1)

        # Labels and dropdowns inside name_frame
        self.student_name_label = customtkinter.CTkLabel(self.name_frame, text="Student Name:", anchor="center",
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.student_name_label.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.student_dropdown = customtkinter.CTkOptionMenu(self.name_frame, values=[student[0] for student in self.student.show_student_db()], anchor="center", height=int(self.height * 0.055),
                                                            font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.student_dropdown.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.new_student_name_label = customtkinter.CTkLabel(self.name_frame, text="New Student Name:", anchor="center",
                                                            font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.new_student_name_label.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.new_student_name_entry = customtkinter.CTkEntry(self.name_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), placeholder_text="Name",
                                                            font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        self.new_student_name_entry.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

        # Labels and entries inside admin_add_frame
        self.add_admin_name_label = customtkinter.CTkLabel(self.admin_add_frame, text="Admin Name:", anchor="center",
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.add_admin_name_label.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.add_admin_name_entry = customtkinter.CTkEntry(self.admin_add_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), placeholder_text="Name",
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        self.add_admin_name_entry.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.add_admin_password_label = customtkinter.CTkLabel(self.admin_add_frame, text="Admin Password:", anchor="center",
                                                            font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.add_admin_password_label.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.add_admin_password_entry = customtkinter.CTkEntry(self.admin_add_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), show="*", placeholder_text="Password",
                                                            font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        self.add_admin_password_entry.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

        # Labels and dropdowns inside admin_select_frame
        self.select_admin_name_label = customtkinter.CTkLabel(self.admin_select_frame, text="Admin Name:", anchor="center",
                                                            font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.select_admin_name_label.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.admin_dropdown = customtkinter.CTkOptionMenu(self.admin_select_frame, values=self.dBAdmin.list_admins(), anchor="center", height=int(self.height * 0.055),
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.admin_dropdown.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.add_new_password_label = customtkinter.CTkLabel(self.admin_select_frame, text="New Password:", anchor="center",
                                                            font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.add_new_password_label.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.password_entry = customtkinter.CTkEntry(self.admin_select_frame, width=int(self.width * 0.25), height=int(self.height * 0.05), show="*", placeholder_text="Password",
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"), justify="center")
        self.password_entry.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")

        # Labels and dropdowns inside delete_frame
        self.delete_admin_label = customtkinter.CTkLabel(self.delete_frame, text="Select Admin:", anchor="center",
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.delete_admin_label.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")
        self.delete_admin_dropdown = customtkinter.CTkOptionMenu(self.delete_frame, values=self.dBAdmin.list_admins(), anchor="center", height=int(self.height * 0.055),
                                                                font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.delete_admin_dropdown.grid(row=0, column=1, padx=15, pady=15, sticky="nsew")
        self.delete_student_label = customtkinter.CTkLabel(self.delete_frame, text="Select Student:", anchor="center",
                                                        font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.delete_student_label.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")
        self.delete_student_dropdown = customtkinter.CTkOptionMenu(self.delete_frame, values=[student[0] for student in self.student.show_student_db()], anchor="center", height=int(self.height * 0.055),
                                                                font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.delete_student_dropdown.grid(row=1, column=1, padx=15, pady=15, sticky="nsew")
        admin_name = self.dBAdmin.list_admins()[0]  # Assuming you want the first admin name

        
        self.advanced_admin_frame.grid_rowconfigure(0, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(1, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(2, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(3, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(4, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(5, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(6, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(7, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(8, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(9, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(10, weight=1)
        self.advanced_admin_frame.grid_rowconfigure(11, weight=1)
        self.advanced_admin_frame.grid_columnconfigure(0, weight=1)

        # Welcome label
        self.welcome_label = customtkinter.CTkLabel(self.advanced_admin_frame, text=f"Welcome {admin_name}", anchor="center",
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.welcome_label.grid(row=0, column=0, padx=15, pady=15, sticky="nsew")

        # Buttons
        self.reset_all_data_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Reset All\nData", command=self.reset_all_data_event,
                                                             font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.reset_all_data_button.grid(row=1, column=0, padx=15, pady=15, sticky="nsew")

        self.reset_admin_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Reset\n Admin", command=self.reset_admin_event,
                                                          font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.reset_admin_button.grid(row=2, column=0, padx=15, pady=15, sticky="nsew")

        self.reset_student_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Reset\n Students", command=self.reset_student_event,
                                                            font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.reset_student_button.grid(row=3, column=0, padx=15, pady=15, sticky="nsew")

        self.replace_name_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Replace \nStudent Name", command=self.replace_name_event,
                                                           font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.replace_name_button.grid(row=4, column=0, padx=15, pady=15, sticky="nsew")
        
        self.replace_password_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Replace\nPassword", command=self.replace_password_event,
                                                                font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.replace_password_button.grid(row=5, column=0, padx=15, pady=15, sticky="nsew")

        self.add_multiple_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Add Multiple\nStudents", command=self.add_multiple_event,
                                                           font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.add_multiple_button.grid(row=6, column=0, padx=15, pady=15, sticky="nsew")
        
        self.add_admin = customtkinter.CTkButton(self.advanced_admin_frame, text="Add\nAdmin", command=self.add_admin_event,
                                                 font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.add_admin.grid(row=7, column=0, padx=15, pady=15, sticky="nsew")
        
        self.delete_student_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Delete\nStudent", command=self.delete_student_event,
                                                             font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.delete_student_button.grid(row=8, column=0, padx=15, pady=15, sticky="nsew")
        
        self.delete_admin_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Delete\nAdmin", command=self.delete_admin_event,
                                                           font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.delete_admin_button.grid(row=9, column=0, padx=15, pady=15, sticky="nsew")
        
        self.back_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Back", command=self.back_event,
                                                   font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.back_button.grid(row=10, column=0, padx=15, pady=15, sticky="nsew")
        
        self.exit_button = customtkinter.CTkButton(self.advanced_admin_frame, text="Exit", command=self.close_window_event,
                                                   font=customtkinter.CTkFont(family="Roboto", size=17, weight="normal", slant="italic"))
        self.exit_button.grid(row=11, column=0, padx=15, pady=15, sticky="nsew")
            
    def reset_all_data_event(self):
        Student.reset()
        self.show_popup("All data reset.")
    
    def reset_admin_event(self):
        os.system("rm -rf admin.db")
        self.show_popup("Admin data reset.")
    
    def reset_student_event(self):
        os.system("rm -rf students.db")
        self.show_popup("Student data reset.")
    
    def replace_name_event(self):
        self.student.dBManagement.db_update_student(self.student_dropdown.get(), self.new_student_name_entry.get())
        self.show_popup("Student name replaced.")
    
    def replace_password_event(self):
        self.dBAdmin.db_update_admin_password(self.admin_dropdown.get(), self.password_entry.get())
        self.show_popup("Admin password replaced.")
    
    def add_multiple_event(self):
        self.selected_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if self.selected_path:
            self.student.register_multiple_students(self.selected_path)
            self.show_popup("Students added")
        else:
            self.show_popup("No file selected")
    
    def add_admin_event(self):
        self.dBAdmin.db_add_admin(self.add_admin_name_entry.get(), self.add_admin_password_entry.get())
        self.show_popup("Admin added.")
    
    def delete_student_event(self):
        self.student.dBManagement.db_delete_students(self.delete_student_dropdown.get())
        self.show_popup("Student deleted.")
    
    def delete_admin_event(self):
        self.dBAdmin.db_delete_admin(self.delete_admin_dropdown.get())
        self.show_popup("Admin deleted.")
    
    def web_view(self):
        self.show_popup("Web view work in progress.\n Please check back in later iteration.")
    
    def refresh_attendance_event(self):
        self.canvas.get_tk_widget().destroy()
        self.table_frame.destroy()
        self.create_attendance_graphic()
        self.create_attendance_table()
        self.show_popup("Attendance refreshed.")

    def generate_report_event(self):
        self.student.generate_attendance_report()
        self.show_popup("Attendance report generated.")
    
    def register_event(self):
        username = self.reg_username_entry.get()
        password = self.reg_password_entry.get()

        if username and password:
            if len(password) < 8:
                print("Registration failed - password too short")
                self.error_label.configure(text="Password must be at least 8 characters long")
            else:
                self.dBAdmin.db_add_admin(username, password)
                print("Registration successful - username:", username)
                self.registration_frame.destroy()
                self.show_login_frame()
        else:
            print("Registration failed - username or password missing")
            self.error_label.configure(text="Invalid username or password")

    def login_event(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        remember_me = self.remember_me_checkbox.get()

        if self.dBAdmin.db_check_admin(username, password):
            print("Login successful - username:", username)
            print("Remember Me:", remember_me)
            self.error_label.configure(text="")
            self.login_frame.destroy()
            self.show_main_frame()
            self.admin_label.configure(text=f"Welcome\n {username}!")
        else:
            print("Login failed - username:", username)
            self.error_label.configure(text="Invalid username or password")

    def back_event(self):
        self.main_frame.destroy()
        try:
            self.show_advanced_frame.destroy()
        except AttributeError:
            pass
        self.show_login_frame()
        plt.close(self.fig)
        
    def back_event_student(self):
        self.show_student_frame.destroy()
        plt.close(self.fig)
        self.show_login_frame()

    def close_window_event(self):
        plt.close(self.fig)
        self.destroy()
        sys.exit()

if __name__ == '__main__':
    app = App()
    app.mainloop()