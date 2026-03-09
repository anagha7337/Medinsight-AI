from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import mysql.connector
from mysql.connector import Error
from decouple import config 

from ocr_utils import extract_text
from report_parser import parse_report
from range_checker import check_abnormal_values
from ai_interpreter import interpret_abnormality
from scan_interpreter import interpret_scan

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ============================================================================
# DATABASE CONFIGURATION (Medicine Lookup)
# ============================================================================

db_config = {
    'host': config('DB_HOST', default='localhost'),
    'user': config('DB_USER', default='root'),
    'password': config('DB_PASSWORD'),
    'database': config('DB_NAME', default='MEDINSIGHT_AI')
}

def create_connection():
    """Create database connection"""
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Database connection error: {e}")
        return None

def search_in_database(medicine_name):
    """Search for medicine in local database"""
    connection = create_connection()
    if not connection:
        return None
    
    cursor = connection.cursor(dictionary=True)
    
    query = """
    SELECT * FROM medicines 
    WHERE LOWER(brand_name) LIKE LOWER(%s) 
    OR LOWER(generic_name) LIKE LOWER(%s)
    LIMIT 1
    """
    
    try:
        cursor.execute(query, (f"%{medicine_name}%", f"%{medicine_name}%"))
        result = cursor.fetchone()
        return result
    except Error as e:
        print(f"Database search error: {e}")
        return None
    finally:
        cursor.close()
        connection.close()

