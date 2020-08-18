#!/usr/bin/env python3
from flask import Flask, request, render_template
app = Flask(__name__)

@app.route('/')
def hello_world():
    return render_template('index.html')

@app.route('/redirect', methods=['POST'])
def sample_post():
    #urlチェック
    return "param1:{}".format(request.form['domain']) 