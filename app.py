from flask import Flask, render_template, request, redirect, url_for, flash
from database import db, Tenant, Unit, Lease, Payment, MaintenanceRequest
from datetime import date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/apartment_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

db.init_app(app)

# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.route('/')
def dashboard():
    total_units = Unit.query.count()
    occupied = Unit.query.filter_by(is_occupied=True).count()
    total_tenants = Tenant.query.count()
    pending_maintenance = MaintenanceRequest.query.filter_by(status='Pending').count()
    recent_payments = Payment.query.order_by(Payment.payment_date.desc()).limit(5).all()
    return render_template('dashboard.html',
        total_units=total_units, occupied=occupied,
        total_tenants=total_tenants, pending_maintenance=pending_maintenance,
        recent_payments=recent_payments)

# ─── Tenants ──────────────────────────────────────────────────────────────────

@app.route('/tenants')
def tenants():
    all_tenants = Tenant.query.all()
    return render_template('tenants.html', tenants=all_tenants)

@app.route('/tenants/add', methods=['GET', 'POST'])
def add_tenant():
    units = Unit.query.filter_by(is_occupied=False).all()
    if request.method == 'POST':
        tenant = Tenant(
            name=request.form['name'],
            email=request.form['email'],
            phone=request.form['phone'],
            unit_id=request.form['unit_id']
        )
        unit = Unit.query.get(request.form['unit_id'])
        if unit:
            unit.is_occupied = True
        db.session.add(tenant)
        db.session.commit()
        flash('Tenant added successfully!', 'success')
        return redirect(url_for('tenants'))
    return render_template('add_tenant.html', units=units)

@app.route('/tenants/delete/<int:id>')
def delete_tenant(id):
    tenant = Tenant.query.get_or_404(id)
    if tenant.unit:
        tenant.unit.is_occupied = False
    db.session.delete(tenant)
    db.session.commit()
    flash('Tenant removed.', 'info')
    return redirect(url_for('tenants'))

# ─── Units ────────────────────────────────────────────────────────────────────

@app.route('/units')
def units():
    all_units = Unit.query.all()
    return render_template('units.html', units=all_units)

@app.route('/units/add', methods=['GET', 'POST'])
def add_unit():
    if request.method == 'POST':
        unit = Unit(
            unit_number=request.form['unit_number'],
            floor=request.form['floor'],
            bedrooms=request.form['bedrooms'],
            rent_amount=request.form['rent_amount']
        )
        db.session.add(unit)
        db.session.commit()
        flash('Unit added!', 'success')
        return redirect(url_for('units'))
    return render_template('add_unit.html')

# ─── Leases ───────────────────────────────────────────────────────────────────

@app.route('/leases')
def leases():
    all_leases = Lease.query.all()
    return render_template('leases.html', leases=all_leases)

@app.route('/leases/add', methods=['GET', 'POST'])
def add_lease():
    tenants = Tenant.query.all()
    if request.method == 'POST':
        lease = Lease(
            tenant_id=request.form['tenant_id'],
            start_date=request.form['start_date'],
            end_date=request.form['end_date'],
            monthly_rent=request.form['monthly_rent'],
            status='Active'
        )
        db.session.add(lease)
        db.session.commit()
        flash('Lease created!', 'success')
        return redirect(url_for('leases'))
    return render_template('add_lease.html', tenants=tenants)

# ─── Payments ─────────────────────────────────────────────────────────────────

@app.route('/payments')
def payments():
    all_payments = Payment.query.order_by(Payment.payment_date.desc()).all()
    return render_template('payments.html', payments=all_payments)

@app.route('/payments/add', methods=['GET', 'POST'])
def add_payment():
    tenants = Tenant.query.all()
    if request.method == 'POST':
        payment = Payment(
            tenant_id=request.form['tenant_id'],
            amount=request.form['amount'],
            payment_date=date.today(),
            method=request.form['method'],
            status='Paid'
        )
        db.session.add(payment)
        db.session.commit()
        flash('Payment recorded!', 'success')
        return redirect(url_for('payments'))
    return render_template('add_payment.html', tenants=tenants)

# ─── Maintenance ──────────────────────────────────────────────────────────────

@app.route('/maintenance')
def maintenance():
    requests = MaintenanceRequest.query.order_by(MaintenanceRequest.created_at.desc()).all()
    return render_template('maintenance.html', requests=requests)

@app.route('/maintenance/add', methods=['GET', 'POST'])
def add_maintenance():
    tenants = Tenant.query.all()
    if request.method == 'POST':
        req = MaintenanceRequest(
            tenant_id=request.form['tenant_id'],
            description=request.form['description'],
            status='Pending',
            created_at=date.today()
        )
        db.session.add(req)
        db.session.commit()
        flash('Maintenance request submitted!', 'success')
        return redirect(url_for('maintenance'))
    return render_template('add_maintenance.html', tenants=tenants)

@app.route('/maintenance/update/<int:id>/<status>')
def update_maintenance(id, status):
    req = MaintenanceRequest.query.get_or_404(id)
    req.status = status
    db.session.commit()
    flash(f'Status updated to {status}.', 'success')
    return redirect(url_for('maintenance'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
