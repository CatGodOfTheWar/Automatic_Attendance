import cv2
import numpy as np
from openvino.runtime import Core
import face_recognition
import logging

# Set logging configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

class FaceRecognition:
    def __init__(self, known_face_encodings, known_face_names, model_path, model_bin):
        if len(known_face_encodings) != len(known_face_names):
            logging.error("Error: The number of face encodings and names do not match.")
            exit()
        if len(known_face_encodings) == 0:
            logging.error("Error: No face encodings provided.")
            exit()
        if len(known_face_names) == 0:
            logging.error("Error: No names provided.")
            exit()
        if not model_path:
            logging.error("Error: No model path provided.")
            exit()
        if not model_bin:
            logging.error("Error: No model binary path provided.")
            exit()
        self.model_bin = model_bin
        self.model_path = model_path
        self.known_face_encodings = known_face_encodings
        self.known_face_names = known_face_names
        self.cap = self.initialize_webcam()
        self.compiled_model = self.initialize_model(self.model_path, self.model_bin)
        self.input_blob, self.output_blob = self.extract_input_output_blobs(self.compiled_model)
        
    def initialize_webcam(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            logging.error("Error: Could not open webcam.")
            exit()
        return cap
    
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
            exit()
        return compiled_model
        
    def extract_input_output_blobs(self, compiled_model):
        input_blob = compiled_model.input(0).any_name
        output_blob = compiled_model.output(0).any_name
        return input_blob, output_blob
        
    def recognize_faces(self):
        skip_frames = 2 
        frame_counter = 0
        try:
            while True:
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
                        
                        # Annotate the frame
                        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
                        cv2.putText(frame, name, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                cv2.imshow('Video', frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
        except Exception as e:
            logging.error(f"An error occurred during execution: {e}")

        finally:
            self.cap.release()
            cv2.destroyAllWindows()
            logging.info("Resources released, application closed.")