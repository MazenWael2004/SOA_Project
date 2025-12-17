
from flask import Flask,request, jsonify
import requests
from dotenv import load_dotenv
from models import NotificationLog
from flask_migrate import Migrate
from config import Config
from database import db #type:ignore
import os


load_dotenv('../../.env')



ORDER_URL = "http://localhost:5001/api/orders/"
CUSTOMER_URL ="http://localhost:5004/api/customers/"
INVENTORY_URL= "http://localhost:5002/api/inventory/check/"

# db = mysql.connector.connect(
#     host=os.getenv('MYSQL_HOST'),
#     user=os.getenv("MYSQL_USER"),
#     password=os.getenv("MYSQL_PASSWORD"),
#     database=os.getenv("MYSQL_DB")
# )
app = Flask(__name__)

app.config.from_object(Config)
db.init_app(app)
Migrate(app, db)

@app.route("/api/notifications/send", methods=["POST"])
def send_order_notification():
    # get body
    data = request.get_json()
    # validate body
    if not data :
        return jsonify({"error": "Nothing was send in request body", "status": 400, "status_text": "Bad Request"}), 400
    # extract order_id from body
    order_id = data.get("order_id")

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
        order_products = order_data["products"]
    except ValueError as ve :
        return jsonify({"error": str(ve), "status": 404}), 404
    
    # get contact information from customer using their id in the customer_order
    # and get customer contact information
    customer_id = order_data["customer_id"]

    try:
        customer_response = requests.get(f"{CUSTOMER_URL}{customer_id}")
        if customer_response.status_code != 200 :
            raise ValueError(f"Failed to get Customer details for customer with id {customer_id}")
        customer_data = customer_response.json()
        customer_email = customer_data["email"]
        customer_phone = customer_data["phone"]
    except ValueError as ve:
        return jsonify({"error": str(ve),"status": 404}), 404
    
    #check product existence in inventory
    try :
        for product in order_products :
            inventory_response = requests.get(f"{INVENTORY_URL}{product['product_id']}")
            if inventory_response.status_code != 200 :
                raise ValueError(f"product with id: {product['product_id']} was unable to be located")
            inventory_data = inventory_response.json()
            if product['quantity'] > inventory_data['quantity_available'] :
                raise ValueError(f"Insufficient Stock for product with id {product['product_id']}")
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    
    # generate Notification message
    message = f"Dear {customer_data['name']}, you're order #{order_id}, has been confirmed.\n All items are in stock and will be shipped soon."

    # print to console 
    print(f"Sent to : {customer_email}")
    print(f"Subject: completion of order {order_id}")
    print(f"Body: {message}")

    # add log to database

    log = NotificationLog(
        order_id = order_id,
        customer_id = customer_id,
        notification_type = "EMAIL",
        message = message
    )

    db.session.add(log)
    db.session.commit()
    return jsonify({"message":"notification sent"}),200







    




if __name__ == "__main__":
    app.run(debug=True,port=5005)
