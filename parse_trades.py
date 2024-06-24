###!/usr/bin/python3

from decimal import Decimal as Dec


THEADER = "#asset,transaction date,transaction type,coin amount,EUR,fee,PricePerUnit"


def read_csv():
    data = []
    f = open("ledgers.csv", "r")
    lines = f.readlines()
    for line in lines:
        data.append(line.replace('"',''))
    return data


def extract_ticker(ticker):
    if ticker in {"ADA", "ADA.S"}:
        return "ADA"
    if ticker in {"DOT", "DOT.S"}:
        return "DOT"
    if ticker in {"ZEUR", "EUR.HOLD", "EUR"}:
        return "EUR"
    if ticker in {"XXBT", "BTC"}:
        return "BTC"
    if ticker in {"XETH", "ETH"}:
        return "ETH"
    if "LRC" in ticker:
        return "LRC"
    if ticker in {"XXRP", "XRP"}:
        return "XRP"
    if ticker in {"XXLM", "XLM"}:
        return "XLM"
    if ticker in {"XXDG", "DOGE"}:
        return "DOGE"
    if "CHZ" in ticker:
        return "CHZ"
    if "LINK" in ticker:
        return "LINK"
    if "MATIC" in ticker:
        return "MATIC"
    if "ETHW" in ticker:
        return "ETHW"
    if ticker in {"RNDR"}:
        return "RNDR"
    if ticker in {"PEPE"}:
        return "PEPE"
    if ticker in {"ONDO"}:
        return "ONDO"
    return "TICKER"

def sort_data(data):
    return sorted(data, key=lambda x:x[:3])

def ppu(amount, cost, ticker):
    if ticker in {"PEPE"}:
        return "%0.10f" % (abs(cost)/abs(amount))
    return "%0.2f" % (abs(cost)/abs(amount))

def purchase_sale(line1, line2):
    if extract_ticker(line1[6]) == "EUR":
        # purchase
        return f"{extract_ticker(line2[6])},{line2[2]},purchase,{Dec(line2[8])},{Dec(line1[8])},{Dec(line1[9])}," \
               f"{ppu(Dec(line2[8]), Dec(line1[8]), extract_ticker(line2[6]))}"
    # sale
    return f"{extract_ticker(line1[6])},{line2[2]},sale,{Dec(line1[8])},{Dec(line2[8])},{Dec(line2[9])}," \
           f"{ppu(Dec(line1[8]), Dec(line2[8]), extract_ticker(line2[6]))}"


def parse_trades():
    data = [THEADER]
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
            data.append(f"{ticker1},{line1s[2]},deposit,0,{Dec(line1s[8])},0")
            continue
        if line1s[3] == "staking" or (line1s[3] == "earn" and line1s[4] == "reward"):
            data.append(f"{ticker1},{line1s[2]},staking,{Dec(line1s[8])},0,{Dec(line1s[9])}")
            continue
        for line2 in data_lines[i+1:]:
            line2s = line2.split(",")
            if len(line2s) < 5:
                break
            if line1s[1] == line2s[1]:
                if line1s[3] in {"spend", "trade"} and line2s[3] in {"receive", "trade"}:
                    data.append(purchase_sale(line1s, line2s))
                    break
                if line1s[3] == "deposit" and line2s[4] == "spotfromfutures":
                    data.append(f"{extract_ticker(line2s[6])},{line2s[2]},deposit,{Dec(line2s[8])},0,{Dec(line2s[9])}")
                    break
            if line2s[3] == "withdrawal":
                break
    #return sort_data(data)
    return data

def cleanup_staking(data):
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


trades = parse_trades()
#for item in trades:
#    print(item)

new_data = cleanup_staking(trades)
for item in new_data:
    print(item)
