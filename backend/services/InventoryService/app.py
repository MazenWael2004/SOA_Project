from flask import Flask, jsonify,request
from models import Inventory
from config import Config
from database import db
from flask_migrate import Migrate

load_dotenv('../../.env')

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
Migrate(app, db)




@app.route("/api/inventory/check/<product_id>",methods=['GET'])
def check_product_avail(product_id):
    product = Inventory.query.get_or_404(product_id)
    if product:
        return jsonify(product.to_dict())
    return jsonify({"error":"Product not found"}),404


    

@app.route("/api/inventory/update",methods=['PUT'])
def update_inventory():
    data =request.get_json()
    product_id = data.get('product_id')
    qty = data.get('quantity')
    
    if qty<=0:
        return jsonify({"error":"please enter a valid quantity"}),400
    
    product= Inventory.query.get(product_id)
    if not product:
        return jsonify({"error","this isn't a valid product"}),400
    if qty> product.quantity_available:
        return jsonify({"error":"the quantity available is sufficent"}),400
    
    product.quantity_available -= qty
    db.session.commit()
    return jsonify({"Success":"Stock updated"}),200

@app.route('/api/inventory', methods=['GET'])
def get_all():
    products = Inventory.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/inventory/seed', methods=['POST'])
def seed_inventory():
    """Populates the database with initial data from the assignment PDF."""
    
    # 1. Check if data already exists
    if Inventory.query.first():
        return jsonify({"message": "Database already contains data. Seed skipped."}), 200

    # [cite_start]2. Define the sample data [cite: 221-227]
    sample_products = [
        Inventory(product_name="Laptop", quantity_available=50, unit_price=999.99),
        Inventory(product_name="Mouse", quantity_available=200, unit_price=29.99),
        Inventory(product_name="Keyboard", quantity_available=150, unit_price=79.99),
        Inventory(product_name="Monitor", quantity_available=75, unit_price=299.99),
        Inventory(product_name="Headphones", quantity_available=100, unit_price=149.99)
    ]

    # 3. Insert into Database
    try:
        db.session.add_all(sample_products)
        db.session.commit()
        return jsonify({
            "message": "Inventory seeded successfully!",
            "products_added": len(sample_products)
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
if __name__ == "__main__":
    app.run(port=5002, debug=True)