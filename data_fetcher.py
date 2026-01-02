# data_fetcher.py
import pandas as pd
import feedparser
from config import exchange
from indicators import calculate_trader_indicators

def fetch_data(symbol, limit=100):
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, '1d', limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        if len(df) < 50: return pd.DataFrame()
        return calculate_trader_indicators(df)
    except Exception as e:
        print(f"⚠️ Fetch Error {symbol}: {e}")
        return pd.DataFrame()

def get_market_dashboard():
    """生成详细的市场仪表盘"""
    print("🚦 分析 BTC 盘面细节...")
    df = fetch_data('BTC/USDT')
    if df.empty: return {}
    
    curr = df.iloc[-1]
    prev = df.iloc[-2]
    
    # 细化评分逻辑
    score = 50
    ema_structure = "纠缠 (无方向)"
    if curr['EMA_7'] > curr['EMA_25'] > curr['EMA_99']:
        score += 25
        ema_structure = "多头完美排列 (Bullish)"
    elif curr['EMA_7'] < curr['EMA_25'] < curr['EMA_99']:
        score -= 25
        ema_structure = "空头完美排列 (Bearish)"
    
    macd_status = "动能衰竭"
    if curr['MACD_Hist'] > 0:
        if curr['MACD_Hist'] > prev['MACD_Hist']:
            score += 15
            macd_status = "多头动能增强 (Accelerating)"
        else:
            score += 5
            macd_status = "多头动能减弱 (Decelerating)"
    else:
        if curr['MACD_Hist'] < prev['MACD_Hist']:
            score -= 15
            macd_status = "空头抛压增强 (Dumping)"
            
    signal_light = "⚪ 震荡观望"
    if score >= 75: signal_light = "🟢 极强多头 (Strong Long)"
    elif score >= 55: signal_light = "🟢 弱多头 (Weak Long)"
    elif score <= 25: signal_light = "🔴 极强空头 (Strong Short)"
    elif score <= 45: signal_light = "🔴 弱空头 (Weak Short)"

    return {
        "price": float(curr['close']),
        "score": int(score),
        "signal_light": signal_light,
        "ema_structure": ema_structure,
        "macd_status": macd_status,
        "adx": float(round(curr['ADX'], 1)),
        "rsi": float(round(curr['RSI'], 1)),
        "safe_leverage": float(round(curr['Safe_Leverage'], 1))
    }

def scan_setups():
    """扫描机会，并提取用于'推理'的细节数据"""
    print("🛰️ 深度扫描全市场...")
    tickers = exchange.fetch_tickers()
    valid = [t for s, t in tickers.items() if s.endswith('/USDT') and t['quoteVolume'] > 15000000]
    
    sorted_tickers = sorted(valid, key=lambda x: x['percentage'], reverse=True)
    candidates = sorted_tickers[:6] + sorted_tickers[-4:]
    
    setups = []
    
    for t in candidates:
        symbol = t['symbol']
        df = fetch_data(symbol)
        if df.empty: continue
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        # --- 强制类型转换区 ---
        # 这里必须用 bool() 包裹，否则就是 numpy.bool_
        is_bullish = bool(curr['close'] > curr['EMA_99'])
        
        pattern = "无明显形态"
        
        if is_bullish and (curr['close'] > curr['EMA_25']) and (curr['RSI'] < 60) and (curr['RSI'] > 40):
            pattern = "空中加油 (Bull Flag)"
        elif (prev['close'] < prev['EMA_99']) and (curr['close'] > curr['EMA_99']) and (curr['volume'] > prev['volume']*1.5):
            pattern = "底部放量突破 (Reversal)"
        elif curr['close'] > curr['KC_Upper']:
            pattern = "极度强势 (Super Trend)"
            
        if pattern != "无明显形态" or abs(t['percentage']) > 8:
            
            support = curr['EMA_25']
            
            setups.append({
                "ticker": symbol,
                "price": float(curr['close']),
                "change": f"{t['percentage']:.2f}%",
                "pattern": pattern,
                "tech_details": {
                    "rsi": float(round(curr['RSI'], 1)),
                    "adx": float(round(curr['ADX'], 1)),
                    "dist_to_ema25": f"{(curr['close'] - curr['EMA_25'])/curr['EMA_25']*100:.2f}%",
                    "vol_spike": f"{curr['volume']/df['volume'].rolling(20).mean().iloc[-1]:.1f}x"
                },
                "risk_data": {
                    "atr_stop": float(round(curr['ATR'] * 2.0, 4)),
                    "max_lev": float(round(curr['Safe_Leverage'], 1))
                },
                "support_level": float(round(support, 4)),
                # 修复点：确保这里传入的是 python bool
                "is_bullish_trend": is_bullish 
            })
            
    return setups[:4]

def get_news_context():
    print("📰 抓取新闻...")
    try:
        urls = ['https://cryptopanic.com/news/rss/', 'https://cointelegraph.com/rss']
        news = []
        for url in urls:
            d = feedparser.parse(url)
            for e in d.entries[:3]:
                news.append(e.title)
        return list(set(news))[:8] 
    except:
        return []