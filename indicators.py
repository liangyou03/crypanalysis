import pandas as pd
import numpy as np

def calculate_trader_indicators(df):
    """
    计算合约交易专用指标：
    1. EMA Ribbon (趋势)
    2. MACD (动能)
    3. ATR (止损与杠杆倍数)
    4. ADX (趋势强度 - 过滤震荡)
    5. Keltner Channels (爆发通道)
    """
    # 基础清洗
    for col in ['open', 'high', 'low', 'close', 'volume']:
        df[col] = df[col].astype(float)

    # --- 1. 趋势与动能 ---
    # EMA Ribbon
    df['EMA_7'] = df['close'].ewm(span=7, adjust=False).mean()
    df['EMA_25'] = df['close'].ewm(span=25, adjust=False).mean()
    df['EMA_99'] = df['close'].ewm(span=99, adjust=False).mean()
    
    # MACD
    exp1 = df['close'].ewm(span=12, adjust=False).mean()
    exp2 = df['close'].ewm(span=26, adjust=False).mean()
    df['MACD_Line'] = exp1 - exp2
    df['MACD_Signal'] = df['MACD_Line'].ewm(span=9, adjust=False).mean()
    df['MACD_Hist'] = df['MACD_Line'] - df['MACD_Signal']

    # --- 2. 波动率与风控 (ATR) ---
    prev_close = df['close'].shift(1)
    tr = pd.concat([
        df['high'] - df['low'],
        (df['high'] - prev_close).abs(),
        (df['low'] - prev_close).abs()
    ], axis=1).max(axis=1)
    df['ATR'] = tr.rolling(window=14).mean()
    
    # *** 核心功能：最大安全杠杆计算 ***
    # 逻辑：止损通常设在 2*ATR。如果 2*ATR 是 5% 的跌幅，为了不爆仓，杠杆最好不要超过 10倍
    # 公式：Max_Lev = 风险偏好系数 / 波动率
    df['Volatility_Pct'] = (df['ATR'] / df['close'])
    # 假设我们允许单笔止损亏损本金的 2% (风险模型)，止损距离是 2ATR
    df['Safe_Leverage'] = 0.02 / (2 * df['Volatility_Pct']) 
    df['Safe_Leverage'] = df['Safe_Leverage'].clip(upper=20) # 限制最高显示 20x，防止太激进

    # --- 3. 趋势强度 (ADX) ---
    # ADX > 25 代表有趋势，ADX < 20 代表震荡(不要开合约)
    plus_dm = df['high'].diff()
    minus_dm = df['low'].diff()
    plus_dm = np.where((plus_dm > minus_dm) & (plus_dm > 0), plus_dm, 0.0)
    minus_dm = np.where((minus_dm > plus_dm) & (minus_dm > 0), minus_dm, 0.0)
    
    tr_s = df['ATR'] # 使用 ATR 作为 TR 的平滑
    plus_di = 100 * (pd.Series(plus_dm).ewm(alpha=1/14).mean() / tr_s)
    minus_di = 100 * (pd.Series(minus_dm).ewm(alpha=1/14).mean() / tr_s)
    dx = (abs(plus_di - minus_di) / abs(plus_di + minus_di)) * 100
    df['ADX'] = dx.ewm(alpha=1/14).mean()

    # --- 4. 肯特纳通道 (Keltner Channels) ---
    # 用于止盈：价格冲破上轨通常是短期顶部
    df['KC_Mid'] = df['close'].ewm(span=20).mean()
    df['KC_Upper'] = df['KC_Mid'] + 2 * df['ATR']
    df['KC_Lower'] = df['KC_Mid'] - 2 * df['ATR']
    
    # 辅助：RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    return df