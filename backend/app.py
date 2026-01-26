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

    query = query = query = """
SELECT
    l.base_name,

    MAX(l.uses) AS uses,
    MAX(l.how_it_works) AS how_it_works,
    MAX(l.common_side_effects) AS common_side_effects,
    MAX(l.serious_side_effects) AS serious_side_effects,

    GROUP_CONCAT(DISTINCT dp.ingredient_name SEPARATOR ' + ') AS composition

FROM medicine_lookup_final_then l
JOIN medicines m
    ON m.medicine_name = l.base_name
JOIN medicine_drug_map mdm
    ON mdm.medicine_id = m.medicine_id
JOIN drug_profiles dp
    ON dp.drug_id = mdm.drug_id

WHERE l.base_name LIKE %s
GROUP BY l.base_name
LIMIT 1;
"""



    cursor.execute(query, (f"%{name}%",))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return jsonify({"error": "Medicine not found"}), 404

    # ---------- FORMAT FOR FRONTEND ----------
    response = {
    "name": row["base_name"],
    "category": "Medicine",
    "composition": row["composition"] if row["composition"] else "Not available",
    "uses": row["uses"].split("; ") if row["uses"] else [],
    "action": row["how_it_works"] if row["how_it_works"] else "",
    "common": row["common_side_effects"].split(", ") if row["common_side_effects"] else [],
    "serious": row["serious_side_effects"].split(", ") if row["serious_side_effects"] else []
}


    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True)
