# strategy.py – Pure price‑action signal logic
from data import market_structure, get_support_resistance, is_high_volume
from patterns import candle_confirmation

def check_signal(df):
    if len(df) < 50:
        return None

    structure = market_structure(df)
    support, resistance = get_support_resistance(df)
    if support is None or resistance is None:
        return None

    price = df['close'].iloc[-1]
    tol = (resistance - support) * 0.1  # 10% of S/R range
    last_idx = -1

    if structure == 'bullish':
        # Must be near support
        if price > support + tol:
            return None
        confs = set()
        if abs(price - support) <= tol:
            confs.add('near_support')
        pat = candle_confirmation(df, last_idx, pattern='any', level=support)
        if pat == 'bullish':
            confs.add('bullish_pattern')
        # Rejection specifically
        from patterns import is_rejection_candle
        if is_rejection_candle(df.iloc[last_idx], support, tolerance=0.0005):
            confs.add('rejection')
        if len(confs) >= 3:
            return 'buy'

    elif structure == 'bearish':
        if price < resistance - tol:
            return None
        confs = set()
        if abs(price - resistance) <= tol:
            confs.add('near_resistance')
        pat = candle_confirmation(df, last_idx, pattern='any', level=resistance)
        if pat == 'bearish':
            confs.add('bearish_pattern')
        from patterns import is_rejection_candle
        if is_rejection_candle(df.iloc[last_idx], resistance, tolerance=0.0005):
            confs.add('rejection')
        if len(confs) >= 3:
            return 'sell'

    elif structure == 'range':
        # High volume must be present
        if not is_high_volume(df):
            return None
        if price <= support + tol:
            confs = set()
            if abs(price - support) <= tol:
                confs.add('near_support')
            pat = candle_confirmation(df, last_idx, pattern='any', level=support)
            if pat == 'bullish':
                confs.add('bullish_pattern')
            from patterns import is_rejection_candle
            if is_rejection_candle(df.iloc[last_idx], support, tolerance=0.0005):
                confs.add('rejection')
            if len(confs) >= 2:
                return 'buy'
        elif price >= resistance - tol:
            confs = set()
            if abs(price - resistance) <= tol:
                confs.add('near_resistance')
            pat = candle_confirmation(df, last_idx, pattern='any', level=resistance)
            if pat == 'bearish':
                confs.add('bearish_pattern')
            from patterns import is_rejection_candle
            if is_rejection_candle(df.iloc[last_idx], resistance, tolerance=0.0005):
                confs.add('rejection')
            if len(confs) >= 2:
                return 'sell'

    return None