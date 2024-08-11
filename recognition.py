import face_recognition  # type: ignore
import cv2  # type: ignore
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class Recognition:

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

    def check(self, student_img_path, temp_img_path):
        self.student_img_path = student_img_path
        self.temp_img_path = temp_img_path
        self.student_img = self.load_and_convert(self.student_img_path)
        self.temp_img = self.load_and_convert(self.temp_img_path)
        self.student_encoding = self.encode(self.student_img)
        self.temp_encoding = self.encode(self.temp_img)
        if self.student_encoding is not None:
            if self.temp_encoding is not None:
                return face_recognition.compare_faces([self.student_encoding], self.temp_encoding)[0]
            else:
                logging.error("temp_encoding empty")
        else:
            logging.error("student_encoding empty")
        return False
