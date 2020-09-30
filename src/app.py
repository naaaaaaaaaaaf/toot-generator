#!/usr/bin/env python3
import os
import sys
import datetime
import markovify
from flask import Flask, request, redirect, abort, jsonify, render_template
import MeCab
import exportModel
import mastodonTools
import json

app = Flask(__name__)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/redirect', methods=['POST'])
def get_auth_url():
    # todo ドメインチェック
    # インスタンスにAPP登録
    global client_id, client_secret, domain
    domain = request.form['domain']
    filepath = os.path.join("./tokens", os.path.basename(domain.lower()) + ".json")
    if (os.path.isfile(filepath)):
        with open(filepath) as f:
            store = json.load(f)
            client_id, client_secret = store['client_id'], store['client_secret']
    else:
        client_id, client_secret = mastodonTools.get_client_id(domain)
        token_dic = {}
        token_dic['client_id'] = client_id
        token_dic['client_secret'] = client_secret
        with open(filepath, "w") as f:
            json.dump(token_dic, f)

    url = mastodonTools.get_authorize_url(domain, client_id)
    return render_template('getToken.html', url=url)


@app.route('/auth', methods=['POST'])
def get_auth():
    code = request.form['code']
    try:
        access_token = mastodonTools.get_access_token(domain, client_id, client_secret, code)
        # get account info
        account_info = mastodonTools.get_account_info(domain, access_token)
        params = {"exclude_replies": 1, "exclude_reblogs": 1}
        filename = "{}@{}".format(account_info["username"], domain)
        filepath = os.path.join("./chainfiles", os.path.basename(filename.lower()) + ".json")
        if (os.path.isfile(filepath) and datetime.datetime.now().timestamp() - os.path.getmtime(filepath) < 60 * 60 * 24):
            Msg = "You can generate Markov chain only once per 24 hours."
        else:
            exportModel.generateAndExport(exportModel.loadMastodonAPI(domain, access_token, account_info['id'], params), filepath)
            Msg = account_info["username"] + "'s Markov chain model was successfully GENERATED!"
            print("LOG,GENMODEL," + str(datetime.datetime.now()) + "," + account_info["username"].lower())   # Log
    except Exception as e:
        print(e)
        Msg = "Failed to generate your Markov chain. Please retry a few minutes later."

    return render_template('modelResult.html', message=Msg)
    # if successMsg:
    #    return redirect("https://markov.cordx.net/" + account_info["screen_name"] + "?success=" + urllib.parse.quote(successMsg))
    # else:
    #    return redirect("https://markov.cordx.net/?error=" + urllib.parse.quote(errMsg))
