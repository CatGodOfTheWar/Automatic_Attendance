import os
import subprocess
from flask import Flask, render_template
import logging
from DB_management import DBmanagement
import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

app = Flask(__name__)

def get_student_data():
    try:
        db = DBmanagement()
        data = db.db_get_attendance()
        return data
    except Exception as e:
        logging.error(f"Error getting student data: {e}")
        return []

def generate_report_data():
    try:
        db = DBmanagement()
        attendance_data = db.db_get_attendance()
        dataFrame = pd.DataFrame(attendance_data, columns=['student_name', 'date'])
        dataFrame['date'] = dataFrame['date'].fillna("")
        groupData = dataFrame.groupby('student_name').agg({
            'date': [lambda x: max(0, len(x) - 1), lambda x: list(x)]
        }).reset_index()
        groupData.columns = ['student_name', 'attendance_count', 'dates']
        report_data = groupData.to_dict(orient='records')
        for record in report_data:
            record['dates'] = " ; ".join(record['dates'][1:])
        return report_data
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return []
        
def kill_process_on_port(port):
    try:
        result = subprocess.check_output(f"sudo lsof -t -i:{port}", shell=True)
        pid = int(result.strip())
        os.kill(pid, 9)
        logging.error(f"Process on port {port} has been killed.")
    except subprocess.CalledProcessError:
        logging.error(f"No process found on port {port}.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        
@app.route('/')
def report():
    try:
        report_data = generate_report_data()
        return render_template('index.html', report_data=report_data)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return "An error occurred. Please check the logs."

if __name__ == '__main__':
    try:
        kill_process_on_port(6969)
        app.run(debug=True, port=6969)
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        exit(1)