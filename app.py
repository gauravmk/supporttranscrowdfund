from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField
from wtforms.validators import DataRequired
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['DEBUG'] = os.environ.get('DEBUG', True)
app.config['SECRET_KEY'] = 'yolo'
db = SQLAlchemy(app)

# Models
class User(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  phone_number = db.Column(db.String())
  # "Notify every <frequency> days"
  frequency = db.Column(db.Integer)
  # Default/prefilled donation amount
  amount = db.Column(db.Integer)

# Forms
class Signup(FlaskForm):
  phone_number = StringField('phone_number', validators=[DataRequired()])
  frequency = IntegerField('frequency', validators=[DataRequired()])
  amount = IntegerField('amount', validators=[DataRequired()])
  submit = SubmitField('Submit')

@app.route("/")
def index():
    return render_template('index.html', form=Signup())

if __name__ == '__main__':
    app.run()

