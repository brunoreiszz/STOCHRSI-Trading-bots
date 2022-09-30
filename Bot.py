import websocket, json, pprint, talib, numpy, tulipy
import config
from binance.client import Client
from binance.enums import *

SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

RSI_PERIOD = 14
RSI_OVERBOUGHT = 70
RSI_OVERSOLD = 30
TRADE_SYMBOL = 'ETHUSDT'
TRADE_QUANTITY = 1

closes = []
in_position = False

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
    global closes, in_position
    # global price_on_buy

    # print("Received message")
    json_message = json.loads(message)
    # pprint.pprint(json_message)

    candle = json_message['k']
    isCandleClosed = candle['x']
    close = candle['c']

    price = candle['c']
    print("ETH price {}".format(price))

    if isCandleClosed:
        print("Candle closed at {}".format(close))
        closes.append(float(close))
        print("Closes:")
        print(closes)

        
        if len(closes) > RSI_PERIOD:
            np_closes = numpy.array(closes)
            rsi = tulipy.rsi(np_closes, RSI_PERIOD)
            print("All RSI values:")
            print(rsi)
            last_rsi = rsi[-1]
            print("The current RSI {}".format(last_rsi))

            if last_rsi > RSI_OVERBOUGHT:
                if in_position:
                    print("Sell! Sell! Sell!")
                    # put binance sell logic here
                    order_succeeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_SELL)
                    if order_succeeded:
                        print("$$$ MARKET SELL $$$")
                        print(order_succeeded)
                        in_position = False
                        # if price_on_buy > price:
                           # print("$$$ PROFIT of $$$")
                else:
                    print("RSI Overbought, but already out of position")

            if last_rsi < RSI_OVERSOLD:
                if in_position:
                    print("RSI Oversold, but already in position")
                else:
                    print("Buy! Buy! Buy!")
                    # put binance order logic here
                    order_succeeded = order(TRADE_SYMBOL, TRADE_QUANTITY, SIDE_BUY)
                    if order_succeeded:
                        print("$$$ MARKET BUY $$$")
                        print(order_succeeded)
                        in_position = True
                        # price_on_buy = price
                        # print("MARKET BUY order at ${}".format(price_on_buy))

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
print(client.get_account())
ws.run_forever()

