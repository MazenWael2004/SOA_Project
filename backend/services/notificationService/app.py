
from flask import Flask,request, jsonify
import requests
from dotenv import load_dotenv
from models import NotificationLog
from flask_migrate import Migrate
from config import Config
from database import db
import os


load_dotenv('../../.env')

ORDER_URL = "http://localhost:5001/api/orders/"
CUSTOMER_URL ="http://localhost:5004/api/customers/"

# db = mysql.connector.connect(
#     host=os.getenv('MYSQL_HOST'),
#     user=os.getenv("MYSQL_USER"),
#     password=os.getenv("MYSQL_PASSWORD"),
#     database=os.getenv("MYSQL_DB")
# )
app = Flask(__name__)

@app.route("/api/notifications/send", methods=["POST"])
def send_order_notification():
    # get body
    data = request.get_json()

    # validate body
    if not data :
        return jsonify({"error": "Nothing was send in request body", "status": 400, "status_text": "Bad Request"}), 400
    
    # extract order_id from body
    order_id = data["order_id"]

    # validate order_id is not empty
    if not order_id :
        return jsonify({"error": "Body is missing order_id", "status": 400, "status_text": "Bad Request"}), 400
    
    # validate order_id is an integer
    if not isinstance(order_id, int):
        return jsonify({"error": "order_id must be an integer ", "status": 400, "status_text": "Bad Request"}), 400
    
    # verify order exists done through call to order services and return order details
    order_payload = {"order_id": order_id}

    try :
        order_response = requests.get(f"{ORDER_URL}{order_id}")
        if order_response.status_code != 200:
            raise ValueError(f"Failed to locate order with id {order_id}")
        order_data = order_response.json()
    except ValueError as ve :
        return jsonify({"error": str(ve), "status": 400}), 400
    
    # get contact information from customer using their id in the customer_order
    customer_id = order_data["customer_id"]

    try:
        customer_response = requests.get(f"{CUSTOMER_URL}{customer_id}")
        if customer_response.status_code != 200 :
            raise ValueError(f"Failed to get Customer details for customer with id {customer_id}")
        customer_data = customer_response.json()
        customer_email = customer_data["email"]
    except ValueError as ve:
        return jsonify({"error": str(ve),"status": 400}), 400







    




if __name__ == "__main__":
    app.run(debug=True,port=5005)
