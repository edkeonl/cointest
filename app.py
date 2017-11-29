#!/usr/bin/env python

#import urllib
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

    res = makeCoinQuery(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeCoinQuery(req):
    if req.get("result").get("action") != "coin_change":
        return {}
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")

    baseurl = "https://api.coinmarketcap.com/v1/ticker/"
    coin_url = baseurl + coin_type
    
    #coin_data = urllib.urlopen(coin_url).read()
    #data = json.loads(coin_data)
    
    #coin_name = str(data[0]['name'])
    #coin_price = str(data[0]['price_usd'])
    
    #speech = coin_name + " is currently " + coin_price + " US dollars"
    speech = "coin coin coin"
    
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