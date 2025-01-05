# Attendance Management System

## Overview

The Attendance Management System is a comprehensive application designed to manage student attendance using face recognition technology. The system provides an intuitive user interface for both administrators and students, ensuring seamless attendance tracking and reporting.

## Features

- **Admin Panel**: Allows administrators to manage student data, add student names and pictures, generate attendance reports, and delete data.
- **Student Panel**: Enables students to log their attendance by simply looking at the camera.
- **Face Recognition**: Utilizes OpenVINO and face_recognition libraries for accurate face detection and recognition.
- **Attendance Reports**: Generates detailed attendance reports in Excel format.
- **Pop-Up Notifications**: Provides real-time feedback and notifications through pop-up windows.

## Project Structure

```plaintext
.
├── __pycache__/
├── data/
│   ├── admin.db
│   ├── students.db
├── reports/
│   ├── attendance_report.xlsx
├── DB_admin.py
├── DB_management.py
├── icons/
├── imgs/
├── intel/
│   ├── face-detection-adas-0001/
│   │   ├── FP16/
│   │   │   ├── face-detection-adas-0001.xml
│   │   │   ├── face-detection-adas-0001.bin
│   │   ├── FP32/
│   │       ├── face-detection-adas-0001.xml
│   │       ├── face-detection-adas-0001.bin
├── main.py
├── README.md
├── recognition.py
├── style_sheets/
│   ├── style_admin.qss
│   ├── style_student.qss
│   ├── style.qss
├── templates/
│   ├── index.html
├── UI.py
├── web_server.py
```

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/attendance-management-system.git
    cd attendance-management-system
    ```

2. **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

3. **Download OpenVINO models**:
    - Place the `face-detection-adas-0001.xml` and `face-detection-adas-0001.bin` files in the [FP16](http://_vscodecontentref_/14) directory.

## Usage

1. **Run the application**:
    ```sh
    python main.py
    ```

2. **Admin Panel**:
    - Log in with your admin credentials.
    - Manage student data, add pictures, generate reports, and more.

3. **Student Panel**:
    - Students can log their attendance by looking at the camera.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgements

- [OpenVINO](https://docs.openvino.ai/latest/index.html)
- [face_recognition](https://github.com/ageitgey/face_recognition)
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/intro)

## Contact

For any inquiries or support, please contact [chirieacandrei@proton.me](mailto:chirieacandrei@proton.me).