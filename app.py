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
    elif req.get("result").get("action") == "coin_premium":
        res = coinPremiumQuery(req)

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
    
    #define coin market cap parameters 
    coin_name = str(data[0]['name'])
    coin_price = str(data[0]['price_usd'])
    coin_symbol = str(data[0]['symbol'])
    
    coinone_price_b_url = "https://api.coinone.co.kr/ticker/?currency="
    coinone_price_t_url = coinone_price_b_url + coin_symbol
    coinone_price_url = urllib.request.urlopen(coinone_price_t_url).read()
    
    #define coinone parameters 
    coinone_price_data = json.loads(coinone_price_url)
    coinone_price = str(coinone_price_data['last'])
    
    #coins listed in Coinone
    coinone_coins = ['BTC', 'BCH', 'ETH', 'ETC', 'XRP', 'QTUM', 'IOTA', 'LTC']
    if coin_symbol in coinone_coins:
        speech = coin_name + " is currently $" + coin_price + " Coinone is currently ₩" + coinone_price
    else:
        speech = coin_name + " is currently " + coin_price + " US Dollars"
    
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

def coinPremiumQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    
    coin_data = urllib.request.urlopen(coin_url).read()
    data = json.loads(coin_data)
    
    #define coin market cap parameters 
    coin_name = str(data[0]['name'])
    coin_symbol = str(data[0]['symbol'])
    
    bitfinex_b_url = "https://api.bitfinex.com/v1/pubticker/"
    bitfinex_price_t_url = bitfinex_b_url + coin_symbol + "usd"
    bitfinex_price_url = urllib.request.urlopen(bitfinex_price_t_url).read()
    
    #define coinone parameters 
    bitfinex_price_data = json.loads(bitfinex_price_url)
    bitfinex_price = bitfinex_price_data['last_price']
    
    #convert bitfinex price from USD to KRW
    # 1 USD = 1,082.48 KRW
    convert_USDtoKRW = 1082.48
    bitfinex_price_KRW = float(bitfinex_price)*convert_USDtoKRW
    
    coinone_price_b_url = "https://api.coinone.co.kr/ticker/?currency="
    coinone_price_t_url = coinone_price_b_url + coin_symbol
    coinone_price_url = urllib.request.urlopen(coinone_price_t_url).read()
    
    #define coinone parameters 
    coinone_price_data = json.loads(coinone_price_url)
    coinone_price = float(coinone_price_data['last'])
    
    coin_premium = bitfinex_price_KRW / coinone_price
    
    speech = "Premium for " + coin_name + "is " + str(coin_premium)
    
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