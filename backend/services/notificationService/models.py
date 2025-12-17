from datetime import datetime
from database import db

class NotificationLog(db.Model):
    __tablename__='notification_log'

    # notification_id INT PRIMARY KEY AUTO_INCREMENT,
    notification_id = db.Column(db.Integer, primary_key = True, autoincrement = True)
    # order_id INT NOT NULL,
    order_id = db.Column(db.Integer, nullable = False)
    # customer_id INT NOT NULL,
    customer_id = db.Column(db.Integer, nullable = False)
    # notification_type VARCHAR(50),
    notification_type = db.Column(db.String(50))
    # message TEXT,
    message = db.Column(db.Text)
    # sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sent_at = db.Column(db.DateTime , default = datetime.now)

    def to_dict(self):
        return{
            "notification_id" : self.notification_id,
            "order_id" : self.order_id,
            "customer_id" : self.customer_id,
            "notification_type" : self.notification_type,
            "message" : self.message,
            "sent_at" : self.sent_at
        }
    
    # these tables are not in the responsability of this service and so are not handled here
    # FOREIGN KEY (order_id) REFERENCES orders(order_id),
    # FOREIGN KEY (customer_id) REFERENCES customers (customer_id)