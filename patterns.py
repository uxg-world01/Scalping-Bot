# patterns.py – Candlestick pattern detection
import pandas as pd

def is_pin_bar(row, body_ratio=0.3, wick_ratio=0.6):
    body = abs(row['close'] - row['open'])
    total_range = row['high'] - row['low']
    if total_range == 0:
        return None
    lower_wick = min(row['open'], row['close']) - row['low']
    upper_wick = row['high'] - max(row['open'], row['close'])
    if body / total_range > body_ratio:
        return None
    if lower_wick >= total_range * wick_ratio and upper_wick <= total_range * 0.2:
        return 'bullish'
    elif upper_wick >= total_range * wick_ratio and lower_wick <= total_range * 0.2:
        return 'bearish'
    return None

def is_engulfing(row, prev_row):
    if prev_row is None:
        return None
    if prev_row['close'] < prev_row['open'] and row['close'] > row['open']:
        if row['open'] <= prev_row['close'] and row['close'] >= prev_row['open']:
            return 'bullish'
    elif prev_row['close'] > prev_row['open'] and row['close'] < row['open']:
        if row['open'] >= prev_row['close'] and row['close'] <= prev_row['open']:
            return 'bearish'
    return None

def is_rejection_candle(row, level, tolerance=0.0005):
    if level is None:
        return False
    low, high = row['low'], row['high']
    touch_high = abs(high - level) <= level * tolerance
    touch_low = abs(low - level) <= level * tolerance
    if touch_high and row['close'] < level * (1 - tolerance):
        return 'bearish'
    if touch_low and row['close'] > level * (1 + tolerance):
        return 'bullish'
    return None

def candle_confirmation(df, row_idx, pattern='any', level=None):
    row = df.iloc[row_idx]
    prev = df.iloc[row_idx-1] if row_idx > 0 else None
    pin = is_pin_bar(row)
    eng = is_engulfing(row, prev)
    rej = is_rejection_candle(row, level)
    patterns = {'pin': pin, 'engulfing': eng, 'rejection': rej}
    if pattern != 'any':
        return patterns.get(pattern, None)
    for p in ['rejection', 'engulfing', 'pin']:  # priority order
        if patterns[p] in ('bullish', 'bearish'):
            return patterns[p]
    return None