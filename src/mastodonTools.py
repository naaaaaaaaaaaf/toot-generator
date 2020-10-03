#!/usr/bin/env python3
import json
import re
from os import access
import requests
from urllib.parse import urlencode

redirect_uri = ''
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
                             redirect_uris=redirect_uri,
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
        redirect_uri=redirect_uri,   # ブラウザ上にcode表示
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
        redirect_uri=redirect_uri,
        client_id=client_id,
        client_secret=client_secret,
        code=code
    )).json()

    return res["access_token"]


def get_account_info(domain, access_token):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    res = requests.get('https://' + domain + '/api/v1/accounts/verify_credentials', headers=headers).json()
    return res


def fetchToots(domain, access_token, account_id, params):
    headers = {'Authorization': 'Bearer {}'.format(access_token)}
    url = "https://{}/api/v1/accounts/{}/statuses".format(domain, account_id)
    req = requests.get(url, headers=headers, json=params).json()
    return req


def fetchTootsLoop(domain, access_token, account_id, params, loop):
    toots = []
    for i in range(loop):
        req = fetchToots(domain, access_token, account_id, params)
        for x in req:
            #print(x['content'])
            seikei = re.compile(r"<[^>]*?>").sub("",  x['content'])
            toots.append(seikei)
            last_id = x['id']
        params["max_id"] = last_id
    return toots
