#!/usr/bin/env python3
from flask import Flask, request, render_template
import requests
from urllib.parse import urlencode

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
    client_id, client_secret = get_client_id(domain)
    url = get_authorize_url(domain, client_id)
    return render_template('getToken.html', url=url)
    # return "param1:{}".format(url)


@app.route('/auth', methods=['POST'])
def get_auth():
    code = request.form['code']
    access_token = get_access_token(domain, client_id, client_secret, code)
    return access_token


def get_client_id(domain):
    """
    認証済みアプリのためのclient_id, client_secretの発行
    :return: (client_id, client_secret)
    """

    # すでに作成ずみで保存してあればそれを利用
    # if os.path.exists(STORE_FILE_NAME):
    #    with open(STORE_FILE_NAME) as f:
    #        store = json.load(f)
    #        return store["client_id"], store["client_secret"]

    # 未作成であれば新規に発行
    request_uri = 'https://' + domain + '/api/v1/apps'
    res = requests.post(request_uri,
                        dict(client_name="Toot Generator",
                             redirect_uris="urn:ietf:wg:oauth:2.0:oob",
                             scopes="read")).json()

    # ファイルに保存
    # with open(STORE_FILE_NAME, "w") as f:
    #    json.dump(res, f)
    return res["client_id"], res["client_secret"]


def get_authorize_url(domain, client_id):
    """
    認証済みアプリに権限を与えるための承認ページのURLを作成する
    :param domain:
    :param client_id:
    :return: url
    """
    params = urlencode(dict(
        client_id=client_id,
        response_type="code",
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",   # ブラウザ上にcode表示
        scope="read"
    ))

    return 'https://' + domain + '/oauth/authorize?' + params


def get_access_token(domain, client_id, client_secret, code):
    """
    client_idと認証コードを利用してアクセストークンを取得する
    :param domain:
    :param client_id:
    :param client_secret:
    :param code: ブラウザに表示された認証コード
    :return: access_token
    """
    res = requests.post('https://' + domain + '/oauth/token', dict(
        grant_type="authorization_code",
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
        client_id=client_id,
        client_secret=client_secret,
        code=code
    )).json()

    return res["access_token"]
