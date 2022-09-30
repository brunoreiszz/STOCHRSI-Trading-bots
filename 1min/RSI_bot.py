import websocket, json
import numpy as np
import tulipy as ti
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 7
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 0.5

closes = []
in_position = False
num_trades = 0
price_buy = 0
price_sell = 0
pnl = 0

client = Client(config.API_KEY, config.API_SECRET, testnet=True)

def order(symbol, quantity, side, order_type=ORDER_TYPE_MARKET):
    try:
        print("Sending order")    
        order = client.create_order(
            symbol = symbol,
            side = side,
            type = order_type,
            quantity = quantity
            )
        print(order)
    except Exception as e:
        return False

    return True

def on_open(ws):
    print("Connection open")

def on_close(ws):
    print("Connection closed")

def on_message(ws, message):
    global closes, in_position, num_trades, price_buy, price_sell, pnl

    # print("Received message")
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']
    isCandleClosed = candle['x']
    close = candle['c']

    price = candle['c']
    priceINT = float(price)
    #print("ETH price ${}".format(price))   

    if isCandleClosed:
        print("---\nRSI ETH - Candle closed at {}\n---".format(close))
        closes.append(float(close))
        #print("Closes:")
        #print(closes)

        if len(closes) > RSI_PERIOD:
            np_closes = np.array(closes) 
            
            rsi = ti.rsi(np_closes, period=RSI_PERIOD)
            rsinp = np.array(rsi)
            #print("RSI values:")
            #print(rsi)
            
            last_rsi = rsi[-1]
            print("RSI is {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Sell! Sell! Sell!")
                    # put binance sell logic here
                    #order_succeeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_SELL)

                    #if order_succeeded:
                    print("----------------------------\n$$$ MARKET SELL $$$\n----------------------------")
                    price_sell = priceINT
                    in_position = False
                    print("MARKET SELL order at ${}".format(price_sell))

                    if price_buy < price_sell:
                        profit = price_sell - price_buy
                        print("------\n$$++ PROFIT of + ${} ++$$\n------".format(profit))
                        num_trades += 1
                        print("Trades so far = {}".format(num_trades))
                        pnl += profit
                        print("-----\nCurrent PnL is ${}\n-----".format(pnl))
                    else:
                        loss = price_sell - price_buy
                        print("------\n$$-- LOSS of ${} --$$\n------".format(loss))
                        num_trades += 1
                        print("Trades so far = {}".format(num_trades))
                        pnl += loss
                        print("-----\nCurrent PnL is ${}\n-----".format(pnl))
                            
                else:
                    print("--ALREADY OUT OF POSITION--")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("--ALREADY IN POSITION--")
                else:
                    print("Buy! Buy! Buy!")
                    # put binance order logic here
                    # order_succeeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_BUY)
                    #if order_succeeded:
                    print("----------------------------\n$$$ MARKET BUY $$$\n----------------------------")
                    price_buy = priceINT
                    print("MARKET BUY order at ${}".format(price_buy))
                    num_trades += 1
                    print("Trades so far = {}".format(num_trades))
                    in_position = True
                        

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
print(client.get_account())
ws.run_forever()



