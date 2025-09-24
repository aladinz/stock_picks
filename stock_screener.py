import yfinance as yf
import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
import time

def run_stock_screening(params, progress_bar=None, status_text=None):
    """
    Run stock screening based on provided parameters
    
    Args:
        params (dict): Dictionary containing screening parameters
        progress_bar: Streamlit progress bar object (optional)
        status_text: Streamlit text object for status updates (optional)
    
    Returns:
        list: List of dictionaries containing stock data that meet criteria
    """
    
    # Load S&P 500 tickers
    try:
        sp500 = pd.read_csv('sp500_tickers.csv')
    except FileNotFoundError:
        # Create a sample if file doesn't exist
        sample_tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'META', 'NVDA', 
                         'JPM', 'JNJ', 'V', 'UNH', 'HD', 'PG', 'MA', 'DIS']
        sp500 = pd.DataFrame({'Ticker': sample_tickers})
    
    results = []
    total_symbols = len(sp500['Ticker'])
    
    for i, symbol in enumerate(sp500['Ticker'], 1):
        try:
            # Update progress
            if progress_bar:
                progress_bar.progress(i / total_symbols)
            if status_text:
                status_text.text(f"Analyzing {symbol} ({i}/{total_symbols})...")
            
            time.sleep(0.05)  # Rate limiting
            tk = yf.Ticker(symbol)
            info = tk.info
            
            # Basic validation
            if not info or 'currentPrice' not in info:
                continue
                
            # Fundamentals
            fwd_pe = info.get('forwardPE')
            price = info.get('currentPrice')
            market_cap = info.get('marketCap')
            beta = info.get('beta')
            rec = info.get('recommendationKey', '')
            
            # Apply fundamental filters
            if not fwd_pe or fwd_pe > params['max_pe']:
                continue
            if not price or price < params['min_price']:
                continue
            if not market_cap or market_cap < params['min_market_cap']:
                continue
            if not beta or beta < params['min_beta']:
                continue
                
            # Recommendation filter
            if params['recommendation_filter'] == 'strong_buy' and rec != 'strong_buy':
                continue
            elif params['recommendation_filter'] == 'buy' and rec not in ['buy', 'strong_buy']:
                continue
            
            # Price history analysis
            try:
                hist = tk.history(period='6mo', interval='1d')
                if hist.empty or len(hist) < 50:
                    continue
                    
                # 5-day return
                hist['5d_return'] = hist['Close'].pct_change(5)
                latest_return = hist['5d_return'].iloc[-1]
                if pd.isna(latest_return) or latest_return < params['min_return']:
                    continue
                
                # Moving averages
                ma50 = hist['Close'].rolling(50).mean().iloc[-1]
                ma200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) >= 200 else ma50
                if pd.isna(ma50) or pd.isna(ma200) or not (price > ma50 and price > ma200):
                    continue
                
                # RSI calculation
                delta = hist['Close'].diff()
                up = delta.clip(lower=0)
                down = -1 * delta.clip(upper=0)
                ma_up = up.ewm(com=13, adjust=False).mean()
                ma_down = down.ewm(com=13, adjust=False).mean()
                rsi = 100 - (100 / (1 + ma_up / ma_down))
                latest_rsi = rsi.iloc[-1]
                
                if pd.isna(latest_rsi) or not (params['rsi_min'] < latest_rsi < params['rsi_max']):
                    continue
                
                # Volume check
                avg_vol = hist['Volume'].rolling(30).mean().iloc[-1]
                if pd.isna(avg_vol) or avg_vol < params['min_volume']:
                    continue
                
                # Consecutive up days
                recent_changes = hist['Close'].diff().tail(params['consecutive_days'])
                consec_up = (recent_changes > 0).all()
                
                # Bollinger Bands
                m20 = hist['Close'].rolling(20).mean().iloc[-1]
                std20 = hist['Close'].rolling(20).std().iloc[-1]
                upper_bb = m20 + 2 * std20
                near_upper = price >= (upper_bb * 0.98) if not pd.isna(upper_bb) else False
                
                # ATR for stop loss
                high_low = hist['High'] - hist['Low']
                high_pc = np.abs(hist['High'] - hist['Close'].shift())
                low_pc = np.abs(hist['Low'] - hist['Close'].shift())
                tr = pd.concat([high_low, high_pc, low_pc], axis=1).max(axis=1)
                atr = tr.rolling(14).mean().iloc[-1]
                stop_loss = price - 1.5 * atr if not pd.isna(atr) else price * 0.9
                
            except Exception as e:
                print(f"Technical analysis failed for {symbol}: {e}")
                continue
            
            # Finviz scraping (if enabled)
            finviz_passed = True
            if params.get('enable_finviz', False):
                try:
                    time.sleep(0.1)  # Rate limiting
                    url = f'https://finviz.com/quote.ashx?t={symbol}'
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Monthly performance
                    perf_element = soup.find(text='Perf Month')
                    if perf_element:
                        perf = perf_element.find_next('td').text
                        if not perf.startswith('+'):
                            finviz_passed = False
                    
                    # Institutional ownership
                    if finviz_passed:
                        instro_element = soup.find(text='Inst Own')
                        if instro_element:
                            instro_text = instro_element.find_next('td').text.strip('%')
                            try:
                                instro = float(instro_text)
                                if instro <= 0:
                                    finviz_passed = False
                            except (ValueError, TypeError):
                                finviz_passed = False
                                
                except Exception as e:
                    print(f"Finviz scraping failed for {symbol}: {e}")
                    finviz_passed = False
                    
                if not finviz_passed:
                    continue
            
            # If we get here, stock passed all filters
            results.append({
                'Ticker': symbol,
                'Price': round(price, 2),
                'Fwd P/E': round(fwd_pe, 1),
                'Market Cap': market_cap,
                'Volume': int(avg_vol),
                'RSI': round(latest_rsi, 1),
                'MA Position': 'Above 50/200d ✓',
                'Sector': info.get('sector', 'Unknown'),
                'Beta': round(beta, 2),
                'Momentum': '↑' if consec_up else '→',
                'Bollinger': '✓' if near_upper else '–',
                'Consec Up-Days': '✓' if consec_up else '',
                'Stop-Loss': round(stop_loss, 2),
                '5d Return': f"{latest_return*100:.1f}%"
            })
            
        except Exception as e:
            print(f"Error processing {symbol}: {e}")
            continue
    
    # Clear progress indicators
    if progress_bar:
        progress_bar.progress(1.0)
    if status_text:
        status_text.text("Screening completed!")
    
    return results

