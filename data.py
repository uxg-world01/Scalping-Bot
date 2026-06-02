# data.py – Data fetching and price‑action structure detection (NO indicators)
import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from config import SWING_LOOKBACK, STRUCTURE_SWING_COUNT

def initialize_mt5():
    if not mt5.initialize():
        print("MT5 initialize failed")
        return False
    return True

def fetch_rates(symbol, timeframe, bars=300):
    tf = mt5.TIMEFRAME_M1 if timeframe == "1min" else mt5.TIMEFRAME_M5
    rates = mt5.copy_rates_from_pos(symbol, tf, 0, bars)
    if rates is None or len(rates) < bars:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    return df

def add_swing_points(df):
    """Detect swing highs and lows using SWING_LOOKBACK bars."""
    high = df['high']
    low = df['low']
    # Swing high: highest of surrounding SWING_LOOKBACK bars
    df['swing_high'] = high[
        (high == high.rolling(window=2*SWING_LOOKBACK+1, center=True).max())
    ]
    df['swing_low'] = low[
        (low == low.rolling(window=2*SWING_LOOKBACK+1, center=True).min())
    ]
    return df

def market_structure(df):
    """Returns 'bullish', 'bearish', or 'range' based on last swing pivots."""
    sh = df['swing_high'].dropna()
    sl = df['swing_low'].dropna()
    if len(sh) < STRUCTURE_SWING_COUNT or len(sl) < STRUCTURE_SWING_COUNT:
        return 'range'
    hh = sh.iloc[-STRUCTURE_SWING_COUNT:].values
    ll = sl.iloc[-STRUCTURE_SWING_COUNT:].values
    # Higher highs and higher lows
    if all(hh[i] > hh[i-1] for i in range(1, len(hh))) and \
       all(ll[i] > ll[i-1] for i in range(1, len(ll))):
        return 'bullish'
    # Lower highs and lower lows
    if all(hh[i] < hh[i-1] for i in range(1, len(hh))) and \
       all(ll[i] < ll[i-1] for i in range(1, len(ll))):
        return 'bearish'
    return 'range'

def get_support_resistance(df):
    """Support = last 3 swing lows mean, Resistance = last 3 swing highs mean."""
    sl = df['swing_low'].dropna().tail(3)
    sh = df['swing_high'].dropna().tail(3)
    if len(sl) == 0 or len(sh) == 0:
        return None, None
    return sl.mean(), sh.mean()

def is_high_volume(df):
    """Check if current candle has volume > threshold * average of last VOLUME_LOOKBACK candles."""
    from config import VOLUME_LOOKBACK, VOLUME_THRESHOLD
    vol = df['tick_volume'].iloc[-1]
    avg_vol = df['tick_volume'].tail(VOLUME_LOOKBACK).mean()
    return vol > avg_vol * VOLUME_THRESHOLD