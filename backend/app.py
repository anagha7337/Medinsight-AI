from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector

app = Flask(__name__)
CORS(app)

# ---------- DATABASE CONNECTION ----------
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        port=3307, 
        user="root",
        password="banana@1234",
        database="medinsight_ai"
    )

# ---------- API ROUTE ----------
@app.route("/api/medicine")
def medicine_lookup():
    name = request.args.get("name", "").lower().strip()

    if not name:
        return jsonify({"error": "No medicine name provided"}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
        SELECT 
            base_name,
            uses,
            how_it_works,
            common_side_effects,
            serious_side_effects
        FROM medicine_lookup_final_then
        WHERE base_name LIKE %s
        LIMIT 1
    """

    cursor.execute(query, (f"%{name}%",))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return jsonify({"error": "Medicine not found"}), 404

    # ---------- FORMAT FOR FRONTEND ----------
    response = {
        "name": row["base_name"].title(),
        "category": "Medicine",  # optional, static for now
        "composition": "See chemical composition in report",
        "uses": row["uses"].split("; "),
        "action": row["how_it_works"],
        "common": row["common_side_effects"].split(", "),
        "serious": row["serious_side_effects"].split(", ")
    }

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
