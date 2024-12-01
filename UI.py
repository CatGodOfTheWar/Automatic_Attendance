import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, 
    QVBoxLayout, QHBoxLayout, QApplication, 
    QSpacerItem, QSizePolicy
)
import logging
from db_amin import DBAdmin

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Define constants for file paths
STYLE_PATH_LOGIN = "/home/catwarrior/Documents/Python/Teste/Proiect_Final_Python_Versiunea_Noua/style.qss"
STYLE_PATH_ADMIN = "/home/catwarrior/Documents/Python/Teste/Proiect_Final_Python_Versiunea_Noua/style_admin.qss"
ICON_PATH = "/home/catwarrior/Documents/Python/Teste/Proiect_Final_Python_Versiunea_Noua/cat-2.png"
USERNAME_ICON_PATH = "/home/catwarrior/Documents/Python/Teste/Proiect_Final_Python_Versiunea_Noua/username.png"
PASSWORD_ICON_PATH = "/home/catwarrior/Documents/Python/Teste/Proiect_Final_Python_Versiunea_Noua/password.png"

class LoginPage(QWidget):
    def __init__(self):
        super().__init__()
        super().__init__()
        self.main_layout = QVBoxLayout()  
        self.setLayout(self.main_layout)  
        self.db_admin = DBAdmin()
        self.db_admin.db_connect()
        self.db_admin.init_admin_db()   
        self.login_page()  

    def login_page(self):
        try:
            self.setWindowTitle("Attendance System")
            self.setFixedSize(600, 800) 
            self.setStyleSheet(open(STYLE_PATH_LOGIN, "r").read())
            self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.setContentsMargins(100, 0, 100, 0)
            self.clear_layout(self.main_layout)

            self.add_icon(self.main_layout, ICON_PATH, 250)
            self.add_spacer(self.main_layout, 100)

            self.username_input = self.create_input_field(self.main_layout, USERNAME_ICON_PATH, "Username")
            self.password_input = self.create_input_field(self.main_layout, PASSWORD_ICON_PATH, "Password", is_password=True)

            self.add_spacer(self.main_layout, 30)
            self.create_button(self.main_layout, "Log In", self.login, "loginButton")
            self.add_spacer(self.main_layout, 15)
            self.create_button(self.main_layout, "Sign Up", self.register, "registerButton")

        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

    def admin_page(self):
        try:
            self.setWindowTitle("Admin Dashboard")
            self.setFixedSize(600, 800) 
            self.setStyleSheet(open(STYLE_PATH_ADMIN, "r").read())

            self.clear_layout(self.main_layout)

            self.add_icon(self.main_layout, ICON_PATH, 250)

            label = QLabel("Welcome to the Admin Dashboard")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.main_layout.addWidget(label)

            logout_button = QPushButton("Log Out")
            logout_button.setFixedHeight(50)
            logout_button.clicked.connect(self.logout)
            self.main_layout.addWidget(logout_button)

        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

    def add_icon(self, layout, path, size, alignment=Qt.AlignmentFlag.AlignCenter):
        try:
            icon_label = QLabel()
            pixmap = QPixmap(path)
            if pixmap.isNull():
                logging.error(f"Error: Could not load image from path {path}")
            else:
                scaled_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.IgnoreAspectRatio, Qt.TransformationMode.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(icon_label)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

    def add_spacer(self, layout, height):
        try:
            spacer = QSpacerItem(0, height, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
            layout.addSpacerItem(spacer)
        except Exception as e: 
            logging.error(f"Error: {e}")
            sys.exit(1)

    def create_input_field(self, layout, icon_path, placeholder, is_password=False):
        try:
            input_layout = QHBoxLayout()
            icon_label = QLabel()
            icon_label.setPixmap(QIcon(icon_path).pixmap(40, 40))
            input_layout.addWidget(icon_label)
            
            input_field = QLineEdit()
            input_field.setFixedHeight(50)
            input_field.setPlaceholderText(placeholder)
            if is_password:
                input_field.setEchoMode(QLineEdit.EchoMode.Password)
            input_layout.addWidget(input_field)
            layout.addLayout(input_layout)

            return input_field
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)

    def create_button(self, layout, text, callback, object_name=None):
        try:
            button_layout = QHBoxLayout()
            button = QPushButton(text)
            button.setFixedHeight(60)
            button.setFixedWidth(400)
            if object_name:
                button.setObjectName(object_name)
            button.clicked.connect(callback)
            button_layout.addWidget(button, alignment=Qt.AlignmentFlag.AlignCenter)
            layout.addLayout(button_layout)
        except Exception as e:
            logging.error(f"Error: {e}")
            sys.exit(1)
            
            
    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        if self.db_admin.db_admin_exists():
            if self.db_admin.db_check_admin(username, password):
                self.clear_layout(self.layout())  
                self.admin_page() 
            else:
                print("Invalid credentials")

    def register(self):
        print("Register button clicked")
        username = self.username_input.text()
        password = self.password_input.text()
        self.db_admin.db_add_admin(username, password)
        
    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater() 
                elif child.layout():
                    self.clear_layout(child.layout()) 
    
    def logout(self):
        self.clear_layout(self.layout())
        self.login_page()  

           


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login_page = LoginPage()
    login_page.show()
    sys.exit(app.exec())