import websocket, json, pprint, talib
import numpy as np
import tulipy as ti
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_5m"

RSI_PERIOD = 14
#FASTK_PERIOD = 3
#FASTD_PERIOD = 3
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

    # global price_on_buy
    
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
        print("---\nShort 14-14-5 5min Candle closed at {}".format(close))
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
            
            fastk, fastd = ti.stoch(rsinp, rsinp, rsinp, 14, 5, 3)
            #print("fast k values:")
            #print(fastk)
            #print("fast d values:")
            #print(fastd)
            last_fastk = fastk[-1]
            
            last_fastd = fastd[-1]
            

            #np_closes = numpy.array(closes)
            #rsi = talib.RSI(np_closes, RSI_PERIOD)
            #print("All RSI values:")
            #print(rsi)
            #last_rsi = rsi[-1]
            print("Last K = {} AND Last D = {}\n----".format(last_fastk, last_fastd))

            if last_fastk > (last_fastd + 3):
                if in_position:
                    print("Get out! Get out! Get out!")
                    # put binance sell logic here
                    #order_succeeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_SELL)

                    #if order_succeeded:
                    print("----------------------------\n$$$ Off Short $$$\n----------------------------")
                    price_sell = priceINT
                    in_position = False
                    print("Off Short order at ${}".format(price_sell))

                    if price_buy < price_sell:
                        loss = price_sell - price_buy
                        loss1 = -(loss)
                        print("------\n$$ Loss of ${} $$\n------".format(loss1))
                        num_trades += 1
                        print("Trades so far = {}".format(num_trades))
                        pnl += loss1
                        print("-----\nCurrent PnL is ${}\n-----".format(pnl))
                    else:
                        profit = price_sell - price_buy
                        profit1 = -(profit)
                        print("------\n$$ Profit of ${} $$\n------".format(profit1))
                        num_trades += 1
                        print("Trades so far = {}".format(num_trades))
                        pnl += profit1
                        print("-----\nCurrent PnL is ${}\n-----".format(pnl))
                            
                else:
                    print("--ALREADY OUT OF POSITION--")

            if last_fastk < (last_fastd - 3):
                if in_position:
                    print("--ALREADY IN POSITION--")
                else:
                    print("Short! Short! Short!")
                    # put binance order logic here
                    # order_succeeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_BUY)
                    #if order_succeeded:
                    print("----------------------------\n$$$ MARKET SHORT $$$\n----------------------------")
                    price_buy = priceINT
                    print("SHORT order at ${}".format(price_buy))
                    num_trades += 1
                    print("Trades so far = {}".format(num_trades))
                    in_position = True

                    # ----------------- Selling Side -----------------------


                        

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
print(client.get_account())
ws.run_forever()



