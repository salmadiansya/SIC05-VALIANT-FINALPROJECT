import streamlit as st
import pandas as pd
from datetime import datetime

# Load dataset
@st.cache_data
def load_student_data():
    return pd.read_csv('dataset/student_data.csv')

def load_log_data(log_data_file):
    try:
        return pd.read_csv(log_data_file)
    except FileNotFoundError:
        return pd.DataFrame(columns=['timestamp', 'student_name', 'student_class', 'nfc_card_id'])

student_data = load_student_data()
log_data_file = 'dataset/log.csv'
log_data = load_log_data(log_data_file)

# Define function to add log entry
def add_log_entry(nfc_card_id):
    student_info = student_data[student_data['nfc_card_id'] == nfc_card_id]
    if not student_info.empty:
        student_name = student_info['student_name'].values[0]
        student_class = student_info['student_class'].values[0]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = pd.DataFrame([[timestamp, student_name, student_class, nfc_card_id]], 
                                 columns=['timestamp', 'student_name', 'student_class', 'nfc_card_id'])
        return log_entry
    else:
        return None

def save_log_data(log_data):
    try:
        log_data.to_csv(log_data_file, index=False)
    except Exception as e:
        st.error(f"Error saving log data: {e}")

# Streamlit UI
st.title("MAN10 JAKARTA T-BOX LOG")

# Section to display log data
st.header("Log Notification")
if st.button("Refresh"):
    log_data = load_log_data(log_data_file)
st.dataframe(log_data)

# Section to simulate NFC card reading
st.header("Add Log Entry")
nfc_card_id = st.text_input("Enter NFC Card ID")
if st.button("Add Log Entry"):
    log_entry = add_log_entry(nfc_card_id)
    if log_entry is not None:
        log_data = pd.concat([log_data, log_entry], ignore_index=True)
        save_log_data(log_data)
        st.success(f"Log entry added for NFC Card ID: {nfc_card_id}")
    else:
        st.error(f"No student found with NFC Card ID: {nfc_card_id}")

# Section to search logs by student name
st.header("Search by Student Name")
student_name_search = st.text_input("Enter Student Name to Search")
if student_name_search:
    filtered_log_data = log_data[log_data['student_name'].str.contains(student_name_search, case=False, na=False)]
    st.dataframe(filtered_log_data)
else:
    st.write("Enter the student's name to search for their T-BOX log.")

# Section to display student data
st.header("Student Data")
st.dataframe(student_data)

# Endpoint for receiving data from ESP32
query_params = st.query_params
if 'nfc_card_id' in query_params:
    nfc_card_id = query_params['nfc_card_id'][0]
    log_entry = add_log_entry(nfc_card_id)
    if log_entry is not None:
        log_data = pd.concat([log_data, log_entry], ignore_index=True)
        log_data.to_csv(log_data_file, index=False)
        st.write("Log entry added")
    else:
        st.write("No student found with NFC Card ID: ", nfc_card_id)