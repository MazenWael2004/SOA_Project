import mysql.connector
from flask import Flask,request, jsonify
from dotenv import load_dotenv
import os


load_dotenv('../../.env')

# db = mysql.connector.connect(
#     host=os.getenv('MYSQL_HOST'),
#     user=os.getenv("MYSQL_USER"),
#     password=os.getenv("MYSQL_PASSWORD"),
#     database=os.getenv("MYSQL_DB")
# )
app = Flask(__name__)

@app.route("/api/notifications/send", methods=["POST"])
def calculate_price():
    return jsonify("Notyfifcation")




if __name__ == "__main__":
    app.run(debug=True,port=5005)
