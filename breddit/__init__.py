from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://b3322b067b460c:225bfff4@us-cdbr-east-04.cleardb.com/heroku_6ac55aa9e840c72'
app.config['SECRET_KEY'] = 'lIk9BYX296OU3UCl8isc'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from breddit import routes

