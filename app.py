#!/usr/bin/env python

import requests
import urllib.request, urllib.parse, urllib.error
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
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "coin_change":
        return {}
        
    baseurl = "https://api.coinmarketcap.com/v1/ticker/"
    yql_query = makeCoinQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + yql_query + "/"
    print(yql_url)
    
    r = requests.get(yql_url)

    curr_price = requests.get(r.url).json()
    percent = curr_price[0]['percent_change_24h']

    print("yql result: ")
    print(result)

    speech = "hey i am a coin"
    #speech = coin_type + "changed" + percent + "% within the last 24 hours"

    print("Response:")
    print(speech)
    
    #result = req.get("result")
    #parameters = result.get("parameters")
    #zone = parameters.get("shipping-zone")

    #cost = {'Europe':100, 'North America':200, 'South America':300, 'Asia':400, 'Africa':500}

    #speech = "The cost of shipping to " + zone + " is " + str(cost[zone]) + " euros."

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {},
        # "contextOut": [],
        "source": "api-coinmarketcap"
    }
    
    return res


def makeCoinQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    if coin_type is None:
        return None

    return coin_type

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')
