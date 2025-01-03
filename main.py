import sys
import logging
from PyQt6.QtWidgets import QApplication
from UI import MainApp

# Configure logging to display information with timestamp and log level
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Student:
    def __init__(self):
        self.main_app = MainApp()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    student = Student()
    student.main_app.show()
    try:
        sys.exit(app.exec())
    except Exception as e:
        logging.error(f"An error occurred: {e}")
   