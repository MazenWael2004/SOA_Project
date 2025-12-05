import mysql.connector
from flask import Flask,request, jsonify
from dotenv import load_dotenv
import os


load_dotenv('../../.env')


app = Flask(__name__)

def getCon():
    con= mysql.connector.connect(
        host=os.getenv('MYSQL_HOST'),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DB")
    )
    return con
    


@app.route("/orders")
def get_orders():
    orders = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
    ]
    return jsonify(orders)

@app.route("/api/orders/create", methods=["POST"])
def create_order():
    try:
        data  = request.get_json() # To access the request body
        if not data:
            raise ValueError("Empty or Invalid")
        if 'customer_id' not in data or 'products' not in data or 'total_amount' not in data:
            raise ValueError("Required Field Missing")
        customer_id = data.get('customer_id') # access the parameter 'customer_id'
        products = data.get('products')
        total_amount = data.get('total_amount')
        con = getCon()
        cursor = con.cursor(dictionary = True)
        # sql statements used
        sql_customer_id = "SELECT customer_id  FROM customers WHERE customer_id = %s "
        sql_orders = "INSERT INTO orders (customer_id, total_amount) values (%s, %s)"
        sql_order_items = "INSERT INTO order_items (order_id , product_id , unit_price , quantity) values(%s , %s , %s , %s)"
        sql_get_product_attributes = "SELECT unit_price,quantity_available  FROM inventory WHERE  product_id = %s "
        con.start_transaction()
        # validate customer id
        cursor.execute(sql_customer_id, (customer_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"No customer with ID {customer_id}")
        # insert into the orders table this will generate the order_id and date
        cursor.execute(sql_orders, (customer_id, total_amount))
        order_id = cursor.lastrowid
        # keep track of sum to check if there is a mismatch(not needed done in pricing)
        calculated_total  = 0
        price_mismatch = False
        for product in products:
            product_id = product['product_id']
            quantity = product ['quantity']
            # get the unit_price of the product and check that quantity is available
            cursor.execute(sql_get_product_attributes, (product_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Product with ID {product_id}, does not exist")
            unit_price = row["unit_price"]
            quantity_available = row["quantity_available"]
            if quantity_available < quantity:
                raise ValueError(f"Insufficient Stock for product {product_id}")
            calculated_total  += unit_price * quantity
            if calculated_total  > total_amount:
                price_mismatch = True
            cursor.execute(sql_order_items ,(order_id , product_id , unit_price , quantity))

        con.commit()  
        return jsonify({"message": "Order created successfully","order_id":order_id, "status": 200 , "status_text" : "Created"}), 201 
    except ValueError as ve:
        # json returned is invalid or empty
        con.rollback()
        return jsonify( {"message": str(ve) , "status": 400 , "status_text":"Bad Request" } ), 400
    except KeyError as ke:
        return jsonify( {"message": str(ke), "status": 400 , "status_text":"Bad Request"} ), 400
    except Exception as e:
        return jsonify( {"message": str(e), "status": 500 , "status_text" : "Internal Server Error" } ), 500
    finally:
        cursor.close()
        con.close()


if __name__ == "__main__":
    app.run(port=5001, debug=True)