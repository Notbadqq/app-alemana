from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY']=os.environ["SECRET_KEY"] #Clave para ingresar al servidor
app.config['SQLALCHEMY_DATABASE_URI']=os.environ["ENGINE"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db=SQLAlchemy(app)

from flaskweb import routes