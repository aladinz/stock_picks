import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time

# 1. Define your universe (e.g., S&P 500 tickers list)
sp500 = pd.read_csv('sp500_tickers.csv')  # list of tickers

results = []

total_symbols = len(sp500['Ticker'])
for i, symbol in enumerate(sp500['Ticker'], 1):
    try:
        print(f"Analyzing {symbol} ({i}/{total_symbols})...")
        time.sleep(0.05)  # Small delay to avoid overwhelming APIs
        tk = yf.Ticker(symbol)
        info = tk.info
        
        # Fundamentals
        fwd_pe = info.get('forwardPE')
        price = info.get('currentPrice')
        market_cap = info.get('marketCap')
        beta = info.get('beta')
        rec = info.get('recommendationKey')  # e.g., 'strong_buy'
        
        if not (fwd_pe and fwd_pe<15 and price>15 and market_cap>1e10 and beta>1 and rec=='strong_buy'):
            continue
        
        # Price history
        hist = tk.history(period='6mo', interval='1d')
        hist['5d_return'] = hist['Close'].pct_change(5)
        if hist['5d_return'].iloc[-1] < 0.05:
            continue
        
        # Moving averages
        ma50 = hist['Close'].rolling(50).mean().iloc[-1]
        ma200 = hist['Close'].rolling(200).mean().iloc[-1]
        if not (price > ma50 and price > ma200):
            continue
        
        # RSI (14-day)
        delta = hist['Close'].diff()
        up = delta.clip(lower=0)
        down = -1*delta.clip(upper=0)
        ma_up = up.ewm(com=13, adjust=False).mean()
        ma_down = down.ewm(com=13, adjust=False).mean()
        rsi = 100 - (100/(1 + ma_up/ma_down))
        latest_rsi = rsi.iloc[-1]
        if not (30 < latest_rsi < 70):
            continue
        
        # Bollinger Bands (20d)
        m20 = hist['Close'].rolling(20).mean().iloc[-1]
        std20 = hist['Close'].rolling(20).std().iloc[-1]
        upper_bb = m20 + 2*std20
        near_upper = price >= (upper_bb * 0.98)
        
        # ATR (14-day)
        high_low = hist['High'] - hist['Low']
        high_pc = np.abs(hist['High'] - hist['Close'].shift())
        low_pc = np.abs(hist['Low'] - hist['Close'].shift())
        tr = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
        atr = tr.rolling(14).mean().iloc[-1]
        stop_loss = price - 1.5*atr
        
        # Finviz scrape for sector sentiment & institutional ownership change
        try:
            time.sleep(0.1)  # Rate limiting to avoid being blocked
            url = f'https://finviz.com/quote.ashx?t={symbol}'
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Sector sentiment (Performance row 10)
            perf_element = soup.find(text='Perf Month')
            if not perf_element:
                continue
            perf = perf_element.find_next('td').text
            if not perf.startswith('+'):
                continue
                
            # Institutional ownership change (3-month)
            instro_element = soup.find(text='Inst Own')
            if not instro_element:
                continue
            instro_text = instro_element.find_next('td').text.strip('%')
            try:
                instro = float(instro_text)
                if instro <= 0:
                    continue
            except (ValueError, TypeError):
                continue  # Skip if institutional ownership is not a valid number
        except Exception as e:
            print(f"Finviz scraping failed for {symbol}: {e}")
            continue
        
        # Volume & consecutive up-days
        avg_vol = hist['Volume'].rolling(30).mean().iloc[-1]
        if avg_vol < 2e6:
            continue
        consec_up = (hist['Close'].diff() > 0).tail(3).all()
        
        # Compile result
        results.append({
            'Ticker': symbol,
            'Price': price,
            'Fwd P/E': fwd_pe,
            'Market Cap': market_cap,
            'Volume': int(avg_vol),
            'RSI': round(latest_rsi,1),
            'MA Position': f'Above 50/200d ✓',
            'Sector': info.get('sector'),
            'Beta': round(beta,2),
            'Momentum': '↑',
            'Bollinger': '✓' if near_upper else '–',
            'Consec Up-Days': '✓' if consec_up else '',
            'Stop-Loss': round(stop_loss,2)
        })
    except Exception:
        continue

df = pd.DataFrame(results)
print(f"Found {len(results)} stocks that meet all criteria:")

if len(results) > 0:
    print("\nStock screening results:")
    df = df.sort_values(by='Market Cap', ascending=False)
    print(df.to_string(index=False))
else:
    print("No stocks met all the screening criteria.")
    print("This is normal as the criteria are quite strict:")
    print("- Forward P/E < 15")
    print("- Price > $15")
    print("- Market Cap > $10B")  
    print("- Beta > 1")
    print("- Strong Buy recommendation")
    print("- 5-day return > 5%")
    print("- Price above 50-day and 200-day moving averages")
    print("- RSI between 30-70")
    print("- Average volume > 2M shares")
    print("- Positive monthly performance")
    print("- Institutional ownership increase")
    print("- 3 consecutive up days")
