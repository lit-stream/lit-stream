#from flask import Flask, render_template
from decimal import Decimal as Dec
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json

import config as cfg

DATA = cfg.DATA

def coin_price(coins):
    url = cfg.url
    coins = ','.join(coins)
    
    parameters = {
        'symbol':coins,
        'convert':'EUR'
    }
    headers = {
      'Accepts': 'application/json',
      'X-CMC_PRO_API_KEY': cfg.api_key,
    }
    session = Session()
    session.headers.update(headers)
    try:
        response = session.get(url, params=parameters)
        return json.loads(response.text)
        #return (data['data'][coin]['quote']['EUR']['price'])
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
        return e

def read_csv():
    csv_data = []
    f = open("ledgers.csv", "r")
    lines = f.readlines()
    for line in lines:
        csv_data.append(line.replace('"',''))
    return csv_data

def extract_ticker(ticker):
    for coin in DATA.keys():
        if ticker in DATA[coin]["ticker"]:
            return coin
    else:
        return "unknown"

def ppu(amount, cost, ticker):
    if ticker in {"PEPE"}:
        return "%0.10f" % (abs(cost)/abs(amount))
    return "%0.2f" % (abs(cost)/abs(amount))

def purchase_sale(line1, line2):
    line1_ticker = extract_ticker(line1[6])
    line2_ticker = extract_ticker(line2[6])
    date = line2[2]
    p_price = ppu(Dec(line2[8]), Dec(line1[8]), line2_ticker)
    s_price = ppu(Dec(line1[8]), Dec(line2[8]), line1_ticker)
    print(DATA)

    if line1_ticker == "EUR": # purchase
        DATA[line2_ticker]["purchase"].append({"date": date,
                                               "amount": Dec(line2[8]),
                                               "price": Dec(line1[8]),
                                               "ppu": p_price,
                                               "fee": Dec(line1[9])
                                               })
        DATA["EUR"]["total_fee"] += round(Dec(line1[9]), 4)
        return True
    # sale
    DATA[line1_ticker]["sale"].append({"date": date,
                                       "amount": Dec(line1[8]),
                                       "price": Dec(line2[8]),
                                       "ppu": s_price,
                                       "fee": Dec(line2[9])
                                       })
    DATA["EUR"]["total_fee"] += round(Dec(line2[9]), 4)
    print(DATA)
    return True

def parse_trades():
    data_lines = read_csv()
    del data_lines[0]
    for i, line1 in enumerate(data_lines):
        line1s = line1.split(",")
        if len(line1s) < 5:
            continue
        ticker1 = extract_ticker(line1s[6])
        if line1s[3] == "transfer" and (line1s[4] == "stakingfromspot" or line1s[4] == "spottostaking"):
            continue
        if line1s[3] == "withdrawal":
            continue
        if line1s[3] == "deposit" and ticker1 == "EUR":
            DATA[ticker1]["deposit"].append({"date": line1s[2],
                                             "amount": Dec(line1s[8])
                                             })
            DATA["EUR"]["total_deposits"] = Dec(DATA["EUR"]["total_deposits"]) + Dec(line1s[8])
            continue
        if line1s[3] == "staking" or (line1s[3] == "earn" and line1s[4] == "reward"):
            DATA[ticker1]["staking"]["date"] = line1s[2]
            DATA[ticker1]["staking"]["amount"] += round(Dec(line1s[8]), 10)
            DATA[ticker1]["staking"]["fee"] += round(Dec(line1s[9]), 10)
            continue
        if line1s[3] == "transfer" and line1s[4] == "spotfromfutures":
            DATA[ticker1]["purchase"].append({"date": line1s[2],
                                              "amount": Dec(line1s[8]),
                                              "price": 0,
                                              "ppu": 0,
                                              "fee": 0
                                              })
            continue
        for line2 in data_lines[i+1:]:
            line2s = line2.split(",")
            if len(line2s) < 5:
                continue
            if line1s[1] == line2s[1]:
                if line1s[3] in {"spend", "trade"} and line2s[3] in {"receive", "trade"}:
                    purchase_sale(line1s, line2s)
                    break
            if line2s[3] == "withdrawal":
                continue


'''def cleanup_staking(data):
    clean_data = []
    for item in data:
        if "staking" in item:
            split_item = item.split(",")
            ticker = split_item[0]
            coin_amount = split_item[3]
            fee = split_item[5]
            for i in range(len(clean_data)):
                if ticker in clean_data[i] and "staking" in clean_data[i]:
                    split_i = clean_data[i].split(",")
                    coin_amount = Dec(split_i[3]) + Dec(coin_amount)
                    fee = Dec(split_i[5]) + Dec(fee)
                    clean_data[i] = f"{ticker},{split_i[1]},staking,{coin_amount},0,{fee},0"
                    break
            else:
                clean_data.append(item)
        else:
            clean_data.append(item)
    return clean_data
'''

parse_trades()
#print(DATA)

