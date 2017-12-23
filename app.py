#!/usr/bin/env python

import urllib.request
import json
import os
from urllib.request import Request, urlopen

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
    elif req.get("result").get("action") == "exchange_data":
        res = exchangeQuery(req)
    elif req.get("result").get("action") == "exchange_arbitrage":
        res = arbitrageQuery(req)
    elif req.get("result").get("action") == "currency_convert":    
        res = convertQuery(req)
    elif req.get("result").get("action") == "help_menu":
        res = menu(req)

    res = json.dumps(res, indent=4)

    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def menu(req):
    result = req.get("result")
    parameters = result.get("parameters")
    
    speech = "Currently the following exchanges are supported: GDAX, bitfinex, korbit, coinone, bithumb \n 1. [coin name or symbol]: Current price of the specific coin \n    coin name ex: Ripple; coin symbol: XRP \n 2. [gimp] [coin name or symbol]: Premium between Bitfinex and Korean exchanges \n 3. [exchange name or abbrev] [coin name or symbol]: Current price of the specific coin at the designated exchange \n    exchange abbrev: gx(GDAX), bf(bitfinex), kb(korbit), co(coinone), bt(bithumb) \n 4. [coin name or symbol] [Period]: Price change of the specific coin during the designated period \n    Period: 1 hr, 24 hr, 7 days"    
    
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "coin_market_cap"
    }

    return res

def makeCoinQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    
    cmc = coinmarketcapParameters(coin_type)

    #define coin market cap parameters 
    coin_name = str(cmc['name'])
    coin_price = str(cmc['price_usd'])
    coin_symbol = str(cmc['symbol'])
    
    #coins listed in Coinone and  Bithumb
    coinone_coins = ['BTC', 'BCH', 'ETH', 'ETC', 'XRP', 'QTUM', 'MIOTA', 'LTC', 'BTG']
    bithumb_coins = ['BTC', 'ETH', 'DASH', 'LTC', 'ETC', 'XRP', 'BCH', 'XMR', 'ZEC', 'QTUM', 'BTG', 'EOS']
    
    if coin_symbol in coinone_coins:
        co = coinoneParameters(coin_symbol)
        coinone_price = co['last']
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
    coin_name = cmc['name']
    
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
    
    #coins listed in Coinone and  Bithumb
    coinone_coins = ['BTC', 'BCH', 'ETH', 'ETC', 'XRP', 'QTUM', 'MIOTA', 'LTC', 'BTG']
    bithumb_coins = ['BTC', 'ETH', 'DASH', 'LTC', 'ETC', 'XRP', 'BCH', 'XMR', 'ZEC', 'QTUM', 'BTG', 'EOS']
    bitfinex_coins = ['BTC', 'BCH', 'ETH', 'ETC', 'ZEC', 'LTC', 'MIOTA', 'USDT', 'XMR', 'XRP', 'DASH', 'EOS', 'NEO', 'QTUM', 'BTG']
    
    if (coin_symbol in bitfinex_coins):
        bf = bitfinexParameters(coin_symbol)
        bitfinex_price = bf['last_price']
        
        #convert bitfinex price from USD to KRW
        bitfinex_price_KRW = CurrencyConverter(float(bitfinex_price), 'USD', 'KRW')
        if (coin_symbol in bithumb_coins):
            bt = bithumbParameters(coin_symbol)
            bithumb_price = float(bt['average_price'])
            
            coin_bithumb_premium = ((bithumb_price / bitfinex_price_KRW) - 1.00)*100
            coin_bithumb_premium = str(round(coin_bithumb_premium, 2))
            
            if (coin_symbol in coinone_coins):
                co = coinoneParameters(coin_symbol)
                coinone_price = float(co['last'])
                coin_coinone_premium = ((coinone_price / bitfinex_price_KRW) - 1.00)*100
                coin_coinone_premium = str(round(coin_coinone_premium, 2))
                
                speech = "Premium for " + coin_name + " is " + coin_coinone_premium + "% (for Coinone) and " + coin_bithumb_premium + "% (for Bithumb)"
            else:
                
                speech = "Premium for " + coin_name + " is " + coin_bithumb_premium + "% (for Bithumb)"
            
        else:
            if (coin_symbol in coinone_coins):
                co = coinoneParameters(coin_symbol)
                coinone_price = float(co['last'])
                
                coin_coinone_premium = ((coinone_price / bitfinex_price_KRW) - 1.00)*100
                coin_coinone_premium = str(round(coin_coinone_premium, 2))
                
                speech = "Premium for " + coin_name + " is " + coin_coinone_premium + "% (for Coinone)"
            else:
                speech = coin_name + " does not exist in Coinone or Bithumb"
                
    else:
        speech = coin_name + " does not exist in Bitfinex"    
        
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "coin_market_cap"
    }

    return res

def exchangeQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    exchange_type = parameters.get("crytpo_exchange")
    coin_type = parameters.get("cryptocurrency")
    
    cmc = coinmarketcapParameters(coin_type)

    #define coin market cap parameters 
    coin_name = str(cmc['name'])
    coin_symbol = str(cmc['symbol'])

    if exchange_type == "Bitfinex":
        bf = bitfinexParameters(coin_symbol)
        bitfinex_price = bf['last_price']
        speech = coin_name + " is  $" + bitfinex_price + " at " + exchange_type
    elif exchange_type == "Bithumb":
        bt = bithumbParameters(coin_symbol)
        bithumb_price = bt['average_price']
        speech = coin_name + " is  ₩" + bithumb_price + " at " + exchange_type
    elif exchange_type == "Coinone":
        co = coinoneParameters(coin_symbol)
        coinone_price = co['last']
        speech = coin_name + " is  ₩" + coinone_price + " at " + exchange_type
    elif exchange_type == "Korbit":
        kb = korbitParameters(coin_symbol)
        korbit_price = kb['last']
        speech = coin_name + " is  ₩" + korbit_price + " at " + exchange_type
    elif exchange_type == "GDAX":
        gx = GDAXParameters(coin_symbol)
        GDAX_price = gx['price']
        speech = coin_name + " is  $" + GDAX_price + " at " + exchange_type
            
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "nothing"
    }

    return res

def arbitrageQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    coin_type = parameters.get("cryptocurrency")
    
    cmc = coinmarketcapParameters(coin_type)
    
    #define coin market cap parameters 
    coin_name = str(cmc['name'])
    coin_symbol = str(cmc['symbol'])
    
    #coins listed in Coinone and  Bithumb
    coinone_coins = ['BTC', 'BCH', 'ETH', 'ETC', 'XRP', 'QTUM', 'MIOTA', 'LTC', 'BTG']
    bithumb_coins = ['BTC', 'ETH', 'DASH', 'LTC', 'ETC', 'XRP', 'BCH', 'XMR', 'ZEC', 'QTUM', 'BTG', 'EOS']
    
    if (coin_symbol in bithumb_coins):
        bt = bithumbParameters(coin_symbol)
        bithumb_price = float(bt['average_price'])
        
        if (coin_symbol in coinone_coins):
            co = coinoneParameters(coin_symbol)
            coinone_price = float(co['last'])
            
            #compare between exchanges 
            if (bithumb_price >= coinone_price):
                coin_premium = ((bithumb_price/coinone_price) - 1.00)*100
                coin_premium = str(round(coin_premium, 2))
                speech = "[Coinone -> Bithumb] : Premium for " + coin_name + " is " + coin_premium + "%"
            else:
                coin_premium = ((coinone_price/bithumb_price) - 1.00)*100
                coin_premium = str(round(coin_premium, 2))
                speech = "[Bithumb -> Coinone] : Premium for " + coin_name + " is " + coin_premium + "%"
        else:
            speech = coin_name + " does not exist in Coinone or Bithumb"
    else:
        speech = coin_name + " does not exist in Coinone or Bithumb"
                
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "nothing"
    }
    return res

def convertQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    b_currency = parameters.get("before_currency")
    a_currency = parameters.get("after_currency")
    price = parameters.get("number")
    
    #converted_price = CurrencyConverter(1100, 'USD', 'KRW')
    #float(price), b_currency, a_currency)
    
    
    speech = " is approximately equal to xxx"
    
    res = {
        "speech": speech,
        "displayText": speech,
        "data": {},
        "contextOut": [],
        "source": "nothing"
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
    if (type == 'MIOTA'):
        type = 'IOTA'
        
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
    if (type == 'MIOTA'):
        type = 'IOT'
    elif (type == 'QTUM'):
        type = 'QTM'
    elif (type == 'DASH'):
        type = 'DSH'

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
    
def bithumbParameters(type):
    bithumb_b_url = "https://api.bithumb.com/public/ticker/"
    bithumb_price_t_url = bithumb_b_url + type
    bithumb_price_url = urllib.request.urlopen(bithumb_price_t_url).read()
    bithumb_price_data = json.loads(bithumb_price_url)
    
    #define bitfinex parameters 
    res = {
        "opening_price" : bithumb_price_data['data']['opening_price'],
        "closing_price" : bithumb_price_data['data']['closing_price'],
        "min_price"     : bithumb_price_data['data']['min_price'],
        "max_price"     : bithumb_price_data['data']['max_price'],
        "average_price" : bithumb_price_data['data']['average_price'],
        "units_traded"  : bithumb_price_data['data']['units_traded'],
        "volume_1day"   : bithumb_price_data['data']['volume_1day'],
        "volume_7day"   : bithumb_price_data['data']['volume_7day'],
        "buy_price"     : bithumb_price_data['data']['buy_price'],
        "sell_price"    : bithumb_price_data['data']['sell_price']
    }
    return res

def korbitParameters(type):
    korbit_b_url = "https://api.korbit.co.kr/v1/ticker/detailed?currency_pair="
    type = type.lower()
    korbit_price_t_url = korbit_b_url + type + "_krw"
    korbit_price_t2_url = Request(korbit_price_t_url, headers={'User-Agent': 'Mozilla/5.0'})
    korbit_price_url = urlopen(korbit_price_t2_url).read()
    korbit_price_data = json.loads(korbit_price_url)
    
    #define bitfinex parameters 
    res = {
        "last": korbit_price_data['last'],
        "bid": korbit_price_data['bid'],
        "ask": korbit_price_data['ask'],
        "low": korbit_price_data['low'],
        "high": korbit_price_data['high'],
        "volume": korbit_price_data['volume']
    }
    return res

#def CoincheckParameters(type)
#https://coincheck.com/api/ticker

def GDAXParameters(type):
    GDAX_b_url = "https://api.gdax.com/products/"
    GDAX_price_t_url = GDAX_b_url + type + "-USD/ticker"
    GDAX_price_url = urllib.request.urlopen(GDAX_price_t_url).read()
    GDAX_price_data = json.loads(GDAX_price_url)
    
    res = {
        "price": GDAX_price_data['price'],
        "size": GDAX_price_data['size'],
        "bid": GDAX_price_data['bid'],
        "ask": GDAX_price_data['ask'],
        "volume": GDAX_price_data['volume']
        }
    return res


def CurrencyConverter(price, from_currency, to_currency):

    currency_b_url = 'https://api.fixer.io/latest?base='
    currency_t_url = currency_b_url + from_currency
    currency_price_url = urllib.request.urlopen(currency_t_url).read()
    currency_price_data = json.loads(currency_price_url)
    
    currency_ratio = currency_price_data['rates'][to_currency]
    converted_price = price*currency_ratio
    
    return converted_price

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    #print "Starting app on port %d" % port

    app.run(debug=True, port=port, host='0.0.0.0')