def insert_medicine_to_database(drug_data):
    """Insert medicine data into database"""
    connection = create_connection()
    if not connection:
        return False
    
    cursor = connection.cursor()
    openfda = drug_data.get('openfda', {})
    
    def safe_get(data, key):
        value = data.get(key, [])
        if isinstance(value, list):
            return ' | '.join(str(v) for v in value) if value else None
        return str(value) if value else None
    
    insert_query = """
    INSERT INTO medicines (
        brand_name, generic_name, manufacturer_name, product_type,
        route, dosage_form, indications_and_usage, warnings,
        adverse_reactions, dosage_and_administration, mechanism_of_action
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    values = (
        safe_get(openfda, 'brand_name'),
        safe_get(openfda, 'generic_name'),
        safe_get(openfda, 'manufacturer_name'),
        safe_get(openfda, 'product_type'),
        safe_get(openfda, 'route'),
        safe_get(drug_data, 'dosage_form'),
        safe_get(drug_data, 'indications_and_usage'),
        safe_get(drug_data, 'warnings'),
        safe_get(drug_data, 'adverse_reactions'),
        safe_get(drug_data, 'dosage_and_administration'),
        safe_get(drug_data, 'mechanism_of_action')
    )
    
    try:
        cursor.execute(insert_query, values)
        connection.commit()
        print("✓ Medicine saved to database")
        return True
    except Error as e:
        print(f"Error inserting to database: {e}")
        return False
    finally:
        cursor.close()
        connection.close()

def fetch_from_openfda(medicine_name):
    """Fetch medicine data from OpenFDA API"""
    base_url = "https://api.fda.gov/drug/label.json"
    search_query = f'openfda.brand_name:"{medicine_name}"'
    
    params = {
        'search': search_query,
        'limit': 1
    }
    
    try:
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0]
        
        search_query = f'openfda.generic_name:"{medicine_name}"'
        params['search'] = search_query
        response = requests.get(base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                return data['results'][0]
        
        return None
        
    except Exception as e:
        print(f"OpenFDA API error: {e}")
        return None

def format_medicine_response(medicine_data):
    """Format medicine data for frontend"""
    if 'openfda' in medicine_data:
        openfda = medicine_data.get('openfda', {})
        brand_name = openfda.get('brand_name', ['N/A'])[0] if openfda.get('brand_name') else 'N/A'
        generic_name = openfda.get('generic_name', ['N/A'])[0] if openfda.get('generic_name') else 'N/A'
        manufacturer = openfda.get('manufacturer_name', ['N/A'])[0] if openfda.get('manufacturer_name') else 'N/A'
        product_type = openfda.get('product_type', ['N/A'])[0] if openfda.get('product_type') else 'N/A'
        
        uses = medicine_data.get('indications_and_usage', ['N/A'])[0] if medicine_data.get('indications_and_usage') else 'N/A'
        warnings = medicine_data.get('warnings', ['N/A'])[0] if medicine_data.get('warnings') else 'N/A'
        side_effects = medicine_data.get('adverse_reactions', ['N/A'])[0] if medicine_data.get('adverse_reactions') else 'N/A'
        mechanism = medicine_data.get('mechanism_of_action', ['N/A'])[0] if medicine_data.get('mechanism_of_action') else 'N/A'
    else:
        brand_name = medicine_data.get('brand_name', 'N/A')
        generic_name = medicine_data.get('generic_name', 'N/A')
        manufacturer = medicine_data.get('manufacturer_name', 'N/A')
        product_type = medicine_data.get('product_type', 'N/A')
        uses = medicine_data.get('indications_and_usage', 'N/A')
        warnings = medicine_data.get('warnings', 'N/A')
        side_effects = medicine_data.get('adverse_reactions', 'N/A')
        mechanism = medicine_data.get('mechanism_of_action', 'N/A')
    
    return {
        'brand_name': brand_name,
        'generic_name': generic_name,
        'manufacturer': manufacturer,
        'category': product_type,
        'uses': uses,
        'warnings': warnings,
        'side_effects': side_effects,
        'mechanism_of_action': mechanism
    }

# ============================================================================
# ROUTES - MEDICAL REPORT ANALYZER
# ============================================================================

@app.route("/upload-report", methods=["POST"])
def upload_report():
    """Medical Report Analyzer endpoint"""
    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    language = request.form.get("language", "english").lower()

    supported_languages = ["english", "hindi", "malayalam", "tamil", "telugu", "kannada", "marathi", "bengali", "gujarati", "urdu", "odia"]
    
    if language not in supported_languages:
        language = "english"
    
    print(f"\nSelected Language: {language.upper()}")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        print("\nStep 1: Extracting text from report...")
        extracted_text = extract_text(file_path)

        print("\nStep 2: Parsing test values...")
        parsed_values = parse_report(extracted_text)

        print("\nStep 3: Checking for abnormal values...")
        abnormal_values = check_abnormal_values(parsed_values)

        print(f"\nStep 4: Generating AI explanations in {language.upper()}...")
        for test_name, details in abnormal_values.items():
            print(f"   → Generating {language} explanation for {test_name}...")
            
            explanation = interpret_abnormality(
                test_name=test_name,
                value=details.get("value"),
                normal_range=details.get("normal_range"),
                status=details.get("status"),
                language=language
            )
            
            details["explanation"] = explanation
            print(f"   {language.capitalize()} explanation generated for {test_name}")

        print("\nAnalysis complete\n")

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

# ============================================================================
# ROUTES - SCAN REPORT ANALYZER (NEW)
# ============================================================================

@app.route("/upload-scan", methods=["POST"])
def upload_scan():
    """Scan Report Analyzer endpoint - analyzes X-rays, CT scans, MRIs, etc."""
    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    # Validate file type
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.pdf'}
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        return jsonify({"error": "Invalid file type. Please upload JPG, JPEG, PNG, or PDF"}), 400

    language = request.form.get("language", "english").lower()
    
    if language not in ["english", "hindi", "malayalam"]:
        language = "english"
    
    print(f"\n📊 Scan Analysis Request - Language: {language.upper()}")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        print("\nStep 1: Analyzing scan image with AI...")
        
        # For PDF, we'd need to convert first page to image
        # For now, assuming image files (JPG/JPEG/PNG)
        if file_ext == '.pdf':
            # TODO: Add PDF to image conversion if needed
            return jsonify({
                "error": "PDF support coming soon. Please upload JPG or PNG for now."
            }), 400
        
        # Analyze the scan
        result = interpret_scan(file_path, language)
        
        if result.get("success"):
            print(f"\n✅ Scan analysis complete in {language.upper()}\n")
            return jsonify({
                "message": "Scan analyzed successfully",
                "filename": file.filename,
                "language": language,
                "analysis": result.get("analysis")
            })
        else:
            print(f"\n⚠️ Scan analysis failed\n")
            return jsonify({
                "error": "Failed to analyze scan",
                "details": result.get("error", "Unknown error"),
                "fallback_message": result.get("analysis")
            }), 500

    except Exception as e:
        print(f"\n❌ Error during scan analysis: {str(e)}\n")
        return jsonify({
            "error": "Failed to analyze scan",
            "details": str(e)
        }), 500

# ============================================================================
# ROUTES - MEDICINE LOOKUP
# ============================================================================

@app.route('/api/search-medicine', methods=['GET'])
def search_medicine_api():
    """Medicine Lookup endpoint"""
    medicine_name = request.args.get('name')
    
    if not medicine_name:
        return jsonify({
            'success': False,
            'message': 'Medicine name is required'
        }), 400
    
    print(f"\n🔍 API Request: Searching for {medicine_name}")
    
    db_result = search_in_database(medicine_name)
    
    if db_result:
        print("✓ Found in database")
        return jsonify({
            'success': True,
            'source': 'database',
            'data': format_medicine_response(db_result)
        })
    
    print("→ Fetching from OpenFDA...")
    api_result = fetch_from_openfda(medicine_name)
    
    if api_result:
        print("✓ Found in OpenFDA")
        insert_medicine_to_database(api_result)
        
        return jsonify({
            'success': True,
            'source': 'openfda',
            'data': format_medicine_response(api_result)
        })
    else:
        print("✗ Not found")
        return jsonify({
            'success': False,
            'message': f'Medicine "{medicine_name}" not found'
        }), 404

# ============================================================================
# HEALTH CHECK
# ============================================================================

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint for all services"""
    return jsonify({
        "status": "healthy",
        "services": {
            "medical_report_analyzer": "active",
            "scan_report_analyzer": "active",
            "medicine_lookup": "active"
        },
        "endpoints": {
            "report_analyzer": "/upload-report (POST)",
            "scan_analyzer": "/upload-scan (POST)",
            "medicine_lookup": "/api/search-medicine (GET)"
        },
        "supported_languages": ["english", "hindi", "malayalam"]
    })

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🏥 MEDINSIGHT AI - Backend Server")
    print("="*60)
    print("\n📋 Available Services:")
    print("   1. Medical Report Analyzer (Blood tests, Lab reports)")
    print("   2. Scan Report Analyzer (X-rays, CT, MRI)")
    print("   3. Medicine Lookup Dictionary")
    print("\n🌐 Server starting on http://127.0.0.1:5000")
    print("\n📡 Endpoints:")
    print("   • POST /upload-report - Lab report analysis")
    print("   • POST /upload-scan - Scan image analysis")
    print("   • GET  /api/search-medicine?name=<medicine> - Medicine lookup")
    print("   • GET  /health - Health check")
    print("\n⚡ Press CTRL+C to stop")
    print("="*60 + "\n")
    
    app.run(debug=True, host="127.0.0.1", port=5000)