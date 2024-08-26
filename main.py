import logging
from time import sleep
import os
import pandas # type: ignore
import sys
from photo_management import PhotoManagement
from recognition import Recognition
from db_management import DBManagement
from db_admin import DBAdmin

import customtkinter
import tkinter.font as tkFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk

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
        dataFrame = pandas.DataFrame(attendance_data, columns=['student_name', 'date'])
        dataFrame = dataFrame[dataFrame['date'].notna()]
        groupData = dataFrame.groupby('student_name').agg({
            'date': ['count', lambda x: list(x)]
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
        self.generate_report = customtkinter.CTkButton(self.side_frame, text="Generate Report", command=self.student.generate_attendance_report, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.refresh = customtkinter.CTkButton(self.side_frame, text="Refresh", command=self.refresh_attendance_event, corner_radius=20,
                                                    font=customtkinter.CTkFont(family="Roboto", size=25, weight="normal", slant="italic"))
        self.web_view = customtkinter.CTkButton(self.side_frame, text="Web View", command=self.web_view, corner_radius=20,
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
        self.web_view.grid(row=5, column=0, padx=15, pady=15, sticky="nsew")
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
        students =   [0] * 15
        attendance = list(range(1,16))  
        db_content = self.student.show_student_db()
        
        for row in db_content:
            index = row[1]  - 1
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
        self.main_frame.place_forget()  
        self.show_student_frame = customtkinter.CTkFrame(self, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.show_student_frame.place(relx=0.5, rely=0.47, anchor="center")
        
    
    def show_advanced_settings(self):
        self.main_frame.place_forget()
        self.show_advanced_frame = customtkinter.CTkFrame(self, corner_radius=20, border_width=2, border_color="#3BA55D")
        self.show_advanced_frame.place(relx=0.5, rely=0.47, anchor="center")
    
    def web_view(self):
        pass
    
    def refresh_attendance_event(self):
        self.canvas.get_tk_widget().grid_forget()
        self.table_frame.grid_forget()
        self.create_attendance_graphic()
        self.create_attendance_table()

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
                self.registration_frame.place_forget()
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
            self.login_frame.place_forget()
            self.show_main_frame()
            self.admin_label.configure(text=f"Welcome\n {username}!")
        else:
            print("Login failed - username:", username)
            self.error_label.configure(text="Invalid username or password")

    def back_event(self):
        self.main_frame.place_forget()
        self.show_login_frame()

    def close_window_event(self):
        plt.close(self.fig)
        self.destroy()
        sys.exit()

if __name__ == '__main__':
    app = App()
    app.mainloop()