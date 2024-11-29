import logging
import face_recognition
from recognition import FaceRecognition

# Setare logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class Student:
    def __init__(self, known_face_encodings, known_face_names, model_path, model_bin):
        self.known_faces_encodings = known_face_encodings
        self.known_names_path = known_face_names
        self.model_path = model_path
        self.model_bin = model_bin
        self.recognition = FaceRecognition(known_face_encodings, known_face_names, model_path, model_bin)
        
        

if __name__ == "__main__":
    model_path = "/home/catwarrior/Documents/Python/Teste/intel/face-detection-adas-0001/FP16/face-detection-adas-0001.xml"
    model_bin = "/home/catwarrior/Documents/Python/Teste/intel/face-detection-adas-0001/FP16/face-detection-adas-0001.bin"
    person_1 = face_recognition.load_image_file("/home/catwarrior/Documents/Python/Teste/Andrei.jpg")
    person_2 = face_recognition.load_image_file("/home/catwarrior/Documents/Python/Teste/Ionut.jpg")
    person_3 = face_recognition.load_image_file("/home/catwarrior/Documents/Python/Teste/Cosmin.jpg")
    known_face_encodings = [face_recognition.face_encodings(person_1, model='small')[0], 
                            face_recognition.face_encodings(person_2, model='small')[0],
                            face_recognition.face_encodings(person_3, model='small')[0]]
    know_face_names = ["Andrei", "Ionut", "Gay"]
    student1 = Student(known_face_encodings, know_face_names, model_path, model_bin)
    student1.recognition.recognize_faces()