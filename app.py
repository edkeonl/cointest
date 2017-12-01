#!/usr/bin/env python

import urllib.request
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

    if req.get("result").get("action") == "coin_price":
        res = makeCoinQuery(req)
    elif req.get("result").get("action") == "coin_change":
        res = coinChangeQuery(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeCoinQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")

    baseurl = "https://api.coinmarketcap.com/v1/ticker/"
    coin_url = baseurl + coin_type
    
    coin_data = urllib.request.urlopen(coin_url).read()
    data = json.loads(coin_data)
    
    coin_name = str(data[0]['name'])
    coin_price = str(data[0]['price_usd'])
    
    speech = coin_name + " is currently " + coin_price + " US Dollars"
    
    if str(data[0]['symbol']) == 'BTC'
        temp_r = requests.get('https://api.coinone.co.kr/ticker/?currency=bch')
        coinone_value = requests.get(temp_r.url).json()
        coinone_price = coinone_value['last']
        speech = coin_name + " is currently $" + coin_price + ", Coinone price is " + coinone_price + "KRW"
    
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "coin_market_cap"
    }

    return res
    
def coinChangeQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    time_length = parameters.get("time_length")

    baseurl = "https://api.coinmarketcap.com/v1/ticker/"
    coin_url = baseurl + coin_type
    
    coin_data = urllib.request.urlopen(coin_url).read()
    data = json.loads(coin_data)
    
    coin_name = str(data[0]['name'])
    if time_length == "1 hour":
        coin_percent = str(data[0]['percent_change_1h'])
        speech = coin_name + " has changed " + coin_percent + " % in the last hour"
    elif time_length == "24 hours":
        coin_percent = str(data[0]['percent_change_24h'])
        speech = coin_name + " has changed " + coin_percent + " % in the last 24 hours"
    elif time_length == "7 days":
        coin_percent = str(data[0]['percent_change_7d'])
        speech = coin_name + " has changed " + coin_percent + " % in the last 7 days"
    
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "coin_market_cap"
    }

    return res

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    #print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')