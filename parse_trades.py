#!/usr/bin/python3

import streamlit as st
from decimal import Decimal as Dec


THEADER = "#asset,transaction_date,transaction_type,amount,cost,fee,PricePerUnit"


def read_csv():
    data = []
    f = open("ledger_long.csv","r")
    lines = f.readlines()
    for line in lines:
        data.append(line.replace('"',''))
    return data

def extract_ticker(ticker):
    if "ADA" in ticker:
        return "ADA"
    if "DOT" in ticker:
        return "DOT"
    if "ZEUR" in ticker or "EUR.HOLD" in ticker:
        return "EUR"
    if "XXBT" in ticker:
        return "BTC"
    if "XETH" in ticker:
        return "ETH"
    if "LRC" in ticker:
        return "LRC"
    if "XXRP" in ticker:
        return "XRP"
    if "XXLM" in ticker:
        return "XLM"
    if "XXDG" in ticker:
        return "DOGE"
    if "CHZ" in ticker:
        return "CHZ"
    if "LINK" in ticker:
        return "LINK"
    if "MATIC" in ticker:
        return "MATIC"
    if "ETHW" in ticker:
        return "ETHW"

def sort_data(data):
    return sorted(data, key=lambda x:x[:3])

def ppu(amount,cost):
    return (abs(cost)/abs(amount))

def purchase_sale(line1, line2):
    if extract_ticker(line1[6]) == "EUR":
        # purchase
        return f"{extract_ticker(line2[6])},{line2[2]},purchase,{Dec(line2[7])},{Dec(line1[7])},{Dec(line1[8])},{ppu(Dec(line2[7]),Dec(line1[7]))}"
    # sale
    return f"{extract_ticker(line1[6])},{line2[2]},sale,{Dec(line2[7])},{Dec(line1[7])},{Dec(line1[8]),ppu(Dec(line1[7]),Dec(line2[7]))}"

def parse_trades():
    data = []
    data.append(THEADER)
    data_lines = read_csv()
    del data_lines[0]
    for i, line1 in enumerate(data_lines):
        line1s = line1.split(",")
        if len(line1s) < 5:
            break
        if line1s[3] == "transfer" and (line1s[4] == "stakingfromspot" or line1s[4] == "spottostaking"):
            continue
        for line2 in data_lines[i+1:]:
            line2s = line2.split(",")
            if len(line2s) < 5:
                break
            if line1s[3] == line2s[3] == "deposit" and line1s[1] == line2s[1]:
                data.append(f"{extract_ticker(line2s[6])},{line2s[2]},deposit,{Dec(line2s[7])},0,{Dec(line2s[8])}")
                break
            if line1s[1] == line2s[1] and line1s[3] == "spend" and line2s[3] == "receive":
                data.append(purchase_sale(line1s, line2s))
                break
    data = sort_data(data)
    for item in data:
        print(item)

parse_trades()
