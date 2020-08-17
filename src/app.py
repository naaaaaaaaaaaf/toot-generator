#!/usr/bin/env python3
from flask import Flask, request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/sample', methods=['POST'])
def sample_post():
    return "param1:{}".format(request.form['param1']) 