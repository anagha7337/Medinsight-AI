from flask import Flask, render_template, jsonify, request, redirect, url_for
from flask_cors import CORS
import os
import requests
import json
from dotenv import load_dotenv
from decouple import config

# Supabase Python client
from supabase import create_client, Client

# Medical Report Analyzer imports
from src.report_analyzer.ocr_utils import extract_text
from src.report_analyzer.report_parser import parse_report
from src.report_analyzer.range_checker import check_abnormal_values
from src.report_analyzer.ai_interpreter import interpret_abnormality
from src.report_analyzer.scan_interpreter import interpret_scan

# AI Chatbot imports
from src.ai_assistant.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from src.ai_assistant.prompt import system_prompt

# ========================================
# FLASK APP INITIALIZATION
# ========================================

app = Flask(__name__)
CORS(app)

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ========================================
# ENVIRONMENT VARIABLES
# ========================================

# Supabase
SUPABASE_URL      = config('SUPABASE_URL')
SUPABASE_ANON_KEY = config('SUPABASE_ANON_KEY')
SUPABASE_SERVICE_KEY = config('SUPABASE_SERVICE_KEY')   # needed for server-side DB writes

# AI Services
GROQ_API_KEY     = config('GROQ_API_KEY',     default='')
PINECONE_API_KEY = config('PINECONE_API_KEY', default='')
GOOGLE_API_KEY   = config('GOOGLE_API_KEY',   default='')

# ========================================
# SUPABASE CLIENT (server-side, service role)
# ========================================
# We use the service-role key here so the backend can read/write the medicines
# table without being blocked by RLS (medicines are public reference data).
supabase_client: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# ========================================
# AI CHATBOT SETUP (RAG)
# ========================================

print("🤖 Initializing AI Chatbot...")

try:
    embeddings = download_hugging_face_embeddings()
    
    docsearch = PineconeVectorStore.from_existing_index(
        index_name="medicalbot",
        embedding=embeddings
    )
    
    retriever = docsearch.as_retriever(search_type="similarity", search_kwargs={"k": 1})
    
    llm = ChatGoogleGenerativeAI(
        temperature=0.4,
        model="models/gemini-2.5-flash",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("human", "{input}"),
        ]
    )
    
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    CHATBOT_INITIALIZED = True
    print("✅ AI Chatbot initialized successfully")
    
except Exception as e:
    print(f"⚠️ AI Chatbot initialization failed: {e}")
    CHATBOT_INITIALIZED = False

# ========================================
# SUPABASE TEMPLATE HELPER
# ========================================

def render_with_supabase(template, **kwargs):
    """Inject Supabase public credentials into every rendered template."""
    return render_template(
        template,
        supabase_url=SUPABASE_URL,
        supabase_anon_key=SUPABASE_ANON_KEY,
        **kwargs
    )

# ========================================
# MEDICINE LOOKUP — DATABASE HELPERS
# ========================================

def search_in_supabase(medicine_name: str):
    """
    Case-insensitive search in the Supabase medicines table.
    Checks both brand_name and generic_name columns.
    Returns the first matching row as a dict, or None.
    """
    try:
        name_lower = medicine_name.lower()

        # Search brand_name
        res = supabase_client.table('medicines') \
            .select('*') \
            .ilike('brand_name', f'%{name_lower}%') \
            .limit(1) \
            .execute()

        if res.data:
            print("✅ Found in Supabase (brand_name)")
            return res.data[0]

        # Search generic_name
        res = supabase_client.table('medicines') \
            .select('*') \
            .ilike('generic_name', f'%{name_lower}%') \
            .limit(1) \
            .execute()

        if res.data:
            print("✅ Found in Supabase (generic_name)")
            return res.data[0]

        return None

    except Exception as e:
        print(f"Supabase search error: {e}")
        return None


def insert_medicine_to_supabase(formatted: dict):
    """
    Save a formatted medicine dict to the Supabase medicines table.
    Ignores duplicates (brand_name + generic_name combo).
    """
    try:
        supabase_client.table('medicines').upsert(
            formatted,
            on_conflict='brand_name,generic_name'
        ).execute()
        print("✓ Medicine saved to Supabase")
    except Exception as e:
        print(f"Supabase insert error: {e}")


