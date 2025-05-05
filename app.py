from flask import Flask, render_template, request, redirect, url_for, flash, get_flashed_messages
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import secrets
import os
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.exceptions import abort

app = Flask(__name__)
app.config['SECRET_KEY'] = '93706c9e3f77354f88ad49691ed40ba39577805ba18482498309142b4bc67856'
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.abspath('/app/reservations.db')}"
db = SQLAlchemy(app)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key=True)
    passengerName = db.Column(db.String(160), nullable=False)
    seatRow = db.Column(db.Integer, nullable=False)
    seatColumn = db.Column(db.Integer, nullable=False)
    eTicketNumber = db.Column(db.String(120), unique=True, nullable=False)
    created = db.Column(db.TIMESTAMP, server_default=db.func.now())

class Admin(db.Model):
    __tablename__ = 'admins'
    username = db.Column(db.String, primary_key=True)
    password = db.Column(db.String, nullable=False)

class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = StringField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ReservationForm(FlaskForm):
    passenger_name = StringField('Passenger Name', validators=[DataRequired()])
    seat_row = IntegerField('Row (1-12)', validators=[DataRequired(), NumberRange(min=1, max=12)])
    seat_col = IntegerField('Column (1-4)', validators=[DataRequired(), NumberRange(min=1, max=4)])
    submit = SubmitField('Reserve Seat')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    error = None
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin and admin.password == form.password.data:
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid username and/or password."
    return render_template('admin_login.html', form=form, error=error)

@app.route('/admin_dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if request.method == 'POST':
        eTicketNumber = request.form.get('eTicketNumber')
        if eTicketNumber:
            res = Reservation.query.filter_by(eTicketNumber=eTicketNumber).first()
            if res:
                db.session.delete(res)
                try:
                    db.session.commit()
                except SQLAlchemyError:
                    db.session.rollback()
    reservations = Reservation.query.all()
    seating_chart_data = get_seating_chart_data(reservations)
    total_sales = get_total_cost(reservations)
    return render_template('admin_dashboard.html',
                           reservations=reservations,
                           seating_chart_data=seating_chart_data,
                           total_sales=total_sales)

def get_seating_chart_data(reservations):
    chart = [['_' for _ in range(4)] for _ in range(12)]
    for r in reservations:
        ri = r.seatRow - 1
        ci = r.seatColumn - 1
        if 0 <= ri < 12 and 0 <= ci < 4:
            chart[ri][ci] = 'X'
    return chart

def get_cost_matrix():
    return [[100, 75, 50, 100] for _ in range(12)]

def get_total_cost(reservations):
    total = 0
    cost_matrix = get_cost_matrix()
    for r in reservations:
        ri = r.seatRow - 1
        ci = r.seatColumn - 1
        if 0 <= ri < 12 and 0 <= ci < 4:
            total += cost_matrix[ri][ci]
    return total

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    form = ReservationForm()
    error = None
    reservation = None
    if form.validate_on_submit():
        name = form.passenger_name.data
        row = form.seat_row.data
        col = form.seat_col.data
        if Reservation.query.filter_by(seatRow=row, seatColumn=col).first():
            error = 'This seat is already reserved.'
        else:
            ticket = secrets.token_hex(8)
            new = Reservation(passengerName=name,
                              seatRow=row,
                              seatColumn=col,
                              eTicketNumber=ticket)
            db.session.add(new)
            try:
                db.session.commit()
                reservation = new
            except SQLAlchemyError as e:
                db.session.rollback()
                error = f"Database error: {e}"
    return render_template('reserve.html', form=form, error=error, reservation=reservation)

@app.route('/edit/<int:reservation_id>', methods=['GET', 'POST'])
def edit_reservation(reservation_id):
    reservation = Reservation.query.get_or_404(reservation_id)
    form = ReservationForm(
        passenger_name=reservation.passengerName,
        seat_row=reservation.seatRow,
        seat_col=reservation.seatColumn
    )
    if form.validate_on_submit():
        reservation.passengerName = form.passenger_name.data
        reservation.seatRow = form.seat_row.data
        reservation.seatColumn = form.seat_col.data
        try:
            db.session.commit()
            return redirect(url_for('admin_dashboard'))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f"Could not update reservation: {e}", 'danger')
    return render_template('edit_reservation.html', form=form, reservation=reservation)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001, host='0.0.0.0')