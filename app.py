#!/usr/bin/env python

import urllib
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

    if req.get("result").get("action") != "coin_change":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    
    baseurl = "https://api.coinmarketcap.com/v1/ticker/"
    coin_url = baseurl + str(coin_type)
    
    result = urllib.urlopen(coin_url).read()
    data = json.loads(result)
    
    #coin_name = str(data[0]['name'])
    #coin_price = str(data[0]['price_usd'])

    #speech = coin_name + " is currently " + coin_price + " US dollars"
    #speech = "coin coin coin"

    print("Response:")
    print(speech)
    
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "apiai-slack-richformatting"
    }
    
    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeCoinQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    if coin_type is None:
        return None

    return coin_type

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    #print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')