def get_stock_info(symbol):
    """
    Get detailed information for a specific stock
    
    Args:
        symbol (str): Stock ticker symbol
    
    Returns:
        dict: Stock information
    """
    try:
        tk = yf.Ticker(symbol)
        info = tk.info
        hist = tk.history(period='1y')
        
        return {
            'info': info,
            'history': hist,
            'current_price': info.get('currentPrice'),
            'market_cap': info.get('marketCap'),
            'pe_ratio': info.get('forwardPE'),
            'beta': info.get('beta'),
            'dividend_yield': info.get('dividendYield'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow')
        }
    except Exception as e:
        print(f"Error getting info for {symbol}: {e}")
        return None

if __name__ == "__main__":
    # Default parameters for testing
    default_params = {
        'max_pe': 15,
        'min_price': 15,
        'min_market_cap': 1e10,
        'min_beta': 1.0,
        'min_return': 0.05,
        'rsi_min': 30,
        'rsi_max': 70,
        'min_volume': 2e6,
        'enable_finviz': True,
        'consecutive_days': 3,
        'recommendation_filter': 'strong_buy'
    }
    
    print("Running stock screening with default parameters...")
    results = run_stock_screening(default_params)
    
    print(f"Found {len(results)} stocks that meet all criteria:")
    if results:
        df = pd.DataFrame(results)
        print(df.to_string(index=False))
    else:
        print("No stocks met all the screening criteria.")