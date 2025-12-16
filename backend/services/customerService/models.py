from database import db
from datetime import datetime

class Customer(db.Model):
    __tablename__="Customers"
    
    customer_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    loyalty_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    
    def to_dict(self):
        return{
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "loyalty_points": self.loyalty_points,
            "created_at": self.created_at
        }