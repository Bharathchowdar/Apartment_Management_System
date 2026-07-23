from flask_sqlalchemy import SQLAlchemy
from datetime import date

db = SQLAlchemy()

class Unit(db.Model):
    __tablename__ = 'units'
    id = db.Column(db.Integer, primary_key=True)
    unit_number = db.Column(db.String(10), unique=True, nullable=False)
    floor = db.Column(db.Integer, nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    rent_amount = db.Column(db.Float, nullable=False)
    is_occupied = db.Column(db.Boolean, default=False)
    tenants = db.relationship('Tenant', backref='unit', lazy=True)

    def __repr__(self):
        return f"Unit({self.unit_number}, Floor {self.floor}, {'Occupied' if self.is_occupied else 'Vacant'})"


class Tenant(db.Model):
    __tablename__ = 'tenants'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=True)
    leases = db.relationship('Lease', backref='tenant', lazy=True)
    payments = db.relationship('Payment', backref='tenant', lazy=True)
    maintenance_requests = db.relationship('MaintenanceRequest', backref='tenant', lazy=True)

    def __repr__(self):
        return f"Tenant({self.name}, {self.email})"


class Lease(db.Model):
    __tablename__ = 'leases'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    monthly_rent = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='Active')  # Active, Expired, Terminated

    @property
    def is_expiring_soon(self):
        return (self.end_date - date.today()).days <= 30

    def __repr__(self):
        return f"Lease(Tenant {self.tenant_id}, {self.start_date} to {self.end_date}, {self.status})"


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_date = db.Column(db.Date, default=date.today)
    method = db.Column(db.String(50))  # Cash, UPI, Bank Transfer
    status = db.Column(db.String(20), default='Paid')  # Paid, Pending, Overdue

    def __repr__(self):
        return f"Payment(Tenant {self.tenant_id}, ₹{self.amount}, {self.payment_date})"


class MaintenanceRequest(db.Model):
    __tablename__ = 'maintenance_requests'
    id = db.Column(db.Integer, primary_key=True)
    tenant_id = db.Column(db.Integer, db.ForeignKey('tenants.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # Pending, In Progress, Resolved
    created_at = db.Column(db.Date, default=date.today)

    def __repr__(self):
        return f"MaintenanceRequest(Tenant {self.tenant_id}, {self.status})"
