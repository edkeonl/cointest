#!/usr/bin/env python

import requests
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import time
from datetime import date

import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = processRequest(req)

    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "coin_change":
        return {}
    baseurl = "https://api.coinmarketcap.com/v1/ticker/"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + coin_type + "/"
    print(yql_url)

    curr_price = requests.get(yql_url.url).json()
    result = curr_price[0]['percent_change_24h']
    #result = urllib.urlopen(yql_url).read()
    print("yql result: ")
    print(result)

    #data = json.loads(result)
    #res = makeWebhookResult(data)
    #return res
    return result


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    if coin_type is None:
        return None

    return coin_type

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
