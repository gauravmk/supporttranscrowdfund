from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_bootstrap import Bootstrap
from wtforms import StringField, IntegerField, SubmitField, RadioField
from wtforms.validators import DataRequired, ValidationError
from send import send_welcome_text, send_update_text
import abcd
import threading
import phonenumbers
import sqlalchemy
import enum
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['DEBUG'] = os.environ.get('DEBUG', True)
app.config['SECRET_KEY'] = 'yolo'
Bootstrap(app)
db = SQLAlchemy(app)


def normalize_phone(number):
    return phonenumbers.format_number(phonenumbers.parse(
        number, 'US'), phonenumbers.PhoneNumberFormat.E164)

# Models


class Frequency(enum.Enum):
    Daily = 0
    EveryOtherDay = 1
    Weekly = 2


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String())
    # daily, every_other_day, weekly
    frequency = db.Column(sqlalchemy.Enum(Frequency))
    # Default/prefilled donation amount
    amount = db.Column(db.Integer)

# Forms


def validate_phone_number(form, field):
    try:
        if len(normalize_phone(field.data)) != 12:
            raise ValidationError('Not valid US phone number')
    except Exception as e:
        raise ValidationError('Not valid US phone number')


class Signup(FlaskForm):
    phone_number = StringField(
        'Phone Number', validators=[
            DataRequired(), validate_phone_number])
    frequency = RadioField(
        'Frequency',
        coerce=int,
        choices=[
            (Frequency.Daily.value,
             'Daily'),
            (Frequency.EveryOtherDay.value,
             'MWF'),
            (Frequency.Weekly.value,
             'Weekly')])
    amount = IntegerField('Amount')
    submit = SubmitField('Submit')


@app.route("/", methods=['GET', 'POST'])
def index():
    form = Signup()
    if form.validate_on_submit():
        phone = normalize_phone(form.phone_number.data),
        existing = User.query.filter(User.phone_number == phone).first()
        if existing:
            existing.frequency = Frequency(form.frequency.data)
            existing.amount = form.amount.data
            threading.Thread(target=send_update_text, args=(existing,)).start()
            return "Your account has been updated!"
        else:
            user = User(
                phone_number=phone,
                frequency=Frequency(form.frequency.data),
                amount=form.amount.data,
            )
            db.session.add(user)
            db.session.commit()
            threading.Thread(target=send_welcome_text, args=(user,)).start()
            return "You've been added! You should get a text right away. If you didn't, you may have entered your phone number incorrectly"
    else:
        return render_template('index.html', form=form)


if __name__ == '__main__':
    app.run()
