from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired, NumberRange
import secrets
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '93706c9e3f77354f88ad49691ed40ba39577805ba18482498309142b4bc67856'
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.abspath("/app/reservations.db")}'
db = SQLAlchemy(app)

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
        admin = Admin.query.filter_by(username = form.username.data).first()
        if admin and admin.password == form.password.data:  # could include password hashing
            return redirect(url_for('admin_dashboard'))
        else:
            error = "Invalid credentials"
    return render_template('admin_login.html', form=form, error=error)

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
            db.session.commit()
            reservation = new_reservation
            
            # return render_template('confirm_reservation.html', reservation=new_reservation)
    return render_template('reserve.html', form=form, error=error, reservation=reservation)
    
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001, host='0.0.0.0')