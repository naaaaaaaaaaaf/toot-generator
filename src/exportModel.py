#!/usr/bin/env python3
from os import access
import sys
import re
import pandas
import json
import MeCab
import markovify
import mastodonTools
mecabW = MeCab.Tagger("-d /usr/lib/mecab/dic/mecab-ipadic-neologd -O wakati")


def filterTweets(twts):
    replyMatch = re.compile(r"@\w+")
    urlMatch = re.compile(r"https?://")
    data = []
    for text in twts:
        if replyMatch.search(text) or urlMatch.search(text):
            continue
        data.append(text)
    return data


def loadTwitterCSV(filepath):
    data = pandas.read_csv(filepath)
    return "\n".join(filterTweets(data["text"]))


def loadTwitterJS(filepath):
    with open(filepath) as f:
        text = f.read()
    text = text[25:]
    data = json.loads(text)
    text = [s["tweet"]["full_text"] for s in data]
    return "\n".join(filterTweets(text))


def loadMastodonAPI(domain, access_token, account_id, params):
    toots = mastodonTools.fetchTootsLoop(domain, access_token, account_id, params, 100)
    #text = [s["text"] for s in tweets if "retweeted_status" not in s]
    return "\n".join(filterTweets(toots))


def generateAndExport(src, dest, state_size=3):
    src = src.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("?", "？").replace("!", "！").replace("，", "、").replace("．", "。").replace("。", "。\n")
    data = [mecabW.parse(s) for s in src.split("\n") if s != ""]
    joinedData = "".join(data)
    modeljson = markovify.NewlineText(joinedData, state_size=state_size).to_json()
    with open(dest, mode="w") as f:
        f.write(modeljson)
    return len(data)


if __name__ == "__main__":
    if len(sys.argv) > 3:
        learned = generateAndExport(loadTwitterJS(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    else:
        learned = generateAndExport(loadTwitterJS(sys.argv[1]), sys.argv[2])
    print("Exported " + str(learned) + " lines learned data to " + sys.argv[2] + ".")
