from flask import *
from forms import RegistrationForm, LoginForm
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from helper_functions import salt_password
from flask_bcrypt import Bcrypt
from config import developmentconfig

app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b3322b067b460c:225bfff4@us-cdbr-east-04.cleardb.com/heroku_6ac55aa9e840c72'
app.config.from_object(developmentconfig)

app.config['SECRET_KEY'] = 'lIk9BYX296OU3UCl8isc'

SQLALCHEMY_TRACK_MODIFICATIONS = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class user(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    image_file = db.Column(db.string(20), nullable=False, default='default.jpg')
    posts = db.relationship('Post', backref='author', lazy=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)

@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)



if __name__ == '__main__':
    app.run(debug=True)