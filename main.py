import sys
import logging
import face_recognition
from recognition import FaceRecognition
from PyQt6.QtWidgets import QApplication
from UI import LoginPage

# Define constants for file paths
MODEL_PATH = "/home/catwarrior/Documents/Python/Teste/Proiect_Final_Python_Versiunea_Noua/intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml"
MODEL_BIN = "/home/catwarrior/Documents/Python/Teste/Proiect_Final_Python_Versiunea_Noua/intel/face-detection-adas-0001/FP16/face-detection-adas-0001.bin"
PHOTO_FILE_PATH = "/home/catwarrior/Documents/Python/Teste/Proiect_Final_Python_Versiunea_Noua"

# Setare logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Student:
    def __init__(self, known_face_encodings, known_face_names, model_path, model_bin):
        self.known_faces_encodings = known_face_encodings
        self.known_names_path = known_face_names
        self.model_path = model_path
        self.model_bin = model_bin
        self.recognition = FaceRecognition(known_face_encodings, known_face_names, model_path, model_bin)
        self.login_page = LoginPage()
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)  # Initialize the QApplication
    person_1 = face_recognition.load_image_file(f"{PHOTO_FILE_PATH}/Andrei.jpg")
    known_face_encodings = [face_recognition.face_encodings(person_1, model='small')[0]]
    know_face_names = ["Andrei"]
    student1 = Student(known_face_encodings, know_face_names, MODEL_PATH, MODEL_BIN)
    #student1.recognition.recognize_faces()
    student1.login_page.show()
    sys.exit(app.exec()) 
    