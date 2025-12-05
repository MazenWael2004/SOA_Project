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

@app.route("/api/customers/<customer_id>")
def get_customer_by_id(customer_id):
    cursor.execute("SELECT * FROM customers WHERE customer_id = %s",(int(customer_id),))
 
    user = cursor.fetchone()  # Each row is now a dict
    if(user):
        return jsonify({"message":"User Successfully retrieved","data":user})
    else:
        return jsonify({"message":"User not Found"})
    

@app.route("/api/customers/orders/<customer_id>")
def get_order_history(customer_id):
    sql = """
SELECT c.customer_id, c.name, o.product_id, o.total_amount
FROM customers c, orders o
WHERE c.customer_id = %s
AND c.customer_id = o.customer_id
"""
    cursor.execute(sql,(int(customer_id),))
    orders = cursor.fetchall()
    return jsonify(orders)
        
    

if __name__ == "__main__":
    app.run(debug=True,port=5004)
