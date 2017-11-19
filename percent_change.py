import json
import requests
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
import time
from datetime import date

#ratio of coins
rate_bitcoin=62.86
rate_ethereum=14.56
rate_bitcoin_cash=8.89
rate_ripple=5.25
rate_dash=2.08
rate_litecoin=2.00
rate_zcash=1.72
rate_ethereum_classic=1.03
rate_monero=0.98
rate_neo=0.64

#name of coins
indexcoins = ['bitcoin', 'ethereum', 'bitcoin-cash', 'ripple', 'dash', 'litecoin', 'zcash', 'ethereum-classic', 'monero', 'neo']
coin_ratio = [62.86, 14.56, 8.89 ,5.25 ,2.08 ,2.00 ,1.72 ,1.03 ,0.98 ,0.64]

#total budget
fund_size = 100

#change the date
past_year = "2017"
past_month = "08"
past_day = "06"
past_date = past_year + past_month + past_day

history_url = 'https://coinmarketcap.com/historical/'+ past_date + '/'
html = urllib.request.urlopen(history_url).read()
soup = BeautifulSoup(html, 'html.parser')
tags = soup('tr')
count = 0
total_earnings = 0
highest_change = 0

for coin in indexcoins:
    #name of coin
    print ('**' + coin + '**') 
    r = requests.get('https://api.coinmarketcap.com/v1/ticker/' + coin + '/')
    curr_price = requests.get(r.url).json()
    percent_change_24 = curr_price[0]['percent_change_24h']
    #print the current price
    print ("Current Price: %" + percent_change_24 + '(' + str(date.today()) + ')') 
    
    if (float(percent_change_24) > float(highest_change)):
       highest_change = percent_change_24 
       highest_change_name = coin
       print (highest_change)
    
    count = count + 1

print ('**********************')
print ('Biggest Change ' + highest_change_name + ' with' + highest_change + '%')
#print ('Total Earnings: (Fund Size $' + str(fund_size) + ')' )
#print ('$ '+ str(total_earnings) + '     (' + str(100*total_earnings/fund_size) + '% )')
print ('**********************')