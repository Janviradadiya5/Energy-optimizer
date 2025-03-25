import os
import json
import statistics
import logging
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
from sklearn.linear_model import LinearRegression

# Configure logging.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = Flask(__name__)
CORS(app)

# Path to the JSON pseudo-database.
DB_FILE = os.path.join(os.path.dirname(__file__), 'db.json')

def load_db():
    """Load or initialize the JSON database."""
    if not os.path.exists(DB_FILE):
        logging.info("DB file not found. Creating new db.json file.")
        with open(DB_FILE, 'w') as f:
            json.dump({"bills": [], "appliance_usages": []}, f, indent=4)
    with open(DB_FILE, 'r') as f:
        data = json.load(f)
    return data

def save_db(data):
    """Save updated data to the JSON database."""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def get_next_id(items):
    """Return the next available ID from the list."""
    return 1 if not items else max(item.get("id", 0) for item in items) + 1

def calculate_energy_usage(power_rating, usage_hours):
    """Calculate energy usage in kWh."""
    return (power_rating * usage_hours) / 1000

def generate_recommendation(current_units, previous_units):
    """Return a recommendation if current usage exceeds previous usage by more than 20%."""
    if previous_units > 0 and current_units > previous_units * 1.2:
        return ("Warning: Your consumption increased by over 20%. "
                "Consider reducing appliance usage for cost savings.")
    return "Good job! Your energy consumption is within expected limits."

def predict_next_value(values):
    """Predict the next value using Linear Regression. Returns the last value if there is insufficient data."""
    if len(values) < 2:
        return values[-1] if values else 0
    X = np.arange(len(values)).reshape(-1, 1)
    y = np.array(values)
    model = LinearRegression()
    model.fit(X, y)
    next_index = np.array([[len(values)]])
    return model.predict(next_index)[0]

def log_request_data(data):
    logging.info("Received data: %s", data)

################################
# Registration Endpoint
################################
@app.route("/api/register", methods=["POST"])
def register():
    """
    Registration endpoint.
    Expected JSON payload:
      { "user_id": "uniqueUserID123" }
    Checks that the user_id is not already taken.
    """
    try:
        data = request.get_json()
    except Exception as e:
        logging.error("Error parsing registration JSON: %s", e)
        return jsonify({"error": "Invalid JSON", "detail": str(e)}), 400

    user_id = data.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required."}), 400

    db_data = load_db()
    for bill in db_data.get("bills", []):
        if bill.get("user_id") == user_id:
            return jsonify({"error": "User ID already taken."}), 409

    # Registration success.
    return jsonify({"user_id": user_id}), 200

################################
# (Optional) Login Endpoint
################################
@app.route("/api/login", methods=["POST"])
def login():
    """
    A simple login endpoint.
    Expected JSON payload: { "username": "demo", "password": "demo123" }
    Uses hard-coded users for demonstration.
    """
    try:
        data = request.get_json()
    except Exception as e:
        logging.error("Error parsing login JSON: %s", e)
        return jsonify({"error": "Invalid JSON", "detail": str(e)}), 400

    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return jsonify({"error": "Username and password are required."}), 400

    users = {
        "demo": {"user_id": "user123", "password": "demo123"},
        "john": {"user_id": "user456", "password": "password456"}
    }
    if username in users and users[username]["password"] == password:
        logging.info("User '%s' logged in successfully.", username)
        return jsonify({"user_id": users[username]["user_id"], "username": username}), 200
    else:
        return jsonify({"error": "Invalid credentials."}), 401

