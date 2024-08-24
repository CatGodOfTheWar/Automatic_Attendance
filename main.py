import logging
from time import sleep
import os
import pandas # type: ignore

from photo_management import PhotoManagement
from recognition import Recognition
from db_management import DBManagement
from db_admin import DBAdmin

import customtkinter
import tkinter.font as tkFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import ttk

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
        
        self.dBAdmin = DBAdmin()
        self.dBAdmin.init_admin_db()

        # Check if admin user exists
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

        # Error message label
        self.error_label = customtkinter.CTkLabel(self.login_frame, text="", text_color="red",
                                                font=customtkinter.CTkFont(family="Roboto", size=22, weight="normal", slant="italic"))
        self.error_label.grid(row=5, column=0, padx=200, pady=(20, 20))

    def show_main_frame(self):
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_label = customtkinter.CTkLabel(self.main_frame, text="CustomTkinter\nMain Page",
                                                font=customtkinter.CTkFont(size=20, weight="bold"))
        self.main_label.grid(row=0, column=1, padx=30, pady=(30, 15))
        self.back_button = customtkinter.CTkButton(self.main_frame, text="Back", command=self.back_event, width=200)
        self.back_button.grid(row=1, column=1, padx=30, pady=(15, 15))
        self.back_button.bind("<Return>", lambda event: self.back_event())
        self.back_button.focus_set()

        self.create_attendance_graphic()
        self.create_attendance_table()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.main_frame.place(relx=0.5, rely=0.45, anchor="center")
      
    def create_attendance_graphic(self):
        # Sample data for attendance
        attendance_data = [10, 20, 30, 40, 50]  # Replace with your actual data
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']  # Replace with your actual labels
        
        primary_color = "#212325"
        border_color = "#3BA55D" 
        
        # Create a figure and a set of subplots with a dark theme
        plt.style.use('grayscale')
        self.fig, self.ax = plt.subplots(figsize=(8, 4)) 
        self.ax.bar(days, attendance_data, color=border_color, edgecolor=primary_color)

        # Set titles and labels with white color
        self.ax.set_title('Attendance Over Days', color=primary_color)
        self.ax.set_xlabel('Days', color=primary_color)
        self.ax.set_ylabel('Number of Attendances', color=primary_color)
        self.ax.tick_params(colors=primary_color)

        # Embed the plot in the Tkinter frame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, rowspan=2, padx=30, pady=(15, 15))
      
    def create_attendance_table(self):
        # Create a table
        attendance_data = [
            ("John Doe", 5, "2023-10-01, 2023-10-02, 2023-10-03, 2023-10-04, 2023-10-05"),
            ("Jane Smith", 3, "2023-10-01, 2023-10-02, 2023-10-03"),
            ("Alice Johnson", 4, "2023-10-01, 2023-10-02, 2023-10-03, 2023-10-04")
        ]  # Replace with your actual data

        # Create a frame for the table
        border_color = "#3BA55D"  # Define a common green color for borders
        table_frame = customtkinter.CTkFrame(self.main_frame, border_color=border_color, border_width=2, corner_radius=10)
        table_frame.grid(row=2, column=0, columnspan=2, padx=30, pady=(15, 15))


        # Create table headers
        headers = ["Username", "Count of Attendance", "Every Date"]
        for col, header in enumerate(headers):
            label = customtkinter.CTkLabel(table_frame, text=header, font=customtkinter.CTkFont(weight="bold"))
            label.grid(row=0, column=col, padx=5, pady=5)

        # Insert data into the table
        for row, (username, count, dates) in enumerate(attendance_data, start=1):
            username_label = customtkinter.CTkLabel(table_frame, text=username)
            username_label.grid(row=row, column=0, padx=5, pady=5)
            count_label = customtkinter.CTkLabel(table_frame, text=count)
            count_label.grid(row=row, column=1, padx=5, pady=5)
            dates_label = customtkinter.CTkLabel(table_frame, text=dates)
            dates_label.grid(row=row, column=2, padx=5, pady=5)

    def on_closing(self):
        plt.close(self.fig)  # Close the matplotlib figure
        self.destroy()  # Close the Tkinter window

    
    def show_student_frame(self):
        pass  

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
        else:
            print("Login failed - username:", username)
            self.error_label.configure(text="Invalid username or password")

    def back_event(self):
        self.main_frame.place_forget()
        self.show_login_frame()
    
    def on_closing(self):
        plt.close(self.fig)  
        self.destroy()

if __name__ == '__main__':
    app = App()
    app.mainloop()