import os
import subprocess
from flask import Flask, render_template
import logging
from DB_management import DBmanagement
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Initialize Flask app
app = Flask(__name__)

# Function to get student data from the database
def get_student_data():
    try:
        db = DBmanagement()  # Initialize database management object
        data = db.db_get_attendance()  # Get attendance data from the database
        return data
    except Exception as e:
        logging.error(f"Error getting student data: {e}")
        return []

# Function to generate report data from the attendance records
def generate_report_data():
    try:
        db = DBmanagement()  # Initialize database management object
        attendance_data = db.db_get_attendance()  # Get attendance data from the database
        dataFrame = pd.DataFrame(attendance_data, columns=['student_name', 'date'])  # Create DataFrame from attendance data
        dataFrame['date'] = dataFrame['date'].fillna("")  # Fill NaN dates with empty strings
        groupData = dataFrame.groupby('student_name').agg({
            'date': [lambda x: max(0, len(x) - 1), lambda x: list(x)]  # Aggregate data by student name
        }).reset_index()
        groupData.columns = ['student_name', 'attendance_count', 'dates']  # Rename columns
        report_data = groupData.to_dict(orient='records')  # Convert DataFrame to list of dictionaries
        for record in report_data:
            record['dates'] = " ; ".join(record['dates'][1:])  # Join dates into a single string
        return report_data
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []

# Function to kill a process running on a specific port
def kill_process_on_port(port):
    try:
        result = subprocess.check_output(f"sudo lsof -t -i:{port}", shell=True)  # Get process ID using lsof
        pid = int(result.strip())  # Convert result to integer
        os.kill(pid, 9)  # Kill the process
        logging.error(f"Process on port {port} has been killed.")
    except subprocess.CalledProcessError:
        logging.error(f"No process found on port {port}.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")

# Route to display the report
@app.route('/')
def report():
    try:
        report_data = generate_report_data()  # Generate report data
        return render_template('index.html', report_data=report_data)  # Render the report in the template
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "An error occurred. Please check the logs."

# Main entry point of the application
if __name__ == '__main__':
    try:
        kill_process_on_port(6969)  # Kill any process running on port 6969
        app.run(debug=True, port=6969)  # Run the Flask app on port 6969
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        exit(1)