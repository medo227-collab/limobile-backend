from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Account(db.Model):
    __tablename__ = 'accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    operator = db.Column(db.String(20), nullable=False)  # 'airtel', 'moov', 'zamani'
    balance = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'operator': self.operator,
            'balance': self.balance,
            'created_at': self.created_at.isoformat()
        }

class Transaction(db.Model):
    __tablename__ = 'transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=True)
    type = db.Column(db.String(20), nullable=False)  # 'transfer', 'forfait', 'deposit'
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Integer, nullable=False)
    operator = db.Column(db.String(20), nullable=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'type': self.type,
            'description': self.description,
            'amount': self.amount,
            'operator': self.operator,
            'date': self.date.isoformat()
        }
