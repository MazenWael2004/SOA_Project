import requests
from decimal import Decimal
from config import Config
from database import db #type:ignore
from models import Order,OrderItem
from flask import Flask,request, jsonify
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from flask_migrate import Migrate
import os


app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
Migrate(app,db)

CUSTOMER_URL = "http://localhost:5004/api/customers"
INVENTORY_URL = "http://localhost:5002/api/inventory"
PRICING_URL =   "http://localhost:5003/api/pricing/calculate"
#Used by customer service  to get orders
# @Pinebruiser please make sure to use routes that don't contradict with other routes
# i think your code needs to update to use call this version instead
@app.route("/api/orders/by_customer/<int:customer_id>",methods=["GET"])
def get_customer(customer_id):
    orders = Order.query.filter_by(customer_id=customer_id).all()
    if orders:
        return jsonify ([order.to_dict() for order in orders]),200
    return jsonify({"error":"no orders found for customer {customer_id}"}),404

@app.route("/debug/orders", methods=["GET"])
def debug_orders():
    orders = Order.query.all()
    return jsonify([
        {
            "order_id": o.order_id,
            "customer_id": o.customer_id,
            "total_amount": float(o.total_amount)
        }
        for o in orders
    ])


#update everything else here    
# note to amr please use return jsonfiy(stuff),http code
@app.route("/api/orders/<int:order_id>",methods=["GET"])
def get_orders(order_id):
    order = Order.query.filter_by(order_id = order_id).first()
    if not order:
        return jsonify({"message": f"No order with id {order_id}", "status": 404}),404
    return jsonify(order.to_dict()), 200
    # # initilize con and cursor
    # con = None
    # cursor = None
    # try:
    #     # setup
    #     con = getCon()
    #     cursor = con.cursor(dictionary = True)
    #     sql_select_order = "SELECT * FROM orders JOIN order_items ON orders.order_id = order_items.order_id  WHERE orders.order_id = %s"
    #     cursor.execute(sql_select_order, (order_id,))
    #     rows = cursor.fetchall()
    #     if not rows:
    #         raise ValueError(f"No Order with ID: {order_id}")
    #     customer_id = rows[0]["customer_id"]
    #     order_date = rows[0]["order_date"]
    #     total_amount = rows[0]["total_amount"]
    #     products = []
    #     for row in rows:
    #         product_id = row["product_id"]
    #         quantity = row["quantity"]
    #         unit_price = row ["unit_price"]
    #         products += [{"product_id" : product_id, "quantity": quantity, "unit_price" : unit_price }]

    #     return jsonify({"customer_id":customer_id ,"order_date": order_date, "total_amount" : total_amount, "products": products}), 200
    # except ValueError as ve:
    #     return jsonify({"message" : str(ve) , "status": 404 , "status_text":"Not Found" }), 404
    # finally:
    #     if cursor: cursor.close()
    #     if con: con.close()

# def validate_order_input(data):
#     if not data:
#         raise ValueError("Empty or Invalid")
#     if 'customer_id' not in data or 'products' not in data or 'total_amount' not in data:
#         raise ValueError("Required Field Missing")

# def validate_customer(cursor,customer_id):
#     sql_Select_customer_id = "SELECT customer_id  FROM customers WHERE customer_id = %s "
#     # get connection and cursor for transaction
#     cursor.execute(sql_Select_customer_id, (customer_id,))
#     row = cursor.fetchone()
#     if not row:
#         raise ValueError(f"No customer with ID {customer_id}")

# def insert_order(cursor,customer_id, total_amount,return_order_id):

#     sql_insert_orders = "INSERT INTO orders (customer_id, total_amount) values (%s, %s)"
#     cursor.execute(sql_insert_orders, (customer_id, total_amount))
#     if return_order_id:
#         order_id = cursor.lastrowid
#         return order_id

# def get_product(cursor,product_id):

#     sql_get_product = "SELECT *  FROM inventory WHERE  product_id = %s "
#     cursor.execute(sql_get_product, (product_id,))
#     product = cursor.fetchone()
#     if not product:
#         raise ValueError(f"Product with ID {product_id}, does not exist")

#     return product
# def insert_order_item(cursor,order_id , product_id , unit_price , quantity):

#     sql_insert_order_items = "INSERT INTO order_items (order_id , product_id , unit_price , quantity) values(%s , %s , %s , %s)"
#     cursor.execute(sql_insert_order_items ,(order_id , product_id , unit_price , quantity))

@app.route("/api/orders/create", methods=["POST"])
def create_order():
    # get body
    data = request.get_json()
    # existence validation
    if not data :
        return jsonify({"message": "the body was empty", "status": 400, "status_text": "Bad Request"}), 400
    # get values from the body
    customer_id = data.get("customer_id")
    # total_amount = data['total_amount'] # Testing ALERT: Commented out for service testing
    products = data.get('products')
    # validate expected values existence
    if not customer_id :
        return jsonify({"error": "Body is missing customer_id", "status": 400, "status_text": "Bad Request"}), 400
    
    # Testing ALERT: Commented out for service testing
    # if not total_amount :
    #     return jsonify({"error": "Body is missing total_amount", "status": 400, "status_text": "Bad Request"}), 400
    
    if not products :
        return jsonify({"error": "Body is missing  products, or products list is empty", "status": 400, "status_text": "Bad Request"}), 400
    
    # validate body input types
    if not isinstance(customer_id, int):
        return jsonify({"error":"customer_id must be integer"}), 400
    
    # Testing ALERT: Commented out for service testing
    # if not isinstance(total_amount, (int, float,Decimal)):
    #     return jsonify({"error":"total_amount must be numeric"}), 400
    
    if not isinstance(products, list):
        return jsonify({"error":"products must be a list"}), 400
    for product in products:
        if "product_id" not in product or "quantity" not in product:
            return jsonify({"error":"product_id and quantity required"}), 400
        if not isinstance(product["product_id"], int) or not isinstance(product["quantity"], int):
            return jsonify({"error":"product_id and quantity must be integer"}), 400

    # customer Existence validation
    if not customer_id :
        return jsonify({"error":"no customer found,maybe a wrong id"}),404
    try:
        response = requests.get(f"{CUSTOMER_URL}/{customer_id}")
        if not response.status_code ==200 :
            raise ValueError(f"Customer with id {customer_id} does not exist")
    except  requests.exceptions.RequestException:
        return jsonify({"error": "failed to connect to customer service"}), 503
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404
    # inventory validated and data returned
    unit_price = {}
    try:
