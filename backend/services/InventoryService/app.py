import mysql.connector
from flask import Flask, jsonify
from dotenv import load_dotenv
import os

load_dotenv('../../.env')

app = Flask(__name__)

db = mysql.connector.connect(
    host=os.getenv('MYSQL_HOST'),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DB")
)

# Use dictionary=True to get column names
cursor = db.cursor(dictionary=True)


@app.route("/api/inventory")
def get_inventory():
    cursor.execute("SELECT * FROM inventory")
    inventory = cursor.fetchall()  # Each row is now a dict
    return jsonify(inventory)

@app.route("/api/inventory/check/<product_id>")
def check_product_availabilty(product_id):
    sql = "SELECT * FROM inventory WHERE product_id = %s AND quantity_available > 0"
    cursor.execute(sql,(int(product_id),))
    product = cursor.fetchone()
    if product:
        return jsonify({"isAvailable": True, "product": product})
    else:
        return jsonify({"isAvailable": False, "message": "Out of stock or not found"})
   


if __name__ == "__main__":
    app.run(port=5002, debug=True)