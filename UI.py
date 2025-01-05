import sys
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QIcon, QImage, QPixmap
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QApplication, 
    QSpacerItem, QSizePolicy, QComboBox,
    QDialog, QFileDialog)
import logging
import os.path
import re
import cv2
import numpy as np
from datetime import datetime
import pandas as pd
import subprocess
import psutil
import face_recognition
from DB_admin import DBAdmin
from DB_management import DBmanagement
from recognition import FaceRecognitionThread

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define constants for file paths and other configurations
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Create the data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Create the reports directory if it doesn't exist
if not os.path.exists(REPORTS_DIR):
    os.makedirs(REPORTS_DIR)

STYLE_PATH_LOGIN = os.path.join(BASE_DIR, "style_sheets", "style.qss")
STYLE_PATH_ADMIN = os.path.join(BASE_DIR, "style_sheets", "style_admin.qss")
STYLE_PATH_STUDENT = os.path.join(BASE_DIR, "style_sheets", "style_student.qss")
ICON_PATH = os.path.join(BASE_DIR, "icons", "cat-2.png")
USERNAME_ICON_PATH = os.path.join(BASE_DIR, "icons", "username.png")
PASSWORD_ICON_PATH = os.path.join(BASE_DIR, "icons", "password.png")
DB_ADMIN_PATH = os.path.join(DATA_DIR, "admin.db")
DB_STUDENT_PATH = os.path.join(DATA_DIR, "students.db")
MODEL_PATH = os.path.join(BASE_DIR, "intel", "face-detection-adas-0001", "FP16", "face-detection-adas-0001.xml")
MODEL_BIN = os.path.join(BASE_DIR, "intel", "face-detection-adas-0001", "FP16", "face-detection-adas-0001.bin")
PHOTO_FILE_PATH = os.path.join(BASE_DIR, "imgs")

"""
    MainLayoutCore is a base class that provides various utility methods 
    for creating and managing UI components such as buttons, labels, 
    input fields, icons, dropdowns, and layouts. It also includes methods 
    for clearing layouts and handling file selection dialogs.
"""
class MainLayoutCore(QWidget):
# Method to create a button and add it to the layout
    def create_button(self, layout, text, callback, alignment=Qt.AlignmentFlag.AlignCenter, object_name=None, height=60, width=400):
        try:
            button_layout = QHBoxLayout()
            button = QPushButton(text)
            button.setFixedHeight(height)
            button.setFixedWidth(width)
            if object_name:
                button.setObjectName(object_name)
            button.clicked.connect(callback)
            button_layout.addWidget(button, alignment)
            layout.addLayout(button_layout)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

# Method to create a label and add it to the layout
    def create_label(self, layout, text, alignment=Qt.AlignmentFlag.AlignCenter, object_name=None):
        try:
            label = QLabel(text)
            if object_name:
                label.setObjectName(object_name)
            label.setAlignment(alignment)
            layout.addWidget(label)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

# Method to create an input field and add it to the layout
    def create_input_field(self, layout, icon_path, placeholder, has_icon=False, is_password=False, object_name=None, height=50, width=200):
        try:
            input_layout = QHBoxLayout()
            icon_label = QLabel()
            if has_icon: 
                icon_label.setPixmap(QIcon(icon_path).pixmap(40, 40))
                input_layout.addWidget(icon_label)
            input_field = QLineEdit()
            input_field.setFixedHeight(height)
            input_field.setFixedWidth(width)
            if object_name:
                input_field.setObjectName(object_name)
            input_field.setPlaceholderText(placeholder)
            if is_password:
                input_field.setEchoMode(QLineEdit.EchoMode.Password)
            input_layout.addWidget(input_field)
            layout.addLayout(input_layout)
            return input_field
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to add an icon to the layout           
    def add_icon(self, layout, path, size, alignment=any, object_name=None):
        try:
            icon_label = QLabel()
            pixmap = QPixmap(path)
            if pixmap.isNull():
                logging.error(f"Error: Could not load image from path {path}")
            else:
                scaled_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            icon_label.setAlignment(alignment)
            layout.addWidget(icon_label)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

# Method to create a dropdown and add it to the layout
    def create_dropdown(self, layout, items, width=None, height=None, alignment=Qt.AlignmentFlag.AlignCenter, object_name=None):
        dropdown = QComboBox()
        dropdown.addItems(items)
        if object_name:
            dropdown.setObjectName(object_name)
        if width and height:
            dropdown.setFixedSize(width, height)
        layout.addWidget(dropdown, alignment=alignment)
        return dropdown

