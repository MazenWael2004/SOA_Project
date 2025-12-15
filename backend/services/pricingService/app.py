import mysql.connector
from flask import Flask,request, jsonify
import _json
from models import PricingRule,TaxRate
from database import db
from config import Config
from flask_migrate import Migrate
import requests


load_dotenv('../../.env')

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app, db)
INVENTORY_SERVICE_URL = "http://localhost:5002/api/inventory/check"

@app.route('/api/pricing/calculate', methods=['POST'])
def calculate_price():
    #get data from orders service
    data= request.get_json()
    products_needed = data.get('products',[])
    total_amount=0
    for product in products_needed:
        product_id = product.get('product_id')
        qty = product.get('quantity') 
        #check if product exists and get price
        response = requests.get(f"{INVENTORY_SERVICE_URL}/{product_id}")
        if response.status_code !=200:
            return jsonify({"error":"that product doesnt exist"})
        product_data= response.json()
        unit_price = product_data['unit_price']
    
        #check if there is a discount rule
        rule = PricingRule.query.filter(
                PricingRule.product_id == product_id, 
                PricingRule.min_quantity <= qty
            ).order_by(PricingRule.min_quantity.desc()).first()
        discount=0.0
        if rule:
            discount = rule.discount_precentage
        
        product_total = unit_price*qty -((unit_price*qty)*(discount/100))
        total_amount+=product_total

    return jsonify({"total_price":f"{total_amount}"})
    
@app.route('/api/pricing/seed', methods=['POST'])
def seed_data():
    if not PricingRule.query.first():
        # Add a rule: Buy 5 or more of Product 1, get 10% off [cite: 235]
        rule1 = PricingRule(product_id=1, min_quantity=5, discount_percentage=10.00)
        # Add a rule: Buy 10 or more of Product 2, get 15% off [cite: 236]
        rule2 = PricingRule(product_id=2, min_quantity=10, discount_percentage=15.00)
        
        db.session.add_all([rule1, rule2])
        db.session.commit()
        return jsonify({"message": "Pricing rules seeded!"})
    return jsonify({"message": "Rules already exist"})



if __name__ == "__main__":
    app.run(debug=True,port=5003)


