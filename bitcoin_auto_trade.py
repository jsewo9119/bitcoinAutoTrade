import time
import pyupbit
import datetime

access = "LtkkonPLe02FITqDa5HvUiOuAob1wLGHjwAjrMb9"
secret = "RB9V2SOlScs0KsCdkyMfqYPGLDNza6ruwKJAk1cx"
coin_count = 0
current_coin =""
btc = "KRW-BTC"
xrp = "KRW-XRP"
eth  = "KRW-ETH"
coin_list = [btc,xrp,eth]

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def coin_select(num):
    return coin_list[num]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time(coin_select(coin_count))
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price(coin_select(coin_count), 0.5)
            current_price = get_current_price(coin_select(coin_count))
            coin_count+=1
            if coin_count >=3:
                coin_count = 0
            if target_price < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(coin_select(coin_count), krw*0.9995)
                    current_coin = coin_select(coin_count)
                    print("매수")
            else:
                print('아무일도 없었다')
                print(coin_select(coin_count))
        else:
            coin = get_balance(current_coin[4:7])
            coin_quantity = 5000/pyupbit.get_current_price(current_coin)
            if coin > coin_quantity:
                upbit.sell_market_order(coin_select(coin_count), coin*0.9995)
                print('매도')
        
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
