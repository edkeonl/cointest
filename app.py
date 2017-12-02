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
    
    cmc = coinmarketcapParameters(coin_type)

    #define coin market cap parameters 
    coin_name = str(cmc['name'])
    coin_price = str(cmc['price_usd'])
    coin_symbol = str(cmc['symbol'])
    
    co = coinoneParameters(coin_symbol)
    coinone_price = str(co['last'])
    
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

    cmc = coinmarketcapParameters(coin_type)
    
    coin_name = str(cmc['name'])
    if time_length == "1 hour":
        coin_percent = str(cmc['percent_change_1h'])
        speech = coin_name + " has changed " + coin_percent + " % in the last hour"
    elif time_length == "24 hours":
        coin_percent = str(cmc['percent_change_24h'])
        speech = coin_name + " has changed " + coin_percent + " % in the last 24 hours"
    elif time_length == "7 days":
        coin_percent = str(cmc['percent_change_7d'])
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
    
    cmc = coinmarketcapParameters(coin_type)
    
    #define coin market cap parameters 
    coin_name = str(cmc['name'])
    coin_symbol = str(cmc['symbol'])
    
    bf = bitfinexParameters(coin_symbol)
    bitfinex_price = bf['last_price']
    
    #convert bitfinex price from USD to KRW

    bitfinex_price_KRW = CurrencyConverter(float(bitfinex_price), 'USDtoKRW')
    
    co = coinoneParameters(coin_symbol)
    coinone_price = float(co['last'])
    
    coin_premium = ((coinone_price / bitfinex_price_KRW) - 1.00)*100
    coin_premium = str(round(coin_premium, 2))
    
    speech = "Premium for " + coin_name + " is " + coin_premium + "%"
    
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "coin_market_cap"
    }

    return res

def coinmarketcapParameters(type):
    coinmarketcap_b_url = "https://api.coinmarketcap.com/v1/ticker/"
    coinmarketcap_t_url = coinmarketcap_b_url + type
    coinmarketcap_t_data = urllib.request.urlopen(coinmarketcap_t_url).read()
    coinmarketcap_data = json.loads(coinmarketcap_t_data)
    
    #define coin market cap parameters 
    res = {
        "name": coinmarketcap_data[0]['name'],
        "symbol": coinmarketcap_data[0]['symbol'],
        "rank": coinmarketcap_data[0]['rank'],
        "price_usd": coinmarketcap_data[0]['price_usd'],
        "24h_volume_usd": coinmarketcap_data[0]['24h_volume_usd'],
        "market_cap_usd": coinmarketcap_data[0]['market_cap_usd'],
        "percent_change_1h": coinmarketcap_data[0]['percent_change_1h'],
        "percent_change_24h": coinmarketcap_data[0]['percent_change_24h'],
        "percent_change_7d": coinmarketcap_data[0]['percent_change_7d'],
    }
    return res
    
def coinoneParameters(type):
    coinone_price_b_url = "https://api.coinone.co.kr/ticker/?currency="
    coinone_price_t_url = coinone_price_b_url + type
    coinone_price_url = urllib.request.urlopen(coinone_price_t_url).read()
    coinone_price_data = json.loads(coinone_price_url)
    
    #define coinone parameters 
    res = {
        "volume": coinone_price_data['volume'],
        "last": coinone_price_data['last'],
        "yesterday_last": coinone_price_data['yesterday_last'],
        "yesterday_low": coinone_price_data['yesterday_low'],
        "high": coinone_price_data['high'],
        "currency": coinone_price_data['currency'],
        "low": coinone_price_data['low'],
        "yesterday_first": coinone_price_data['yesterday_first'],
        "yesterday_volume": coinone_price_data['yesterday_volume'],
        "yesterday_high": coinone_price_data['yesterday_high'],
        "first": coinone_price_data['first']
    }
    return res

def bitfinexParameters(type):
    bitfinex_b_url = "https://api.bitfinex.com/v1/pubticker/"
    bitfinex_price_t_url = bitfinex_b_url + type + "usd"
    bitfinex_price_url = urllib.request.urlopen(bitfinex_price_t_url).read()
    bitfinex_price_data = json.loads(bitfinex_price_url)
    
    #define bitfinex parameters 
    res = {
        "mid": bitfinex_price_data['mid'],
        "bid": bitfinex_price_data['bid'],
        "ask": bitfinex_price_data['ask'],
        "last_price": bitfinex_price_data['last_price'],
        "low": bitfinex_price_data['low'],
        "high": bitfinex_price_data['high'],
        "volume": bitfinex_price_data['volume']
    }
    return res

def CurrencyConverter(price, currency):
    # 1 USD = 1,082.48 KRW
    ratio_USDtoKRW = 1082.48
    #if currency is 'USDtoKRW'
    converted_price = price*ratio_USDtoKRW
    
    return converted_price

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')