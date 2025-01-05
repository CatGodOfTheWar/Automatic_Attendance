import cv2
import numpy as np
from openvino.runtime import Core
import face_recognition
import logging
from PyQt6.QtCore import QThread, pyqtSignal
from DB_management import DBmanagement

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

"""
    This class handles face recognition using a separate thread.
    It captures video frames from the webcam, processes them to recognize faces,
    and emits signals with the frame and recognized attendance information.
    """
class FaceRecognitionThread(QThread):
    # Define signals for frame and attendance
    frame_signal = pyqtSignal(np.ndarray)
    attendance_signal = pyqtSignal(str, str)

    def __init__(self, known_face_encodings, known_face_names, model_path, model_bin):
        try:
            super().__init__()
            self.known_face_encodings = known_face_encodings
            self.known_face_names = known_face_names
            self.model_path = model_path
            self.model_bin = model_bin
            self.cap = self.initialize_webcam()
            self.compiled_model = self.initialize_model(self.model_path, self.model_bin)
            self.input_blob, self.output_blob = self.extract_input_output_blobs(self.compiled_model)
            self.running = True  
            self.db = DBmanagement()
        except Exception as e:
            logging.error(f"Error initializing FaceRecognitionThread: {e}")
            exit(1)

    def initialize_webcam(self):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                logging.error("Error: Could not open webcam.")
                exit(1)
            return cap
        except Exception as e:
            logging.error(f"Error initializing webcam: {e}")
            exit(1)

    def initialize_model(self, model_path, model_bin):
        self.model_path = model_path
        self.model_bin = model_bin
        try:
            ie = Core()
            net = ie.read_model(model=self.model_path, weights=self.model_bin) 
            compiled_model = ie.compile_model(model=net, device_name="MULTI:GPU,CPU")
            logging.info("OpenVINO model loaded and compiled.")
        except Exception as e:
            logging.error(f"Error initializing OpenVINO: {e}")
            exit(1)
        return compiled_model

    def extract_input_output_blobs(self, compiled_model):
        try:
            input_blob = compiled_model.input(0).any_name
            output_blob = compiled_model.output(0).any_name
            return input_blob, output_blob
        except Exception as e:
            logging.error(f"Error extracting input/output blobs: {e}")
            exit(1)

    def run(self):
        skip_frames = 2 
        frame_counter = 0
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    logging.warning("Error: Could not read frame.")
                    break

                # Skip frames based on the counter
                frame_counter += 1
                if frame_counter % (skip_frames + 1) != 0:
                    continue 
            
                # Resize frame only if necessary
                frame_resized = cv2.resize(frame, (672, 384))

                # Prepare input data for inference
                input_data = np.expand_dims(frame_resized.transpose(2, 0, 1), axis=0)

                # Perform inference
                results = self.compiled_model({self.input_blob: input_data})
                detections = results[self.output_blob]

                # Process the results
                for obj in detections[0][0]:
                    confidence = obj[2]
                    if confidence < 0.5:  # Early exit for low confidence
                        continue
                    xmin = int(obj[3] * frame.shape[1])
                    ymin = int(obj[4] * frame.shape[0])
                    xmax = int(obj[5] * frame.shape[1])
                    ymax = int (obj[6] * frame.shape[0])

                    # Skip small or invalid regions
                    if (xmax - xmin) < 20 or (ymax - ymin) < 20:
                        continue

                    # Extract and validate the face ROI
                    face_roi = frame[ymin:ymax, xmin:xmax]
                    if face_roi.size == 0:
                        continue

                    # Process encodings only if face ROI is valid
                    face_encodings = face_recognition.face_encodings(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))
                    if face_encodings:
                        face_encoding = face_encodings[0]
                        matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                        name = "Unknown"
                        if True in matches:
                            first_match_index = matches.index(True)
                            name = self.known_face_names[first_match_index]
                            if self.db.db_record_attendance(name):
                                logging.info(f"Attendance recorded for {name}")
                                self.attendance_signal.emit(name, "recorded")
                            else:
                                logging.info(f"Attendance already recorded for {name} today")
                                self.attendance_signal.emit(name, "already recorded")
                        
                        # Annotate the frame
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (111, 218, 156), 2)
                        cv2.putText(frame, name, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (111, 218, 156), 2)

                # Emit the frame
                self.frame_signal.emit(frame)
                
        except Exception as e:
            logging.error(f"An error occurred during execution: {e}")

        finally:
            self.cap.release()
            logging.info("Resources released, application closed.")

    def stop(self):
        self.running = False
        self.wait()