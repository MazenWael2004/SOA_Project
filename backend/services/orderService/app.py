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
    


@app.route("/orders/<int:order_id>")
def get_orders(order_id):
    # initilize con and cursor
    con = None
    cursor = None
    try:
        # setup
        con = getCon()
        cursor = con.cursor(dictionary = True)
        sql_select_order = "SELECT * FROM orders JOIN order_items ON orders.order_id = order_items.order_id  WHERE orders.order_id = %s"
        cursor.execute(sql_select_order, (order_id,))
        rows = cursor.fetchall()
        if not rows:
            raise ValueError(f"No Order with ID: {order_id}")
        customer_id = rows[0]["customer_id"]
        order_date = rows[0]["order_date"]
        total_amount = rows[0]["total_amount"]
        products = []
        for row in rows:
            product_id = row["product_id"]
            quantity = row["quantity"]
            unit_price = row ["unit_price"]
            products += [{"product_id" : product_id, "quantity": quantity, "unit_price" : unit_price }]

        return jsonify({"customer_id":customer_id ,"order_date": order_date, "total_amount" : total_amount, "products": products}), 200
    except ValueError as ve:
        return jsonify({"message" : str(ve) , "status": 404 , "status_text":"Not Found" }), 404
    finally:
        if cursor: cursor.close()
        if con: con.close()

def validate_order_input(data):
    if not data:
        raise ValueError("Empty or Invalid")
    if 'customer_id' not in data or 'products' not in data or 'total_amount' not in data:
        raise ValueError("Required Field Missing")
    
def validate_customer(cursor,customer_id):
    sql_Select_customer_id = "SELECT customer_id  FROM customers WHERE customer_id = %s "
    # get connection and cursor for transaction
    cursor.execute(sql_Select_customer_id, (customer_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"No customer with ID {customer_id}")

def insert_order(cursor,customer_id, total_amount,return_order_id):

    sql_insert_orders = "INSERT INTO orders (customer_id, total_amount) values (%s, %s)"
    cursor.execute(sql_insert_orders, (customer_id, total_amount))
    if return_order_id:
        order_id = cursor.lastrowid
        return order_id

def get_product(cursor,product_id):

    sql_get_product = "SELECT *  FROM inventory WHERE  product_id = %s "
    cursor.execute(sql_get_product, (product_id,))
    product = cursor.fetchone()
    if not product:
        raise ValueError(f"Product with ID {product_id}, does not exist")

    return product
def insert_order_item(cursor,order_id , product_id , unit_price , quantity):

    sql_insert_order_items = "INSERT INTO order_items (order_id , product_id , unit_price , quantity) values(%s , %s , %s , %s)"
    cursor.execute(sql_insert_order_items ,(order_id , product_id , unit_price , quantity))

@app.route("/api/orders/create", methods=["POST"])
def create_order():
    # initilize con and cursor
    con = None
    cursor = None
    try:
        data  = request.get_json() # To access the request body
        validate_order_input(data)
        # get values from data
        customer_id = data.get('customer_id') # access the parameter 'customer_id'
        products = data.get('products')
        total_amount = data.get('total_amount')

        con = getCon()
        cursor = con.cursor(dictionary = True)
        con.start_transaction()
        # validate customer id
        validate_customer(cursor= cursor,customer_id= customer_id)
        # insert into the orders table this will generate the order_id and date
        order_id = insert_order(cursor= cursor, customer_id=customer_id, total_amount=total_amount,return_order_id= True)
        for product in products:
            product_id = product['product_id']
            quantity = product ['quantity']
            # get the unit_price of the product and check that quantity is available
            temp_product = get_product(cursor= cursor, product_id= product_id)
            unit_price = temp_product["unit_price"]
            quantity_available = temp_product["quantity_available"]
            if quantity_available < quantity:
                raise ValueError(f"Insufficient Stock for product {product_id}")
            insert_order_item(cursor= cursor, order_id=order_id , product_id=product_id , unit_price=unit_price , quantity=quantity)
        con.commit()  
        return jsonify({"message": "Order created successfully","order_id":order_id, "status": 201 , "status_text" : "Created"}), 201 
    except ValueError as ve:
        # json returned is invalid or empty
        if con : con.rollback()
        return jsonify( {"message": str(ve) , "status": 400 , "status_text":"Bad Request" } ), 400
    except KeyError as ke:
        return jsonify( {"message": str(ke), "status": 400 , "status_text":"Bad Request"} ), 400
    except Exception as e:
        return jsonify( {"message": str(e), "status": 500 , "status_text" : "Internal Server Error" } ), 500
    finally:
        if cursor :cursor.close()
        if con :con.close()


if __name__ == "__main__":
    app.run(port=5001, debug=True)