from flask import Flask
from flask_restful import Resource, Api
import requests
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home()
    r = requests.get()