# Product existence validation and item creation
        for product in products:
            # validation
            response = requests.get(f"{INVENTORY_URL}/check/{product['product_id']}")
            if response.status_code != 200:
                raise ValueError(f"Product {product['product_id']} not found")
                return jsonify({"error": f"Product {product['product_id']} not found"}), 404
            inventory_data = response.json()
            if product['quantity'] > inventory_data['quantity_available'] :
                raise ValueError(f"Insufficient stock for product {product['product_id']}")
            unit_price[product['product_id']] = inventory_data['unit_price']
    except ValueError as ve :
        return jsonify({"error": str(ve)}), 400
    # get total amount from the pricing service(reduntent but in assignment specification)
    pricing_payload = { 
            "products": [
                {"product_id": product["product_id"] , "quantity": product["quantity"] }
                for product in products]
                }
    try :
        pricing_response = requests.post(PRICING_URL, json= pricing_payload)
        if pricing_response.status_code != 200:
            raise ValueError( "Failed to calculate pricing")
        pricing_data = pricing_response.json()
        total_amount = Decimal(pricing_data["total_amount"])  
    except ValueError as ve :
        return jsonify({"error": str(ve), "status": 400}), 400

    # create the order
    try:
        order = Order(customer_id = customer_id, total_amount = total_amount)    
        # item creation
        for product in products:
            unit_price_of_product = unit_price[product['product_id']]
            item = OrderItem(product_id = product["product_id"], quantity = product["quantity"], unit_price = unit_price_of_product)
            order.items.append(item)

        # add the order
        db.session.add(order)

        # send updates to inventory service
        #  assignment specifies single service
        # note: this may lead to a partial failure in which case the orders and order item table are fine
        # but the inventory table will have some products updated and others not and be inconsistent
        # would need to preform comepnsatory action in the except block but out of project scope
        
        for product in products:
            inventory_payload = {
                "product_id": product["product_id"] ,
                "quantity": product["quantity"]
                }
            response = requests.put(
                    f"{INVENTORY_URL}/update",
                    json = inventory_payload,
                    )
            if response.status_code != 200:
                raise ValueError(f"Inventory update failed on product with ID: {product['product_id']}")
        db.session.commit()

        order_id = order.order_id
        return  jsonify({
            "message": "Order created successfully",
            "order_id": order_id,
            "status": 201 ,
            "status_text" : "Created"
            }), 201 

    except (SQLAlchemyError, ValueError, requests.exceptions.RequestException) as e:
        db.session.rollback()  # undo any partial DB changes
        return jsonify({
            "message": str(e),
            "status": 400,
            "status_text": "Bad Request"
        }), 400
    # # initilize con and cursor
    # con = None
    # cursor = None
    # try:
    #     data  = request.get_json() # To access the request body
    #     validate_order_input(data)
    #     # get values from data
    #     customer_id = data.get('customer_id') # access the parameter 'customer_id'
    #     products = data.get('products')
    #     total_amount = data.get('total_amount')

    #     con = getCon()
    #     cursor = con.cursor(dictionary = True)
    #     con.start_transaction()
    #     # validate customer id
    #     validate_customer(cursor= cursor,customer_id= customer_id)
    #     # insert into the orders table this will generate the order_id and date
    #     order_id = insert_order(cursor= cursor, customer_id=customer_id, total_amount=total_amount,return_order_id= True)
    #     for product in products:
    #         product_id = product['product_id']
    #         quantity = product ['quantity']
    #         # get the unit_price of the product and check that quantity is available
    #         temp_product = get_product(cursor= cursor, product_id= product_id)
    #         unit_price = temp_product["unit_price"]
    #         quantity_available = temp_product["quantity_available"]
    #         if quantity_available < quantity:
    #             raise ValueError(f"Insufficient Stock for product {product_id}")
    #         insert_order_item(cursor= cursor, order_id=order_id , product_id=product_id , unit_price=unit_price , quantity=quantity)
    #     con.commit()  
    #     return jsonify({"message": "Order created successfully","order_id":order_id, "status": 201 , "status_text" : "Created"}), 201 
    # except ValueError as ve:
    #     # json returned is invalid or empty
    #     if con : con.rollback()
    #     return jsonify( {"message": str(ve) , "status": 400 , "status_text":"Bad Request" } ), 400
    # except KeyError as ke:
    #     return jsonify( {"message": str(ke), "status": 400 , "status_text":"Bad Request"} ), 400
    # except Exception as e:
    #     return jsonify( {"message": str(e), "status": 500 , "status_text" : "Internal Server Error" } ), 500
    # finally:
    #     if cursor :cursor.close()
    #     if con :con.close()


if __name__ == "__main__":
    app.run(port=5001, debug=True)