# ========================================
# MEDICINE LOOKUP — DATA SOURCES
# ========================================

def fetch_from_openfda(medicine_name: str):
    """Query OpenFDA drug label API. Returns a formatted dict or None."""
    base_url = "https://api.fda.gov/drug/label.json"

    for field in ['openfda.brand_name', 'openfda.generic_name']:
        try:
            resp = requests.get(base_url, params={
                'search': f'{field}:"{medicine_name}"',
                'limit': 1
            }, timeout=8)
            if resp.status_code == 200:
                results = resp.json().get('results', [])
                if results:
                    print(f"✅ Found in OpenFDA ({field})")
                    return format_openfda_result(results[0])
        except Exception as e:
            print(f"OpenFDA error: {e}")

    return None


def format_openfda_result(drug: dict) -> dict:
    """Convert a raw OpenFDA result into the standard medicine dict."""
    openfda = drug.get('openfda', {})

    def first(lst):
        return lst[0] if lst else 'N/A'

    return {
        'brand_name':        first(openfda.get('brand_name',        [])),
        'generic_name':      first(openfda.get('generic_name',      [])),
        'manufacturer':      first(openfda.get('manufacturer_name', [])),
        'category':          first(openfda.get('product_type',      [])),
        'uses':              first(drug.get('indications_and_usage', [])),
        'warnings':          first(drug.get('warnings',             [])),
        'side_effects':      first(drug.get('adverse_reactions',    [])),
        'mechanism_of_action': first(drug.get('mechanism_of_action', [])),
        'source':            'openfda'
    }


def fetch_from_groq(medicine_name: str):
    """
    Ask Groq (llama3-8b-8192) to return structured medicine information.
    Used as a final fallback when the user searches a brand/trade name
    that OpenFDA doesn't recognise.
    Returns a formatted dict or None.
    """
    if not GROQ_API_KEY:
        print("⚠️ GROQ_API_KEY not set — skipping Groq fallback")
        return None

    prompt = f"""You are a medical information assistant. The user searched for the medicine: "{medicine_name}".

Return ONLY a valid JSON object (no markdown, no explanation, no extra text) with exactly these keys:
{{
  "brand_name": "...",
  "generic_name": "...",
  "manufacturer": "...",
  "category": "...",
  "uses": "...",
  "warnings": "...",
  "side_effects": "...",
  "mechanism_of_action": "..."
}}

Rules:
- If "{medicine_name}" is a brand/trade name (e.g. Dolo, Crocin, Motrin), fill in the correct generic name.
- Keep each field concise (2-4 sentences max for long fields).
- If a field is genuinely unknown, use "N/A".
- Return ONLY the JSON. Nothing else."""

    try:
        resp = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type':  'application/json'
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'temperature': 0.1,
                'max_tokens':  600,
                'messages': [
                    {'role': 'system', 'content': 'You are a precise medical information assistant. Always respond with valid JSON only.'},
                    {'role': 'user',   'content': prompt}
                ]
            },
            timeout=15
        )

        if resp.status_code != 200:
            print(f"Groq API error: {resp.status_code} {resp.text[:200]}")
            return None

        raw = resp.json()['choices'][0]['message']['content'].strip()

        # Strip markdown fences if model wraps in ```json ... ```
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
            raw = raw.strip()

        data = json.loads(raw)

        # Ensure all required keys exist
        required = ['brand_name', 'generic_name', 'manufacturer', 'category',
                    'uses', 'warnings', 'side_effects', 'mechanism_of_action']
        for key in required:
            if key not in data:
                data[key] = 'N/A'

        data['source'] = 'groq_ai'
        print(f"✅ Groq AI returned data for '{medicine_name}'")
        return data

    except json.JSONDecodeError as e:
        print(f"Groq JSON parse error: {e} — raw: {raw[:200]}")
        return None
    except Exception as e:
        print(f"Groq fetch error: {e}")
        return None


# ========================================
# ROUTES - HOME & NAVIGATION
# ========================================

@app.route("/")
def home():
    """Public landing page — visible to everyone, no auth required"""
    return render_template('index.html')

@app.route("/landingpage")
def landingpage():
    """Logged-in user dashboard"""
    return render_with_supabase('landingpage.html')

