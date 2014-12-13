from flask import Flask

#create the application
app = Flask(__name__)

#import views
from app import views