from config import Config
from flask import Flask, jsonify,request
from database import db
from dotenv import load_dotenv
import os
from flask_migrate import Migrate
import requests
from models import Customer

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
Migrate(app,db)
ORDER_HISTORY_URL="http://localhost:5001/api/orders"


@app.route("/api/customers/<customer_id>",methods=["GET"])
def get_customer_by_id(customer_id):
    cust=Customer.query.get(customer_id)
    if cust:
        return jsonify(cust.to_dict()),200
    return jsonify({"error":"no customer with name"}),404

    

@app.route("/api/customers/<int:customer_id>/orders",methods=["GET"])
def get_order_history(customer_id):
    cust = Customer.query.get(customer_id)
    if not cust:
        return jsonify({"error":"no customer found,maybe a wrong id"}),404
    try:
        response= requests.get(f"{ORDER_HISTORY_URL}/{customer_id}")
        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error":"order service returned an error"}), response.status_code

    except requests.exceptions.RequestException:
        return jsonify({"error":"failed to connect to order service"}),503

@app.route("/api/customers/<int:customer_id>/loyalty")
def update_loyalty(customer_id):
    data = request.get_json()
    points =data.get("loyalty_points")
    if points is None or points==0:
        return jsonify({"error":"missing or got zero for the parameter"}),503
    customer_id = Customer.query.get(customer_id)
    if customer_id:
        customer_id.loyalty_points =points #idk if im supposed to subtract or update directly
        db.session.commit()
        return jsonify({"Success":"points updated successfully"}),200
    return jsonify({"error":"customer not found"}),404

if __name__ == "__main__":
    app.run(debug=True,port=5004)
