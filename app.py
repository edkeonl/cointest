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
    
    baseurl = "https://api.coinmarketcap.com/v1/ticker/"
    
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    
    coin_url = baseurl + coin_type
    
    #b = requests.get(coin_url)
    #curr_price = requests.get(b.url).json()
    #percent = curr_price[0]['percent_change_24h']
    
    speech = coin_type + "changed 24% within the last 24 hours"" 
    #+ percent + "% within the last 24 hours"

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

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    #print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')