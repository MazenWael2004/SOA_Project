from database import db
from datetime import datetime
class Inventory(db.Model):
    __tablename__='inventory'
    
    product_id = db.Column(db.Integer,primary_key=True,autoincrement=True)
    product_name =db.Column(db.String(100),nullable=False)
    quantity_available = db.Column(db.Integer,nullable=False)
    unit_price=  db.Column(db.Numeric(10,2),nullable=False)
    last_updated=db.Column(db.DateTime,default=datetime.now,onupdate=datetime.now)
    def to_dict(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "quantity_available": self.quantity_available,
            "unit_price": float(self.unit_price),
            "last_updated": self.last_updated
        }