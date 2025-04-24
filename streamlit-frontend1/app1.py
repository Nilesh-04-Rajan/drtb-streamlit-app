import streamlit as st
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import inch
from datetime import datetime
import requests

# --- Streamlit Page Config ---
st.set_page_config(
    page_title="DR-TB Prediction App",
    page_icon="🧪",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- Custom CSS Styling ---
st.markdown("""
    <style>
        body {
            background-color: #f5f7fa;
        }
        .main {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        h1, h2, h3 {
            color: #2c3e50;
        }
        .stButton>button {
            background-color: #0072C6;
            color: white;
            border-radius: 5px;
        }
        .stDownloadButton>button {
            background-color: #2ecc71;
            color: white;
        }
        .stRadio > div {
            gap: 20px;
        }
    </style>
""", unsafe_allow_html=True)

# --- Dummy login credentials ---
users = {
    "doctor1": "password123",
    "nurse2": "securepass",
}

# --- Session State ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if 'page' not in st.session_state:
    st.session_state.page = "login"

# --- Login Page ---
def login_page():
    st.markdown("<h2>🧪 Drug Resistance to Tuberculosis Prediction</h2>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### 🔐 Please log in to access the app.")

    username = st.text_input("Username", key="login_username", placeholder="Enter your username")
    password = st.text_input("Password", type="password", key="login_password", placeholder="Enter your password")

    login_pressed = st.button("Login", key="login_btn")

    if login_pressed:
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.page = "input"
        else:
            st.error("❌ Invalid username or password")


# --- Input Form Page ---
def input_page():
    st.title("🧪 DR-TB Prediction App")
    st.markdown("### 👤 Enter patient details below to predict Rifampicin resistance.")

    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input("Age", min_value=0, max_value=120, value=30)
        gender = st.selectbox("Gender", ["Female", "Male"])
        heart_rate = st.number_input("Heart Rate", min_value=30, max_value=200, value=80)
        resp_rate = st.number_input("Respiratory Rate", min_value=5, max_value=60, value=20)

    with col2:
        weight = st.number_input("Weight (kg)", min_value=20, max_value=200, value=60)
        culture_result = st.selectbox("MGT Sputum Culture result", ["Negative", "Positive"])
        afb_microscopy = st.selectbox("AFB Microscopy for sputum", ["Negative", "Positive"])
        tb_history = st.selectbox("History of TB disease prior enrollment", ["No", "Yes"])

    fever = st.radio("Fever", ["No", "Yes"], horizontal=True)
    weight_loss = st.radio("Weight Loss", ["No", "Yes"], horizontal=True)
    hiv_status = st.selectbox("HIV Status", ["Negative", "Positive"])

    cd4rslt = st.number_input("CD4 Count", min_value=0, max_value=1500, value=400) if hiv_status == "Positive" else 0

    if st.button("Predict DR-TB"):
        binary_map = {"No": 0, "Yes": 1, "Negative": 0, "Positive": 1}
        gender_map = {"Female": 0, "Male": 1}
        hiv_cd4_low = 1 if hiv_status == "Positive" and cd4rslt < 200 else 0

        input_df = pd.DataFrame([{
            'MGT Sputum Culture result': binary_map[culture_result],
            'AFB Microscopy for sputum': binary_map[afb_microscopy],
            'Age': age,
            'Gender': gender_map[gender],
            'Heart rate': heart_rate,
            'Respiratory rate': resp_rate,
            'Weight': weight,
            'History of TB disease prior enrollment': binary_map[tb_history],
            'Fever': binary_map[fever],
            'Weight loss': binary_map[weight_loss],
            'HIV status': binary_map[hiv_status],
            'cd4rslt': cd4rslt,
            'HIV_CD4_Low': hiv_cd4_low
        }])

        try:
            res = requests.post("http://localhost:8080/api/patients", json=input_df.to_dict(orient="records")[0])
            if res.status_code == 200:
                data = res.json()
                prediction = data['prediction']
                st.session_state.prediction_result = prediction
                st.session_state.prediction_message = (
                    "🟥 DR-TB Positive: Rifampicin Resistant" if prediction == 1
                    else "🟩 DR-TB Negative: Rifampicin Sensitive"
                )

                st.session_state.update({
                    'age': age, 'gender': gender, 'heart_rate': heart_rate,
                    'resp_rate': resp_rate, 'weight': weight,
                    'culture_result': culture_result, 'afb_microscopy': afb_microscopy,
                    'tb_history': tb_history, 'fever': fever, 'weight_loss': weight_loss,
                    'hiv_status': hiv_status, 'cd4rslt': cd4rslt, 'page': "results"
                })

                st.rerun()
            else:
                st.error(f"❌ Backend Error {res.status_code}: Unable to get prediction.")

        except Exception as e:
            st.error(f"🚨 Could not connect to prediction API:\n{e}")

# --- Results Page ---
def results_page():
    st.title("📊 Prediction Results")

    if "prediction_message" in st.session_state:
        st.success(st.session_state.prediction_message)

        st.markdown("### 🧾 Patient Details")
        inputs = {
            "MGT Sputum Culture result": st.session_state.culture_result,
            "AFB Microscopy for sputum": st.session_state.afb_microscopy,
            "Age": st.session_state.age,
            "Gender": st.session_state.gender,
            "Heart Rate": st.session_state.heart_rate,
            "Respiratory Rate": st.session_state.resp_rate,
            "Weight": f"{st.session_state.weight} kg",
            "History of TB disease prior enrollment": st.session_state.tb_history,
            "Fever": st.session_state.fever,
            "Weight Loss": st.session_state.weight_loss,
            "HIV Status": st.session_state.hiv_status
        }

        if st.session_state.hiv_status == "Positive":
            inputs["CD4 Count"] = st.session_state.cd4rslt

        hiv_cd4_low = 1 if st.session_state.hiv_status == "Positive" and st.session_state.cd4rslt < 200 else 0
        inputs["HIV CD4 Low"] = hiv_cd4_low

        for k, v in inputs.items():
            st.write(f"**{k}:** {v}")

        def create_pdf():
            buffer = BytesIO()
            p = canvas.Canvas(buffer, pagesize=A4)
            width, height = A4
            y = height - 50

            p.setFont("Helvetica-Bold", 20)
            p.setFillColor(colors.HexColor('#0072C6'))
            p.drawString(180, y, "ResistX TB Report")
            y -= 40

            p.setFont("Helvetica", 12)
            p.setFillColor(colors.black)
            p.drawString(50, y, f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            y -= 30

            p.line(50, y, width - 50, y)
            y -= 20

            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Prediction Result:")
            y -= 20

            p.setFont("Helvetica", 12)
            if st.session_state.prediction_result == 1:
                p.setFillColorRGB(1, 0, 0)
            else:
                p.setFillColorRGB(0, 0.5, 0)
            p.drawString(70, y, st.session_state.prediction_message)
            p.setFillColor(colors.black)
            y -= 40

            p.setFont("Helvetica-Bold", 14)
            p.drawString(50, y, "Patient Details:")
            y -= 20

            p.setFont("Helvetica", 12)
            for key, val in inputs.items():
                if y < 100:
                    p.showPage()
                    y = height - 50
                p.drawString(70, y, f"{key}: {val}")
                y -= 20

            p.showPage()
            p.save()
            buffer.seek(0)
            return buffer

        pdf_file = create_pdf()
        st.download_button(
            label="📄 Download Report as PDF",
            data=pdf_file,
            file_name="resistx_report.pdf",
            mime="application/pdf"
        )

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Try Again"):
                st.session_state.page = "input"
        with col2:
            if st.button("🚪 Logout"):
                st.session_state.logged_in = False
                st.session_state.page = "login"
    else:
        st.error("No prediction available. Please enter patient details.")

# --- App Entry Point ---
if not st.session_state.logged_in:
    login_page()
else:
    if st.session_state.page == "input":
        input_page()
    elif st.session_state.page == "results":
        results_page()