@app.route("/trend-tracking")
def trend_tracking_page():
    """Trend & history tracking page"""
    return render_with_supabase('trend_tracking.html')

@app.route("/dashboard")
def dashboard():
    return render_with_supabase('dashboard.html')

# ========================================
# ROUTES - AUTHENTICATION PAGES
# ========================================

@app.route("/signup")
def signup_page():
    return render_with_supabase('signup.html')

@app.route("/login")
def login_page():
    return render_with_supabase('login.html')

# ========================================
# ROUTES - MEDICAL REPORT ANALYZER
# ========================================

@app.route("/report-analyzer")
def report_analyzer_page():
    return render_with_supabase('report_analyzer.html')

@app.route("/upload-report", methods=["POST"])
def upload_report():
    """Medical Report Analyzer endpoint"""
    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    language = request.form.get("language", "english").lower()
    supported_languages = ["english", "hindi", "malayalam", "tamil", "telugu",
                           "kannada", "marathi", "bengali", "gujarati", "urdu", "odia"]
    if language not in supported_languages:
        language = "english"

    print(f"\n🌐 Selected Language: {language.upper()}")

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    try:
        print("\n🔍 Step 1: Extracting text from report...")
        extracted_text = extract_text(file_path)

        print("\n📊 Step 2: Parsing test values...")
        parsed_values = parse_report(extracted_text)

        print("\n⚠️ Step 3: Checking for abnormal values...")
        abnormal_values = check_abnormal_values(parsed_values)

        print(f"\n🤖 Step 4: Generating AI explanations in {language.upper()}...")
        for test_name, details in abnormal_values.items():
            print(f"   → Generating {language} explanation for {test_name}...")
            explanation = interpret_abnormality(
                test_name=test_name,
                value=details.get("value"),
                normal_range=details.get("normal_range"),
                status=details.get("status"),
                language=language,
                skip_ai=details.get("skip_ai", False),   # ← NEW
            )
            details["explanation"] = explanation
            print(f"   ✅ {language.capitalize()} explanation generated for {test_name}")

        print("\n✨ Analysis complete!\n")

        # Build all_values: every parsed metric with [min, max] normal range for trend tracking
        # parsed_values format: { test_name: float_value }
        all_values = {}
        for test_name, raw_value in parsed_values.items():
            abnormal_info    = abnormal_values.get(test_name, {})
            normal_range_str = abnormal_info.get("normal_range", "")
            normal_range_arr = None
            try:
                if isinstance(normal_range_str, list) and len(normal_range_str) == 2:
                    normal_range_arr = [float(normal_range_str[0]), float(normal_range_str[1])]
                elif isinstance(normal_range_str, str) and "-" in normal_range_str:
                    parts = normal_range_str.split("-")
                    normal_range_arr = [float(parts[0].strip()), float(parts[1].strip())]
            except Exception:
                normal_range_arr = None

            all_values[test_name] = {
                "value":            raw_value,
                "unit":             abnormal_info.get("unit", ""),
                "normal_range":     normal_range_str,
                "normal_range_arr": normal_range_arr
            }

        return jsonify({
            "message":        "Report analyzed successfully",
            "filename":       file.filename,
            "language":       language,
            "abnormal_values": abnormal_values,
            "all_values":     all_values
        })

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}\n")
        return jsonify({"error": "Failed to analyze report", "details": str(e)}), 500

# ========================================
# ROUTES - SCAN REPORT ANALYZER
# ========================================

@app.route("/scan-analyzer")
def scan_analyzer_page():
    return render_with_supabase('scan_analyzer.html')

