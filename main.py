import subprocess
import logging
from contextlib import contextmanager
from time import sleep
import cv2  # type: ignore
import numpy as np  # type: ignore
from picamera2 import MappedArray, Picamera2, Preview  # type: ignore
import face_recognition  # type: ignore
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Student:
    
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
    
    class PhotoManagement:
        
        def __init__(self, name, path):
            self.name = name
            self.path = path
            logging.debug("Initializing Picamera2")
            try:
                self.picam2 = Picamera2()
                self.camera_config = self.picam2.create_preview_configuration(
                    main={"size": (4096, 2592)},
                    lores={"size": (640, 480), "format": "YUV420"}
                )
                logging.info("Initialization successful.")
            except RuntimeError as e:
                logging.error(f"Camera __init__ sequence did not complete: {e}")
                raise
        
        @contextmanager
        def camera_session(self):
            self.picam2.configure(self.camera_config)
            self.picam2.start_preview(Preview.QTGL)
            self.picam2.start()
            try:
                yield
            finally:
                self.picam2.stop_preview()
                self.picam2.stop()
        
        def take_picture(self):
            with self.camera_session():
                sleep(5)
                self.picam2.capture_file(f"{self.path}/{self.name}.jpg")
            
    class Recognition:
        
        def __init__(self, student_img_path, temp_img_path):
            self.student_img_path = student_img_path
            self.temp_img_path = temp_img_path
            self.student_img = self.load_and_convert(self.student_img_path)
            self.temp_img = self.load_and_convert(self.temp_img_path)
            self.student_encoding = self.encode(self.student_img)
            self.temp_encoding = self.encode(self.temp_img)
            
        def load_and_convert(self, path):
            img = cv2.imread(path)
            if img is not None:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            return img
        
        def encode(self, img):
            if img is not None:
                face_encoding = face_recognition.face_encodings(img)
                if face_encoding:
                    return face_encoding[0]
            return None

        def check(self):
            if self.student_encoding is not None:
                if self.temp_encoding is not None:
                    return face_recognition.compare_faces([self.student_encoding], self.temp_encoding)[0]
                else:
                    logging.error("temp_encoding empty")
            else:
                logging.error("student_encoding empty")
            return False

    def __init__(self, name):
        self.name = name
        
    def add_student_img(self, path):
        self.path = path
        photo_obj = self.PhotoManagement(self.name, self.path)
        photo_obj.take_picture()
    
    def check_student(self, student_img_path, temp_img_path):
        check_obj = self.Recognition(student_img_path, temp_img_path)
        return check_obj.check()

def restart_camera_service():
    try:
        result = subprocess.run(['sudo', 'systemctl', 'restart', 'raspi-config'], capture_output=True, text=True, check=True)
        logging.info("Service restarted successfully")
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error("Failed to restart the service")
        logging.error(e.stderr)

def main():
    while True:
        try:
            folder_p = Student.images_folder()
            folder_t = Student.temporary_folder()
            username = input("Enter your name: ").strip()
            student_obj = Student(username)
            user_input = int(input("Are you registered in the system? (1-yes / 0-no): "))

            if user_input:
                try:
                    student_obj.add_student_img(folder_t)
                except RuntimeError:
                    restart_camera_service()
                    student_obj.add_student_img(folder_t)
                if student_obj.check_student(f"{folder_p}/{username}.jpg", f"{folder_t}/{username}.jpg"):
                    print(f"You're {username}")
                else:
                    print(f"You're not {username}")
            else:
                student_obj.add_student_img(folder_p)
        except Exception as e:
            logging.error(f"An error occurred: {e}")
            restart_camera_service()

if __name__ == '__main__':
    main()