# Method to add a spacer to the layout
    def add_spacer(self, layout, height):
        try:
            spacer = QSpacerItem(0, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            layout.addSpacerItem(spacer)
        except Exception as e: 
            logging.error(f"Error: {e}")
            sys.exit(1)
     
# Method to set a horizontal layout and add it to the parent layout            
    def set_h_layout(self, layout, alignment=Qt.AlignmentFlag.AlignCenter, object_name=None):
        h_layout = QHBoxLayout()
        widget = QWidget()
        widget.setObjectName(object_name)
        widget.setLayout(h_layout)
        h_layout.setAlignment(alignment)
        layout.addWidget(widget)
        return h_layout
    
# Method to set a vertical layout and add it to the parent layout    
    def set_v_layout(self, layout, alignment=Qt.AlignmentFlag.AlignCenter, object_name=None):
        v_layout = QVBoxLayout()
        widget = QWidget()
        widget.setObjectName(object_name)
        widget.setLayout(v_layout)
        v_layout.setAlignment(alignment)
        layout.addWidget(widget)
        return v_layout
    
# Method to clear all widgets from a layout    
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater() 
                elif child.layout():
                    self.clear_layout(child.layout()) 
   
# Method to open a file selection dialog and return selected file paths                    
    def selection_window(self, file_type="Images (*.png *.xpm *.jpg *.jpeg);;All Files (*)" , window_title="Select Photos"):
        options = QFileDialog.Option.DontUseNativeDialog
        file_paths, _ = QFileDialog.getOpenFileNames(self, window_title, "", file_type, options=options)
        if file_paths:
            return file_paths

"""
    PopUpWindow is a class that creates a pop-up dialog window for displaying messages.
    It inherits from QDialog and MainLayoutCore to utilize their functionalities.
"""
class PopUpWindow(QDialog, MainLayoutCore):
    def __init__(self):
        try:
            super().__init__()
            self.db_student = DBmanagement()
            self.db_student.db_connect()
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
        
    # Method to display an alert window with a message    
    def alertWindow(self, message = "Alert Window", object_name = None, height=300, width=200):
        try:
            self.message = message
            self.object_name = object_name
            self.height = height
            self.width = width
            self.setWindowTitle('Pop-Up Window')
            self.setFixedSize(self.height, self.width)
            layout = QVBoxLayout()
            self.create_label(layout, self.message, alignment=Qt.AlignmentFlag.AlignCenter, object_name=self.object_name)
            self.setLayout(layout)
            with open(STYLE_PATH_ADMIN, "r") as file:
                self.setStyleSheet(file.read())
            QTimer.singleShot(1500, self.close)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

"""
    MainApp is the main application class that initializes the UI and handles 
    the login, admin, and student pages. It inherits from MainLayoutCore to 
    utilize its UI component creation methods.
"""
class MainApp(MainLayoutCore):
    def __init__(self):
        try:
            super().__init__()
            self.main_layout = QVBoxLayout()  
            self.setLayout(self.main_layout)  
            self.db_admin = DBAdmin()
            self.db_admin.db_connect() 
            self.db_admin.init_admin_db() 
            self.db_student = DBmanagement()
            self.db_student.db_connect()
            self.db_student.db_students_init()
            self.login_page(Qt.AlignmentFlag.AlignCenter)
            self.face_recognition_thread = None
            self.is_login_page = True  
            self.failed_login_attempts = 0
            global admin
            global student_name
        except Exception as e:
            logging.error(f"Error: {e}")
    
# Method to display a pop-up window with a message    
    def login_page(self, alignment=any):
        self.is_login_page = True
        try:
            self.setWindowTitle("Attendance System")
            self.setFixedSize(600, 800) 
            with open(STYLE_PATH_LOGIN, "r") as file:
                self.setStyleSheet(file.read())
            self.main_layout.setAlignment(alignment)
            self.main_layout.setContentsMargins(100, 0, 100, 0)
            self.clear_layout(self.main_layout)

            self.add_icon(self.main_layout, ICON_PATH, 250, alignment)
            self.add_spacer(self.main_layout, 100)

            self.create_input_field(self.main_layout, USERNAME_ICON_PATH, "Username",has_icon=True, object_name="inputLabelUsername", height=50, width=350)
            self.create_input_field(self.main_layout, PASSWORD_ICON_PATH, "Password",has_icon=True, is_password=True, object_name="inputLabelPassword", height=50, width=350)

            self.add_spacer(self.main_layout, 30)
            self.create_button(self.main_layout, "Log In", self.login, Qt.AlignmentFlag.AlignCenter, "loginButton")
            if not self.db_admin.db_admin_exists():
                print(self.db_admin.db_admin_exists())
                self.add_spacer(self.main_layout, 15)
                self.create_button(self.main_layout, "Sign Up", self.register, Qt.AlignmentFlag.AlignCenter, "registerButton")  
        except Exception as e:
            logging.error(f"Error: {e}")
  
# Method to display the admin page        
    def admin_page(self, name, alignment=any):
        self.is_login_page = False
        self.name = name
        try:
            self.setWindowTitle(f"Admin Panel for Attendance System")
            self.setFixedSize(600, 800)
            with open(STYLE_PATH_ADMIN, "r") as file:
                self.setStyleSheet(file.read())
            dropdown_items = self.show_student_db()
            
            h_layout_name = self.set_h_layout(self.main_layout, alignment, "hLayoutName")
            self.add_icon(h_layout_name, ICON_PATH, 100, alignment)
            self.create_label(h_layout_name, f"Welcome Back \n {self.name}", alignment, "nameLabel")
            self.add_spacer(self.main_layout, 10)
            
            h_layout_add_student = self.set_h_layout(self.main_layout, alignment, "hLayoutAddStudent")
            self.create_button(h_layout_add_student, "Add \n Names", self.add_student_name, Qt.AlignmentFlag.AlignCenter, "addStudentButton", 50, 120)
            self.create_button(h_layout_add_student, "Add \n Pictures", self.add_student_picture, Qt.AlignmentFlag.AlignCenter, "addStudentButton", 50, 120)
            self.create_button(h_layout_add_student, "Student \nMode", self.show_student_page, Qt.AlignmentFlag.AlignCenter, "studentModeButton", 50, 120)
            self.add_spacer(self.main_layout, 10)
            
            h_layout_delete_student = self.set_h_layout(self.main_layout, alignment, "hLayoutDeleteStudent")
            self.create_button(h_layout_delete_student, "Delete", self.delete_student, Qt.AlignmentFlag.AlignCenter, "deleteStudentButton", 50, 120)
            self.create_dropdown(h_layout_delete_student, dropdown_items, width=250, height=50, alignment=Qt.AlignmentFlag.AlignCenter, object_name="dropdownMenu")
            self.add_spacer(self.main_layout, 10)
            
            h_layout_replace_name_student = self.set_h_layout(self.main_layout, alignment, "hLayoutReplaceStudentName")
            self.create_button(h_layout_replace_name_student, "Replace", self.replace_name, Qt.AlignmentFlag.AlignCenter, "replaceNameStudentButton", 60, 120)
            v_layout_replace_name_student = self.set_v_layout(h_layout_replace_name_student, alignment, "vLayoutReplaceStudentName")
            
            self.create_dropdown(v_layout_replace_name_student, dropdown_items, width=240, height=50, alignment=Qt.AlignmentFlag.AlignCenter, object_name="dropdownMenuReplace")
            self.create_input_field(v_layout_replace_name_student, None ,"Student Name", object_name="inputLabelReplace", height=50, width=240)
            self.add_spacer(self.main_layout, 10)
            
            h_layout_data = self.set_h_layout(self.main_layout, alignment, "hLayoutData")
            self.create_button(h_layout_data, "Add \nData", self.add_data, Qt.AlignmentFlag.AlignCenter, "dataButton", 60, 120)
            v_layout_data = self.set_v_layout(h_layout_data, alignment, "vLayoutData")
            self.create_dropdown(v_layout_data, dropdown_items, width=220, height=50, alignment=Qt.AlignmentFlag.AlignCenter, object_name="dropdownMenuData")
            self.create_input_field(v_layout_data, None ,"YYYY-MM-DD", object_name="inputLabelData", height=50, width=220)
            self.add_spacer(self.main_layout, 10)
            
            h_layout_web_server = self.set_h_layout(self.main_layout, alignment, "hLayoutWebServer")
            self.create_button(h_layout_web_server, "Open Server", self.open_server, Qt.AlignmentFlag.AlignCenter, "webServerButton", 50, 180)
            self.create_button(h_layout_web_server, "Check Complaints", self.check_complaints, Qt.AlignmentFlag.AlignCenter, "webServerButton", 50, 180)
            self.add_spacer(self.main_layout, 10)
            
            h_layout_logout = self.set_h_layout(self.main_layout, alignment, "hLayoutLogout")
            self.create_button(h_layout_logout, "Delete All", self.delete_all_data, Qt.AlignmentFlag.AlignCenter, "logoutButton", 50, 120)
            self.create_button(h_layout_logout, "Log Out", self.logout, Qt.AlignmentFlag.AlignCenter, "logoutButton", 50, 120)
            self.create_button(h_layout_logout, "Generate \n Report", self.report, Qt.AlignmentFlag.AlignCenter, "logoutButton", 50, 120)

        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
   
# Method to display the student page            
    def student_page(self, alignment=Qt.AlignmentFlag.AlignCenter):
        try:
            self.setWindowTitle(f"Student Panel for Attendance System")
            self.setFixedSize(600, 800)
            with open(STYLE_PATH_STUDENT, "r") as file:
                self.setStyleSheet(file.read())

            v_layout = self.set_v_layout(self.main_layout, alignment=alignment, object_name='vLayoutStudent')

            h_layout_name = self.set_h_layout(v_layout, alignment, "hLayoutName")
            self.add_icon(h_layout_name, ICON_PATH, 100, alignment)
            self.create_label(h_layout_name, "Welcome students,\n look at the camera", alignment, "titleLabel")

            v_layout.addLayout(h_layout_name)
            self.add_spacer(v_layout, 10)

            self.video_label = QLabel(self)
            self.video_label.setAlignment(alignment)
            self.video_label.setFixedSize(380, 480)
            self.video_label.setObjectName("videoLabel")
            v_layout.addWidget(self.video_label)
            self.add_spacer(v_layout, 10)
            self.create_button(self.main_layout, "Log Out", self.logout, Qt.AlignmentFlag.AlignCenter, "LogoutButton", width=380, height=60)

            self.start_video_feed()
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
 
# Method to login the admin
    def login(self):
        try:
            self.username = self.findChild(QLineEdit, "inputLabelUsername").text().strip()
            self.password = self.findChild(QLineEdit, "inputLabelPassword").text().strip()
            if self.db_admin.db_admin_exists() or not os.path.exists(DB_ADMIN_PATH):
                if self.db_admin.db_check_admin(self.username, self.password):
                    self.clear_layout(self.layout())  
                    self.admin_page(self.username, Qt.AlignmentFlag.AlignCenter) 
                    self.failed_login_attempts = 0
                else:
                    self.failed_login_attempts += 1 
                    self.clear_layout(self.layout())
                    self.login_page(Qt.AlignmentFlag.AlignCenter)
                    if self.failed_login_attempts == 2:
                        self.create_label(self.layout(), f"Invalid credentials\nYou have {3 - self.failed_login_attempts} attempt left!", Qt.AlignmentFlag.AlignCenter, "errorLabel")
                    else:
                        self.create_label(self.layout(), f"Invalid credentials\nYou have {3 - self.failed_login_attempts} attempts left!", Qt.AlignmentFlag.AlignCenter, "errorLabel")
                    if self.failed_login_attempts == 3:
                        sys.exit(1)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
      
# Method to register a admin                       
    def register(self):
        try:
            self.username = self.findChild(QLineEdit, "inputLabelUsername").text().strip()
            self.password = self.findChild(QLineEdit, "inputLabelPassword").text().strip()
            if self.password_complexity(self.password)[0]:
                self.db_admin.db_add_admin(self.username, self.password)
                self.clear_layout(self.layout())
                self.login_page(Qt.AlignmentFlag.AlignCenter)
                self.showPopUp('Admin added\nsuccessfully', 'registerPop')
                return True
            else:
                self.clear_layout(self.layout())
                self.login_page(Qt.AlignmentFlag.AlignCenter)
                self.add_spacer(self.layout(), 10)
                self.create_label(self.layout(), self.password_complexity(self.password)[1], Qt.AlignmentFlag.AlignCenter, "errorLabel")
            return False
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to check the password complexity        
    def password_complexity(self, password):
        try:
            if len(password) < 8:
                return [False, "Password too short"]
            if not re.search(r"[A-Z]", password):
                return [False, "Password needs uppercase letter"]
            if not re.search(r"[a-z]", password):
                return [False, "Password needs lowercase letter"]
            if not re.search(r"[0-9]", password):
                return [False, "Password needs number"]
            if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
                return [False, "Password needs special character"]
            return [True, "Password is strong"]
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
   
# Method to add student names to the database    
    def add_student_name(self):
        try:
            global admin
            txt_file = self.selection_window("Text Files (*.txt);;All Files (*)", "Select Names")
            if txt_file:
                if isinstance(txt_file, list):
                    txt_file = txt_file[0] 
                with open(txt_file, 'r') as file:
                    names = file.readlines()
                    for name in names:
                        name = name.strip()
                        if not self.db_student.db_check_student(name):
                            self.db_student.db_add_student(name)
                    self.clear_layout(self.layout())
                    self.admin_page(self.username, Qt.AlignmentFlag.AlignCenter)
                    self.showPopUp('Names added\nsuccessfully', 'addPop')
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to add student pictures to the folder    
    def add_student_picture(self):
        try:
            if not os.path.exists(PHOTO_FILE_PATH):
                os.makedirs(PHOTO_FILE_PATH, exist_ok=True)
            images_paths = self.selection_window("Images (*.png *.xpm *.jpg *.jpeg);;All Files (*)", "Select Photos")
            print(images_paths)
            for img in images_paths:
                img_name = os.path.basename(img)
                if not os.path.exists(f"{PHOTO_FILE_PATH}/{img_name}"):
                    os.system(f"mv {img} {PHOTO_FILE_PATH}")
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
   
# Method to delete the student from the database    
    def delete_student(self):
        try:
            student_name = self.findChild(QComboBox, "dropdownMenu").currentText()
            if student_name:
                self.db_student.db_delete_students(student_name)
                self.clear_layout(self.layout())
                self.admin_page(self.username, Qt.AlignmentFlag.AlignCenter) 
                self.showPopUp('Student deleted\nsuccessfully', 'deletePop')
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
  
# Method to replace the student name in the database    
    def replace_name(self):
        try:
            old_student_name = self.findChild(QComboBox, "dropdownMenuReplace").currentText()
            new_student_name = self.findChild(QLineEdit, "inputLabelReplace").text().strip()
            if len(new_student_name) > 1:
                self.db_student.db_update_student(old_student_name, new_student_name)
                self.clear_layout(self.layout())
                self.admin_page(self.username, Qt.AlignmentFlag.AlignCenter) 
                self.showPopUp('Name replaced\nsuccessfully', 'replacePop')
            else: 
                self.showPopUp('Name input empty', 'replacePop')
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
   
# Method to show the student page                  
    def show_student_page(self):
        try:
            self.clear_layout(self.main_layout)
            self.showPopUp('Wait to load', 'studentLoad')
            self.student_page(Qt.AlignmentFlag.AlignCenter)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to start the video feed for face recognition            
    def start_video_feed(self):
        try:
            known_face_encodings = []
            known_face_names = []
            students = self.db_student.db_get_students()
            for student in students:
                if student[1] not in known_face_names:
                    known_face_names.append(student[1])
            print(known_face_names)

            for name in known_face_names:
                try:
                    photo_path = f"{PHOTO_FILE_PATH}/{name}.jpg"
                    self.showPopUp(f"Loading image\n for {name}", 'loadPop')
                    photo_load = face_recognition.load_image_file(photo_path)
                    photo_encodings = face_recognition.face_encodings(photo_load, model='small')
                    if photo_encodings:
                        known_face_encodings.append(photo_encodings[0])
                    else:
                        logging.error(f"No face encodings found for {name}")
                except Exception as e:
                    logging.error(f"Error processing {name}: {e}")
            
            self.face_recognition_thread = FaceRecognitionThread(known_face_encodings, known_face_names, MODEL_PATH, MODEL_BIN)
            self.face_recognition_thread.attendance_signal.connect(self.show_attendance_popup)
            self.face_recognition_thread.frame_signal.connect(self.update_video_frame)
            self.face_recognition_thread.start()
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

# Method to update the video frame for face recognition
    def update_video_frame(self, frame):
        try:
            # Convert the frame to QImage and display it
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            if self.video_label is not None:
                self.video_label.setPixmap(QPixmap.fromImage(qt_image))
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

# Method to stop the video feed for face recognition
    def stop_video_feed(self):
        try:
            if self.face_recognition_thread is not None:
                self.face_recognition_thread.stop()
                self.face_recognition_thread = None
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
   
# Method to add data to the database   
    def add_data(self):
        try:
            student_name = self.findChild(QComboBox, "dropdownMenuData").currentText()
            data = self.findChild(QLineEdit, "inputLabelData").text().strip()
            try:
                date = datetime.strptime(data, "%Y-%m-%d").strftime("%Y-%m-%d")
            except ValueError:
                self.showPopUp('Invalid format', 'dataPop')
                return
            success = self.db_student.db_record_manual_attendance(student_name, date)
            if success:
                self.clear_layout(self.layout())
                self.admin_page(self.username, Qt.AlignmentFlag.AlignCenter) 
                self.showPopUp('Attendance Added', 'dataPop')
            else:
                self.showPopUp('Attendance\nexists', 'dataPop')
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to check if the server is running    
    def is_server_running(self, script_name):
        try:
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                if script_name in proc.info['cmdline']:
                    return True
            return False
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to open the server    
    def open_server(self):
        try:
            if not self.is_server_running(f'{BASE_DIR}/web_server.py'):
                self.showPopUp('User Fingerprint\n or Password', 'serverPop')
                subprocess.Popen(['python3', f'{BASE_DIR}/web_server.py'])
            else:
                self.showPopUp('Server is \nalready running', 'serverPop')
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to check the complaints    
    def check_complaints(self):
        self.showPopUp('Work in progress', 'complaintPop')
    
# Method to delete all data    
    def delete_all_data(self):
        try:
            os.system(f"rm -rf images_folder/*")
            os.system("rm -rf students.db")
            os.system("rm -rf admin.db")
            os.system("rm -rf attendance_report.xlsx")
            self.showPopUp('All data deleted \n  successfully', 'deletePop')
            sys.exit(1)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
      
# Method to generate a report in excel format        
    def report(self):
        try:
            attendance_data = self.db_student.db_get_attendance()
            dataFrame = pd.DataFrame(attendance_data, columns=['student_name', 'date'])
            dataFrame['date'] = dataFrame['date'].fillna("")
            groupData = dataFrame.groupby('student_name').agg({
                'date': [lambda x: max(0, len(x) - 1), lambda x: list(x)]
            }).reset_index()
            groupData.columns = ['student_name', 'attendance_count', 'dates']
            report_data = groupData.to_dict(orient='records')
            for record in report_data:
                record['dates'] = " ; ".join(record['dates'][1:])
            report_df = pd.DataFrame(report_data)
            report_path = os.path.join(REPORTS_DIR, 'attendance_report.xlsx')
            report_df.to_excel(report_path, index=False)
            self.showPopUp('Report generated \n  successfully', 'raportPop')
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
      
# Method to show the student names from the database        
    def show_student_db(self):
        try:
            attendance_data = self.db_student.db_get_attendance()
            dataFrame = pd.DataFrame(attendance_data, columns=['student_name', 'date'])
            dataFrame['date'] = dataFrame['date'].fillna("")
            groupData = dataFrame.groupby('student_name').agg({
                'date': [lambda x: max(0, len(x) - 1), lambda x: list(x)]
            }).reset_index()
            groupData.columns = ['student_name', 'attendance_count', 'dates']
            student_names = groupData['student_name'].tolist()
            return student_names
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)   
    
# Method to show a pop-up window with a message
    def showPopUp(self, message, object_name=None):
        try:
            popUp = PopUpWindow()
            popUp.alertWindow(message, object_name)
            popUp.exec()
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to show the attendance status in a pop-up window        
    def show_attendance_popup(self, name, status):
        try:
            if status == "recorded":
                self.showPopUp(f"Attendance recorded", "attendanceStatus")
            elif status == "already recorded":
                self.showPopUp(f"Attendance already \nrecorded for today", "attendanceStatus")
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
    
# Method to logout the admin
    def logout(self):
            try:
                self.stop_video_feed()
                self.clear_layout(self.layout())
                self.login_page(Qt.AlignmentFlag.AlignCenter)
            except Exception as e:
                logging.error(f"Error during logout: {e}")
                sys.exit(1)
     
# Method to handle key press events        
    def keyPressEvent(self, event):
        try:
            if self.is_login_page and event.key() == 16777220: 
                self.login()
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)