@app.route("/upload-scan", methods=["POST"])
def upload_scan():
    """Scan Report Analyzer endpoint"""
    if "file" not in request.files:
        return jsonify({"error": "No file sent"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

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
        print("\n🔍 Step 1: Analyzing scan image with AI...")

        if file_ext == '.pdf':
            return jsonify({"error": "PDF support coming soon. Please upload JPG or PNG for now."}), 400

        result = interpret_scan(file_path, language)

        if result.get("success"):
            print(f"\n✅ Scan analysis complete in {language.upper()}\n")
            return jsonify({
                "message":  "Scan analyzed successfully",
                "filename": file.filename,
                "language": language,
                "analysis": result.get("analysis")
            })
        else:
            print(f"\n⚠️ Scan analysis failed\n")
            return jsonify({
                "error":            "Failed to analyze scan",
                "details":          result.get("error", "Unknown error"),
                "fallback_message": result.get("analysis")
            }), 500

    except Exception as e:
        print(f"\n❌ Error during scan analysis: {str(e)}\n")
        return jsonify({"error": "Failed to analyze scan", "details": str(e)}), 500

# ========================================
# ROUTES - MEDICINE LOOKUP
# ========================================

@app.route("/medicine-lookup")
def medicine_lookup_page():
    return render_with_supabase('medicine_lookup.html')


@app.route('/api/search-medicine', methods=['GET'])
def search_medicine_api():
    """
    Medicine search with three-tier fallback:
      1. Supabase cache (exact + partial match on brand/generic name)
      2. OpenFDA API  (chemical/generic name search)
      3. Groq AI      (brand/trade name fallback — always returns something)
    """
    medicine_name = request.args.get('name', '').strip()

    if not medicine_name:
        return jsonify({'success': False, 'message': 'Medicine name is required'}), 400

    print(f"\n🔍 Searching for: {medicine_name}")

    # ── Tier 1: Supabase ──────────────────────────────────────────────────────
    db_result = search_in_supabase(medicine_name)
    if db_result:
        return jsonify({'success': True, 'source': 'database', 'data': db_result})

    # ── Tier 2: OpenFDA ───────────────────────────────────────────────────────
    print("→ Not in Supabase. Trying OpenFDA...")
    openfda_result = fetch_from_openfda(medicine_name)
    if openfda_result:
        insert_medicine_to_supabase(openfda_result)
        return jsonify({'success': True, 'source': 'openfda', 'data': openfda_result})

    # ── Tier 3: Groq AI fallback ──────────────────────────────────────────────
    print("→ Not in OpenFDA. Trying Groq AI fallback...")
    groq_result = fetch_from_groq(medicine_name)
    if groq_result:
        # Cache the Groq result so future searches hit Supabase first
        insert_medicine_to_supabase(groq_result)
        return jsonify({'success': True, 'source': 'groq_ai', 'data': groq_result})

    print("❌ All sources exhausted — medicine not found")
    return jsonify({'success': False, 'message': f'Could not find information for "{medicine_name}"'}), 404


# ========================================
# ROUTES - MEDICINE SIMPLIFICATION
# ========================================

@app.route('/api/simplify-medicine', methods=['POST'])
def simplify_medicine():
    """
    Takes raw OpenFDA medicine text (uses, mechanism, side_effects, warnings)
    and asks Groq to rewrite it in simple, plain language a non-doctor can understand.
    """
    body = request.get_json(silent=True) or {}

    brand_name   = body.get('brand_name',          'this medicine')
    generic_name = body.get('generic_name',         '')
    uses         = body.get('uses',                 'N/A')
    mechanism    = body.get('mechanism_of_action',  'N/A')
    side_effects = body.get('side_effects',         'N/A')
    warnings     = body.get('warnings',             'N/A')

    if not GROQ_API_KEY:
        return jsonify({'success': False, 'message': 'Groq API key not configured'}), 503

    # OpenFDA text can be extremely long — truncate each field to avoid
    # exceeding Groq's context window (llama3-8b has ~8k tokens)
    def trunc(text, chars=800):
        return text[:chars] + '...' if len(text) > chars else text

    uses_t     = trunc(uses)
    mechanism_t = trunc(mechanism, 600)
    side_effects_t = trunc(side_effects)
    warnings_t = trunc(warnings)

    prompt = f"""You are a friendly health educator. Rewrite the medicine info below in plain, simple language anyone can understand. No jargon. Short sentences.

Medicine: {brand_name} ({generic_name})

Return ONLY a JSON object with exactly these four keys (no markdown, no preamble):
{{
  "uses": "...",
  "mechanism_of_action": "...",
  "side_effects": "...",
  "warnings": "..."
}}

USES: {uses_t}
HOW IT WORKS: {mechanism_t}
SIDE EFFECTS: {side_effects_t}
WARNINGS: {warnings_t}"""

    try:
        resp = requests.post(
            'https://api.groq.com/openai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {GROQ_API_KEY}',
                'Content-Type':  'application/json'
            },
            json={
                'model': 'llama-3.3-70b-versatile',
                'temperature': 0.2,
                'max_tokens':  1000,
                'messages': [
                    {'role': 'system', 'content': 'You are a plain-language medical writer. Always respond with valid JSON only, no markdown.'},
                    {'role': 'user',   'content': prompt}
                ]
            },
            timeout=20
        )

        if resp.status_code != 200:
            print(f"Groq simplify error: {resp.status_code}")
            return jsonify({'success': False, 'message': 'Groq API error'}), 502

        raw = resp.json()['choices'][0]['message']['content'].strip()

        # Strip markdown fences if present
        if raw.startswith('```'):
            raw = raw.split('```')[1]
            if raw.startswith('json'):
                raw = raw[4:]
            raw = raw.strip()

        simplified = json.loads(raw)

        # Ensure all keys exist
        for key in ['uses', 'mechanism_of_action', 'side_effects', 'warnings']:
            if key not in simplified:
                simplified[key] = 'N/A'

        print(f"✅ Medicine simplified for '{brand_name}'")
        return jsonify({'success': True, 'simplified': simplified})

    except json.JSONDecodeError as e:
        print(f"Simplify JSON parse error: {e}")
        return jsonify({'success': False, 'message': 'Could not parse simplified response'}), 500
    except Exception as e:
        print(f"Simplify error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500
    


# ========================================
# ROUTES - FOOTER PAGES
# ========================================

@app.route("/about")
def about_page():
    return render_template('about_us.html')

@app.route("/ethics")
def ethics_page():
    return render_template('ethics.html')

@app.route("/terms")
def terms_page():
    return render_template('terms.html')

@app.route("/contact")
def contact_page():
    return render_template('contact.html')



# ========================================
# ROUTES - AI CHATBOT (RAG)
# ========================================

@app.route("/ai-assistant")
def ai_assistant_page():
    if not CHATBOT_INITIALIZED:
        return render_with_supabase('error.html',
                                    message="AI Chatbot is currently unavailable. Please try again later.")
    return render_with_supabase('ai_assistant.html')

@app.route("/get", methods=["GET", "POST"])
def chat():
    if not CHATBOT_INITIALIZED:
        return jsonify({"error": "AI Chatbot not initialized"}), 503

    msg = request.form.get("msg")
    if not msg:
        return "Please provide a message", 400

    print(f"\n💬 User: {msg}")
    try:
        response = rag_chain.invoke({"input": msg})
        answer   = str(response["answer"])
        print(f"🤖 Bot: {answer[:100]}...")
        return answer
    except Exception as e:
        print(f"❌ Chatbot Error: {e}")
        return "AI service is temporarily busy. Please try again later."

# ========================================
# ROUTES - HEALTH CHECK
# ========================================

@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "healthy",
        "services": {
            "medical_report_analyzer": "active",
            "scan_report_analyzer":    "active",
            "medicine_lookup":         "active",
            "ai_chatbot":              "active" if CHATBOT_INITIALIZED else "unavailable"
        },
        "medicine_lookup_sources": ["supabase", "openfda", "groq_ai"],
        "supported_languages": {
            "report_analyzer": ["english", "hindi", "malayalam", "tamil", "telugu",
                                "kannada", "marathi", "bengali", "gujarati", "urdu", "odia"],
            "scan_analyzer":   ["english", "hindi", "malayalam"],
            "chatbot":         ["english"]
        }
    })

# ========================================
# MAIN
# ========================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🏥 MEDINSIGHT AI - Unified Backend Server")
    print("="*70)
    print("\n📋 Available Services:")
    print("   1. ✅ Medical Report Analyzer")
    print("   2. ✅ Scan Report Analyzer")
    print("   3. ✅ Medicine Lookup  (Supabase → OpenFDA → Groq AI)")
    print("   4. ✅ AI Medical Assistant Chatbot (RAG)")
    print("\n🔐 Authentication: /signup  /login  (Supabase JS SDK)")
    print("\n🌐 Server: http://127.0.0.1:5000")
    print("="*70 + "\n")

    app.run(debug=True, host="127.0.0.1", port=5000)