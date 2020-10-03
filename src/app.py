#!/usr/bin/env python3
import os
import sys
import datetime
import markovify
from flask import Flask, request, redirect, url_for, abort, jsonify, render_template
import exportModel
import mastodonTools
import Form
import json

app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

@app.route('/',methods=["GET", "POST"])
def index():
    form = Form.GenForm()
    return render_template('index.html',form=form)

@app.route('/login',methods=["GET", "POST"])
def login_mastodon():
    form = Form.DomainForm()
    if request.method == 'POST' and form.validate_on_submit():
        global client_id, client_secret, domain
        domain = request.form['domain']
        filepath = os.path.join("./tokens", os.path.basename(domain.lower()) + ".json")
        if (os.path.isfile(filepath)):
            with open(filepath) as f:
                store = json.load(f)
                client_id, client_secret = store['client_id'], store['client_secret']
        else:
            try:
                client_id, client_secret = mastodonTools.get_client_id(domain)
                token_dic = {}
                token_dic['client_id'] = client_id
                token_dic['client_secret'] = client_secret
                with open(filepath, "w") as f:
                    json.dump(token_dic, f)                
            except Exception as e:
                Msg = "Mastodon認証に失敗しました。"
                return render_template('modelResult.html', message=Msg)
        return get_auth_url(domain,client_id)
    return render_template('login.html',form=form)


def get_auth_url(domain, client_id):
    try:
        url = mastodonTools.get_authorize_url(domain, client_id)
    except Exception as e:
        Msg = "Mastodon認証に失敗しました。"
        return render_template('getToken.html', message=Msg)
    return redirect(url)

@app.route('/redirect', methods=['GET'])
def callback():
    if "code" not in request.args:
        abort(400)
    try:
        access_token = mastodonTools.get_access_token(domain, client_id, client_secret, request.args['code'])
            # get account info
        account_info = mastodonTools.get_account_info(domain, access_token)
        params = {"exclude_replies": 1, "exclude_reblogs": 1}
        filename = "{}@{}".format(account_info["username"], domain)
        filepath = os.path.join("./chainfiles", os.path.basename(filename.lower()) + ".json")
        if (os.path.isfile(filepath) and datetime.datetime.now().timestamp() - os.path.getmtime(filepath) < 60 * 60 * 24):
            Msg = "モデルは24時間に1回生成が可能です。"
        else:
            exportModel.generateAndExport(exportModel.loadMastodonAPI(domain, access_token, account_info['id'], params), filepath)
            Msg = account_info["username"] + "さんの学習が完了しました。"
            print("LOG,GENMODEL," + str(datetime.datetime.now()) + "," + account_info["username"].lower())   # Log
        return render_template('modelResult.html', message=Msg) 
    except Exception as e:
        print(e)
        Msg = "処理に失敗しました。改善しない場合は管理者までご連絡をお願い致します。"
    return render_template('modelResult.html', message=Msg)

@app.route('/genText', methods=['POST','GET'])
def genText():
    form = Form.GenForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = request.form['username']
        instance = request.form['domain']

        if not os.path.isfile("./chainfiles/{}@{}.json".format(username, instance)):
            render_template('GenText.html', message='まずトゥートの学習をさせてね',form=form)
        try:
            with open("./chainfiles/{}@{}.json".format(username, instance)) as f:
                textModel = markovify.Text.from_json(f.read())
                sentence = textModel.make_sentence(tries=100)
                sentence = "".join(sentence.split())
            return render_template('GenText.html', result=sentence,form=form)
        except Exception as e:
            print(e)
            return render_template('GenText.html', message='something error happend', form=form)
    return render_template('GenText.html', form=form)
