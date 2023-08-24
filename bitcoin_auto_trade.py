import time
import pyupbit
import datetime
import numpy as np

access = "MMGSnxR3gZgqMJMd6SOYeE7fw3PEqmhagjfpdJCa"
secret = "A7xPRF1R9bJcPrM8fRVAwYXvoLl7OVRSSBPao0ld"
coin_count = 0
current_coin =""
semi_current_coin = ""
btc = "KRW-BTC"
xrp = "KRW-XRP"
trx = "KRW-TRX"
eth  = "KRW-ETH"
is_on_trading = False

coin_list = [btc,xrp,trx,eth]
upbit = pyupbit.Upbit(access, secret)

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

# 최고의 k 값 구하기

def get_ror(k):
    df = pyupbit.get_ohlcv(semi_current_coin,count = 7)
    df['range'] = (df['high'] - df['low']) * k
    df['target'] = df['open'] + df['range'].shift(1)


    df['ror'] = np.where(df['high'] > df['target'],
                         df['close'] / df['target'],
                         1)

    ror = df['ror'].cumprod()[-2]
    return ror

def best_ror():
    ror_list =[]
    for k in np.arange(0.1, 1.0, 0.1):
        ror = get_ror(k)
        ror_list.append(ror)
    return (ror_list.index(max(ror_list))+1)/10



# 로그인


print("autotrade start")

# 자동매매 시작
while True:
    try:
               
        if coin_count >=len(coin_list):
            coin_count = 0
        now = datetime.datetime.now()
        start_time = get_start_time(coin_select(coin_count))
        end_time = start_time + datetime.timedelta(days=1)

        if start_time < now < end_time - datetime.timedelta(seconds=10) and is_on_trading == False :
            semi_current_coin = coin_select(coin_count)
            target_price = get_target_price(coin_select(coin_count), best_ror())
            current_price = get_current_price(coin_select(coin_count))
            
            if target_price < current_price and is_on_trading == False:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(coin_select(coin_count), krw*0.9995)
                    current_coin = coin_select(coin_count)
                    is_on_trading = True
                    print(f"{current_coin}매수")
                else : 
                    print(f'{coin_select(coin_count)}을 사기엔 현금부족')

     

            else:
                print('아무일도 없었다')
                print(coin_select(coin_count))
            coin_count+=1
        elif start_time < now < end_time - datetime.timedelta(seconds=10) and is_on_trading == True:
            print('자동투자중')
        else:
            coin = get_balance(current_coin[4:7])
            current_price = pyupbit.get_current_price(current_coin)
            coin_quantity = 5000 / current_price
            if coin > 0:
                upbit.sell_market_order(current_coin, coin*0.9995)
                is_on_trading = False
                print('매도')
        
        time.sleep(1)
    except Exception as e:
        print(e,'여기서 버그')
        time.sleep(1)
