# import logging
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import secrets
import os
from sqlalchemy.exc import SQLAlchemyError

app = Flask(__name__)
app.config['SECRET_KEY'] = '93706c9e3f77354f88ad49691ed40ba39577805ba18482498309142b4bc67856'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath("/app/reservations.db")}'
db = SQLAlchemy(app)
# logging.basicConfig(level=logging.DEBUG)

class Reservation(db.Model):
    __tablename__ = 'reservations'
    id = db.Column(db.Integer, primary_key = True)
    passengerName = db.Column(db.String(160), nullable = False)
    seatRow = db.Column(db.Integer, nullable = False)
    seatColumn = db.Column(db.Integer, nullable = False)
    eTicketNumber = db.Column(db.String(120), unique = True, nullable = False)
    created = db.Column(db.TIMESTAMP, server_default = db.func.now())

    def __repr__(self):
        return f"<Reservation {self.eTicketNumber}>"
    
class Admin(db.Model):
    __tablename__ = 'admins'
    # admin1 = 12345
    # admin2 = 24680
    # admin3 = 98765
    username = db.Column(db.String, primary_key = True)
    password = db.Column(db.String, nullable = False)

    def __repr__(self):
        return f"<Admin {self.username}"
    
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators = [DataRequired()])
    password = StringField('Password', validators = [DataRequired()])
    submit = SubmitField('Login')

class ReservationForm(FlaskForm):
    passenger_name = StringField('Passenger Name', validators = [DataRequired()])
    seat_row = IntegerField('Row (1-12)', validators = [DataRequired(), NumberRange(min = 1, max = 12)])
    seat_col = IntegerField('Column (1-4)', validators = [DataRequired(), NumberRange(min = 1, max = 4)])
    submit = SubmitField('Reserve Seat')

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()
    error = None
    if form.validate_on_submit():
        admins = Admin.query.filter_by(username = form.username.data).first()
        if admins and admins.password == form.password.data: 
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Incorrect username and/or password."
    return render_template('admin_login.html', form=form, error=error)

@app.route('/admin_dashboard')
def admin_dashboard():
    reservations = Reservation.query.all()
    seating_chart_data = get_seating_chart_data(reservations)
    # total_sales = db.session.query(db.func.sum(Reservation.price)).scalar() or 0
    # return render_template('admin_dashboard.html', reservations=reservations, total_sales=total_sales, cost_matrix=cost_matrix)
    return render_template('admin_dashboard.html', reservations=reservations, seating_chart_data=seating_chart_data)

def get_seating_chart_data(reservations):
    seating_chart = [['_' for _ in range(4)] for _ in range(12)]

    for res in reservations:
        row_index = res.seatRow - 1
        col_index = res.seatColumn - 1
        if 0 <= row_index < 12 and 0 <= col_index < 4:
            seating_chart[row_index][col_index] = 'X'
    return seating_chart

@app.route('/reserve', methods=['GET', 'POST'])
def reserve():
    form = ReservationForm()
    error = None
    reservation = None
    if form.validate_on_submit():
        passenger_name = form.passenger_name.data
        row = form.seat_row.data
        col = form.seat_col.data
        existing_reservation = Reservation.query.filter_by(seatRow=row, seatColumn=col).first()

        if existing_reservation:
            error = 'This seat is already reserved.'
        else:
            
            e_ticket_number = secrets.token_hex(8)      # couldn't figure out the method in the video demo so I did this
            new_reservation = Reservation(
                passengerName = passenger_name,
                seatRow = row,
                seatColumn = col,
                eTicketNumber = e_ticket_number
            )
            db.session.add(new_reservation)
            try:
                db.session.commit()
                reservation = new_reservation
            except SQLAlchemyError as e:
                db.session.rollback()
                error = f"Database error: {e}"
                app.logger.error(f"Error savinf reservation: {e}")
                reservation = None
            
            # return render_template('confirm_reservation.html', reservation=new_reservation)
    return render_template('reserve.html', form=form, error=error, reservation=reservation)
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001, host='0.0.0.0')