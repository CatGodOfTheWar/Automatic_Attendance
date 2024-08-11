from time import sleep
from picamera2 import Picamera2, Preview

class PhotoManagement:
        
    def take_picture(self, name, path):
        self.name = name
        self.path = path         
        try:
            self.picam2 = Picamera2()
            self.camera_config = self.picam2.create_preview_configuration(
                                    main={"size": (4096, 2592)},
                                    lores={"size": (640, 480), "format": "YUV420"})
            self.picam2.configure(self.camera_config)
            self.picam2.start_preview(Preview.QT)
            self.picam2.start()
            sleep(5)
            self.picam2.capture_file(f"{self.path}/{self.name}.jpg")
            self.picam2.stop()
        except RuntimeError as e:
            print(f"Failed to acquire camera: {e}")
            print("Retrying in 5 seconds...")
            sleep(5)
            self.take_picture(self.name, self.folder) 
        finally:
            if hasattr(self, 'picam2'):
                self.picam2.close() 