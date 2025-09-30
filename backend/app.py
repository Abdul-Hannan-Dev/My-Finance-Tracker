import os
import uuid
import logging
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from db_client import LocalDB
from categorizer import Categorizer

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

db = LocalDB()
categorizer = Categorizer()

@app.route('/')
def index():
    return render_template('upload.html')



@app.route("/register", methods=["POST"])
def register():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    try:
        user_id = db.register_user(username, password)
        return jsonify({"user_id": user_id, "message": "User registered successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Missing username or password"}), 400
    user_id = db.authenticate(username, password)
    if user_id:
        return jsonify({"user_id": user_id, "message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401

@app.route("/upload", methods=["POST"])
def upload_csv():
    if "file" not in request.files or "user_id" not in request.form:
        return jsonify({"error": "Missing file or user_id"}), 400

    file = request.files["file"]
    user_id = request.form["user_id"]
    try:
        df = pd.read_csv(file)
        df.columns = df.columns.str.strip().str.lower()
        transactions = []
        for _, row in df.iterrows():
            txn = {
                "transaction_id": str(uuid.uuid4()),
                "user_id": user_id,
                "date": row["date"],
                "description": row["description"],
                "amount": row["amount"],
                "category": categorizer.categorize(row["description"]),
            }
            db.put(txn)
            transactions.append(txn)
        return jsonify({"message": "Transactions processed successfully", "count": len(transactions), "transactions": transactions})
    except Exception as e:
        logger.exception("Error processing upload")
        return jsonify({"error": str(e)}), 500

@app.route("/transactions", methods=["GET"])
def get_transactions():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400
    filters = {k: v for k, v in {
        "category": request.args.get("category"),
        "month": request.args.get("month"),
        "year": request.args.get("year")
    }.items() if v}
    try:
        txns = db.get_transactions(user_id, filters)
        return jsonify(txns)
    except Exception as e:
        logger.exception("Error fetching transactions")
        return jsonify({"error": str(e)}), 500
    

@app.route("/summary", methods=["GET"])
def get_summary():
    try:
        user_id = request.args.get("user_id")
        if not user_id:
            return jsonify({"error": "Missing user_id"}), 400

        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")
        categories = request.args.getlist("category")
        descriptions = request.args.getlist("description")

        txns = db.get_transactions(user_id)

        total_amount = sum(float(t["amount"]) for t in txns)

        filtered_txns = txns
        if start_date:
            filtered_txns = [t for t in filtered_txns if t["date"] >= start_date]
        if end_date:
            filtered_txns = [t for t in filtered_txns if t["date"] <= end_date]
        if categories:
            filtered_txns = [t for t in filtered_txns if t["category"] in categories]
        if descriptions:
            filtered_txns = [t for t in filtered_txns if t["description"] in descriptions]

        filtered_total = sum(float(t["amount"]) for t in filtered_txns)

        percentage = round((filtered_total / total_amount * 100), 2) if total_amount else 0

        return jsonify({
            "total_spent": total_amount,
            "filtered_spent": filtered_total,
            "percentage_of_total": percentage
        })

    except Exception as e:
        logger.exception("Error preparing summary")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