################################
# Data Submission Endpoint
################################
@app.route("/api/submit_data", methods=["POST"])
def submit_data():
    """
    Processes the energy data submission and returns predictions.
    Expected JSON payload:
    {
      "user_id": "user123",
      "month": "Jan 2023",
      "total_units": 150,
      "bill_amount": 3000,
      "appliances": [
         { "name": "AC", "power_rating": 1500, "usage_hours": 5 },
         { "name": "Washing Machine", "power_rating": 500, "usage_hours": 2 }
      ]
    }
    """
    try:
        data = request.get_json()
    except Exception as e:
        logging.error("Error parsing data JSON: %s", e)
        return jsonify({"error": "Invalid JSON data", "detail": str(e)}), 400

    log_request_data(data)
    user_id = data.get("user_id")
    month = data.get("month")
    total_units = data.get("total_units")
    bill_amount = data.get("bill_amount")
    appliances = data.get("appliances", [])
    if not month or total_units is None or bill_amount is None:
        return jsonify({"error": "Month, total_units, and bill_amount are required."}), 400

    db_data = load_db()
    new_bill = {
        "id": get_next_id(db_data["bills"]),
        "user_id": user_id,
        "month": month,
        "total_units": total_units,
        "bill_amount": bill_amount,
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    db_data["bills"].append(new_bill)

    appliance_responses = []
    for appl in appliances:
        appliance_name = appl.get("name")
        power_rating = appl.get("power_rating")
        usage_hours = appl.get("usage_hours")
        if appliance_name and power_rating is not None and usage_hours is not None:
            energy_usage = calculate_energy_usage(power_rating, usage_hours)
            new_usage = {
                "id": get_next_id(db_data["appliance_usages"]),
                "bill_id": new_bill["id"],
                "appliance_name": appliance_name,
                "power_rating": power_rating,
                "usage_hours": usage_hours,
                "energy_usage": energy_usage,
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            db_data["appliance_usages"].append(new_usage)
            appliance_responses.append({
                "appliance": appliance_name,
                "energy_usage": energy_usage
            })

    save_db(db_data)
    
    # Filter bills that belong to this user.
    bills = [b for b in db_data["bills"] if b.get("user_id") == user_id]
    sorted_bills = sorted(bills, key=lambda x: x["created_at"])
    
    # Prediction 1: Next Month's Bill Prediction.
    bill_amounts = [b["bill_amount"] for b in sorted_bills]
    predicted_next_bill = predict_next_value(bill_amounts)
    
    # Prediction 2: Overall Energy Consumption Prediction.
    total_units_list = [b["total_units"] for b in sorted_bills]
    predicted_next_total_units = predict_next_value(total_units_list)
    
    # Prediction 3: Appliance-Level Predictions & Efficiency Alerts.
    appliance_predictions = {}
    efficiency_alerts = {}
    appliance_usages = db_data["appliance_usages"]
    unique_appliances = {record["appliance_name"] for record in appliance_usages}
    for appliance in unique_appliances:
        recs = sorted([r for r in appliance_usages if r["appliance_name"] == appliance], key=lambda x: x["created_at"])
        values = [r["energy_usage"] for r in recs]
        predicted_usage = predict_next_value(values)
        appliance_predictions[appliance] = predicted_usage
        avg_usage = statistics.mean(values) if values else 0
        if values and values[-1] > avg_usage * 1.2:
            efficiency_alerts[appliance] = "Efficiency drop detected. Consider maintenance."
        else:
            efficiency_alerts[appliance] = "Normal performance."
    
    # Prediction 4: Energy Savings Simulation.
    cost_per_unit = (bill_amount / total_units) if total_units > 0 else 0
    savings_simulation = {}
    for appl in appliances:
        saving = (appl["power_rating"] / 1000.0) * cost_per_unit
        savings_simulation[appl["name"]] = saving
    
    # Prediction 5: Carbon Footprint (using factor 0.82 kg CO₂ per kWh).
    carbon_footprint = total_units * 0.82
    
    # Prediction 6: Seasonal Consumption Forecast.
    month_lower = month.lower()
    if any(s in month_lower for s in ["jun", "jul", "aug"]):
        seasonal_factor = 1.1
    elif any(s in month_lower for s in ["dec", "jan", "feb"]):
        seasonal_factor = 0.9
    else:
        seasonal_factor = 1.0
    predicted_seasonal_consumption = predicted_next_total_units * seasonal_factor
    
    # Prediction 7: Dynamic Tariff Suggestion.
    tariff_suggestion = "Operate appliances during off-peak hours (e.g., 12 AM - 6 AM)"
    if total_units < 100:
        tariff_suggestion = "Your usage is low; no specific recommendation."
    
    # Prediction 8: Solar Energy Savings (assuming a 30% offset).
    solar_savings = predicted_next_total_units * 0.3 * cost_per_unit
    
    # Prediction 9: Long-Term Financial Projection (annual).
    annual_projection = predicted_next_bill * 12
    
    # Prediction 10: Household vs. Community Benchmarking.
    benchmark = 200
    usage_benchmark = "Above Average" if total_units >= benchmark else "Below Average"
    
    # Prediction 11: Anomaly Detection.
    historical_bill_amounts = [b["bill_amount"] for b in sorted_bills if b["id"] != new_bill["id"]]
    if historical_bill_amounts:
        mean_bill = statistics.mean(historical_bill_amounts)
        std_bill = statistics.stdev(historical_bill_amounts) if len(historical_bill_amounts) > 1 else 0
    else:
        mean_bill, std_bill = bill_amount, 0
    anomaly_flag = bill_amount > (mean_bill + 2 * std_bill)
    
    # Prediction 12: Peak Demand Prediction.
    historical_units = [b["total_units"] for b in sorted_bills if b["id"] != new_bill["id"]]
    max_units = max(historical_units) if historical_units else total_units
    peak_demand_flag = total_units >= max_units
    
    response = {
        "bill": {
            "id": new_bill["id"],
            "user_id": user_id,
            "month": month,
            "total_units": total_units,
            "bill_amount": bill_amount,
            "recommendation": generate_recommendation(
                total_units,
                sorted_bills[-2]["total_units"] if len(sorted_bills) > 1 else total_units
            )
        },
        "appliances": appliance_responses,
        "predictions": {
            "predicted_next_bill": predicted_next_bill,
            "predicted_next_total_units": predicted_next_total_units,
            "appliance_level_predictions": appliance_predictions,
            "appliance_efficiency_alerts": efficiency_alerts,
            "energy_savings_simulation": savings_simulation,
            "carbon_footprint": carbon_footprint,
            "predicted_seasonal_consumption": predicted_seasonal_consumption,
            "dynamic_tariff_suggestion": tariff_suggestion,
            "solar_energy_savings": solar_savings,
            "annual_financial_projection": annual_projection,
            "usage_benchmark": usage_benchmark,
            "anomaly_flag": anomaly_flag,
            "peak_demand_prediction": "Yes" if peak_demand_flag else "No"
        }
    }
    
    logging.info("Response data: %s", response)
    return jsonify(response)

################################
# Dashboard Data Endpoint (Optional)
################################
@app.route("/api/dashboard_data", methods=["GET"])
def dashboard_data():
    """Return historical bill data for dashboard visualization, optionally filtered by user_id."""
    db_data = load_db()
    bills = db_data.get("bills", [])
    user_id = request.args.get("user_id", None)
    if user_id is not None:
        bills = [bill for bill in bills if str(bill.get("user_id", "")) == user_id]
    sorted_bills = sorted(bills, key=lambda x: x["created_at"])
    data = [{
        "month": bill["month"],
        "total_units": bill["total_units"],
        "bill_amount": bill["bill_amount"]
    } for bill in sorted_bills]
    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
