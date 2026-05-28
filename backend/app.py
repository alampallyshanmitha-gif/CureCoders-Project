from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fpdf import FPDF
import mysql.connector
import tensorflow as tf
import numpy as np
from PIL import Image
import io

# =========================================
# FLASK APP
# =========================================
app = Flask(__name__)
CORS(app)

# =========================================
# LOAD AI MODEL
# =========================================
model = tf.keras.models.load_model("pneumonia_model.h5")

# =========================================
# DATABASE CONNECTION
# =========================================
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Exam@2025!SQL",  
        database="curecoders"
    )

# =========================================
# ANALYZE X-RAY
# =========================================
@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # -----------------------------
        # GET FILE
        # -----------------------------
        file = request.files.get("xray")

        if not file:
            return jsonify({"error": "No X-ray image uploaded"}), 400

        # -----------------------------
        # PATIENT DETAILS
        # -----------------------------
        patient = request.form.get("patient", "--")
        age = request.form.get("age", "--")
        gender = request.form.get("gender", "--")

        # -----------------------------
        # IMAGE PREPROCESSING
        # -----------------------------
        img = Image.open(file).convert("RGB")
        img = img.resize((150, 150))

        img_array = np.array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        # -----------------------------
        # AI PREDICTION
        # -----------------------------
        prediction = model.predict(img_array)[0][0]

        if prediction > 0.5:
            disease = "PNEUMONIA"
            confidence = float(round(prediction * 100, 2))
        else:
            disease = "NORMAL"
            confidence = float(round((1 - prediction) * 100, 2))

        # -----------------------------
        # STATUS
        # -----------------------------
        if disease == "NORMAL":
            status = "Safe"
        elif disease == "PNEUMONIA":
            if confidence >= 90:
                status = "Critical"
            elif confidence >= 75:
                status = "High Risk"
            elif confidence >= 60:
                status = "Moderate Risk"
        else:
            status = "Mild Risk"

        # -----------------------------
        # RECOMMENDATIONS
        # -----------------------------
        if disease == "PNEUMONIA":
            recommendations = [
                "Consult pulmonologist immediately",
                "Start chest infection evaluation",
                "Monitor oxygen levels",
                "Follow-up X-ray recommended"
            ]
        else:
            recommendations = [
                "No pneumonia detected",
                "Maintain healthy lifestyle",
                "Routine checkup recommended"
            ]

        # =========================================
        # DATABASE INSERT
        # =========================================
        conn = get_db_connection()
        cursor = conn.cursor()

        # -----------------------------
        # PATIENTS TABLE
        # -----------------------------
        cursor.execute("""
            INSERT INTO patients (patient_name, age, gender)
            VALUES (%s, %s, %s)
        """, (patient, age, gender))

        # -----------------------------
        # REPORTS TABLE
        # -----------------------------
        cursor.execute("""
            INSERT INTO reports (
                patient_name,
                age,
                gender,
                filename,
                disease,
                confidence,
                status,
                recommendations
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (
            patient,
            age,
            gender,
            file.filename,
            disease,
            confidence,
            status,
            "\n".join(recommendations)
        ))

        # -----------------------------
        # ANALYTICS TABLE
        # -----------------------------
        accuracy = 96

        cursor.execute("""
            UPDATE analytics
            SET total_scans = total_scans + 1,
                pneumonia_cases = pneumonia_cases + %s,
                normal_cases = normal_cases + %s,
                critical_cases=critical_cases+ %s,
                accuracy = %s
            WHERE id = 1
        """, (
            1 if disease == "PNEUMONIA" else 0,
            1 if disease == "NORMAL" else 0,
            1 if  "Critical" in status else 0,
            accuracy
        ))

        conn.commit()

        # -----------------------------
        # FETCH ANALYTICS
        # -----------------------------
        cursor.execute("SELECT * FROM analytics WHERE id = 1")
        analytics_data = cursor.fetchone()

        analytics = {
            "total_scans": analytics_data[1],
            "pneumonia_cases": analytics_data[2],
            "normal_cases": analytics_data[3],
            "accuracy": analytics_data[4],"critical_cases":analytics_data[6]
        }

        cursor.close()
        conn.close()

        # =========================================
        # RESPONSE
        # =========================================
        return jsonify({
            "disease": disease,
            "confidence": confidence,
            "status": status,
            "recommendations": recommendations,
            "analytics": analytics
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# =========================================
# PDF REPORT DOWNLOAD
# =========================================
@app.route("/download_report", methods=["GET"])
def download_report():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # GET LATEST REPORT
        cursor.execute("""
            SELECT * FROM reports
            ORDER BY id DESC
            LIMIT 1
        """)

        report = cursor.fetchone()

        cursor.close()
        conn.close()

        if not report:
            return jsonify({"error": "No reports found"}), 404

        # =========================================
        # CREATE PDF
        # =========================================
        pdf = FPDF()
        pdf.add_page()

        # TITLE
        pdf.set_font("Arial", "B", 18)
        pdf.cell(200, 10, "CureCoders AI Medical Report", ln=True, align="C")

        pdf.ln(10)

        # PATIENT INFO
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Patient Information", ln=True)

        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Patient Name: {report['patient_name']}", ln=True)
        pdf.cell(200, 10, f"Age: {report['age']}", ln=True)
        pdf.cell(200, 10, f"Gender: {report['gender']}", ln=True)

        pdf.ln(5)

        # AI RESULT
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "AI Diagnosis Result", ln=True)

        pdf.set_font("Arial", "", 12)
        pdf.cell(200, 10, f"Disease Detected: {report['disease']}", ln=True)
        pdf.cell(200, 10, f"Confidence Score: {report['confidence']}%", ln=True)
        pdf.cell(200, 10, f"Risk Status: {report['status']}", ln=True)

        pdf.ln(5)

        # RECOMMENDATIONS
        pdf.set_font("Arial", "B", 12)
        pdf.cell(200, 10, "Recommendations", ln=True)

        pdf.set_font("Arial", "", 12)

        recommendations = report["recommendations"].split("\n")

        for rec in recommendations:
            pdf.multi_cell(0, 10, f"- {rec}")

        pdf.ln(10)

        # FOOTER
        pdf.set_font("Arial", "I", 10)
        pdf.multi_cell(
            0,
            8,
            "Disclaimer: This AI system is designed to assist medical professionals and should not replace expert clinical judgment."
        )

        # =========================================
        # OUTPUT PDF
        # =========================================
        pdf_output = pdf.output(dest="S").encode("latin1")

        return send_file(
            io.BytesIO(pdf_output),
            download_name="CureCoders_Report.pdf",
            as_attachment=True,
            mimetype="application/pdf"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# =========================================
# RUN APP
# =========================================
if __name__ == "__main__":
    app.run(debug=True)