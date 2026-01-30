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

    # Get selected language from form data
    language = request.form.get("language", "english").lower()
    
    # Validate language
    if language not in ["english", "hindi", "malayalam"]:
        language = "english"
    
    print(f"\n🌐 Selected Language: {language.upper()}")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        # 1️⃣ OCR - Extract text from report
        print("\n🔍 Step 1: Extracting text from report...")
        extracted_text = extract_text(file_path)

        # 2️⃣ Parse report - Find test values
        print("\n📊 Step 2: Parsing test values...")
        parsed_values = parse_report(extracted_text)

        # 3️⃣ Detect abnormal values
        print("\n⚠️ Step 3: Checking for abnormal values...")
        abnormal_values = check_abnormal_values(parsed_values)

        # 4️⃣ AI interpretation for each abnormal value in selected language
        print(f"\n🤖 Step 4: Generating AI explanations in {language.upper()}...")
        for test_name, details in abnormal_values.items():
            print(f"   → Generating {language} explanation for {test_name}...")
            
            explanation = interpret_abnormality(
                test_name=test_name,
                value=details.get("value"),
                normal_range=details.get("normal_range"),
                status=details.get("status"),
                language=language  # Pass the selected language
            )
            
            details["explanation"] = explanation
            print(f"   ✅ {language.capitalize()} explanation generated for {test_name}")

        print("\n✨ Analysis complete!\n")

        return jsonify({
            "message": "Report analyzed successfully",
            "filename": file.filename,
            "language": language,
            "abnormal_values": abnormal_values
        })

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}\n")
        return jsonify({
            "error": "Failed to analyze report",
            "details": str(e)
        }), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Medical Report Analyzer API",
        "supported_languages": ["english", "hindi", "malayalam"]
    })


if __name__ == "__main__":
    print("\n" + "="*50)
    print("🏥 Medical Report Analyzer - Backend Server")
    print("="*50)
    print("Server starting on http://127.0.0.1:5000")
    print("🌐 Supported Languages: English, Hindi, Malayalam")
    print("Press CTRL+C to stop")
    print("="*50 + "\n")
    
    app.run(debug=True, host="127.0.0.1", port=5000)