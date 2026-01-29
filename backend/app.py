from flask import Flask, request, jsonify
from flask_cors import CORS
import os

from ocr_utils import extract_text
from report_parser import parse_report
from range_checker import check_abnormal_values
from ai_interpreter import interpret_abnormality

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/upload-report", methods=["POST"])
def upload_report():

    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # 1️⃣ OCR
    extracted_text = extract_text(file_path)

    # 2️⃣ Parse report
    parsed_values = parse_report(extracted_text)

    # 3️⃣ Detect abnormal values
    abnormal_values = check_abnormal_values(parsed_values)

    # 4️⃣ AI interpretation
    for test_name, details in abnormal_values.items():
        details["explanation"] = interpret_abnormality(
            test_name=test_name,
            value=details.get("value"),
            normal_range=details.get("normal_range"),
            status=details.get("status")
        )

    return jsonify({
        "message": "Report analyzed successfully",
        "filename": file.filename,
        "abnormal_values": abnormal_values
    })


if __name__ == "__main__":
    app.run(debug=True)
