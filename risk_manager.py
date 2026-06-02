# risk_manager.py – Position sizing using stop loss in points (no ATR for signal)
import MetaTrader5 as mt5
from config import RISK_PER_TRADE

def calculate_position_size(symbol, sl_points, risk_percent=None):
    if risk_percent is None:
        risk_percent = RISK_PER_TRADE
    account_info = mt5.account_info()
    if account_info is None:
        return 0.0
    balance = account_info.balance
    risk_amount = balance * risk_percent

    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        return 0.0

    tick_value = symbol_info.trade_tick_value
    tick_size = symbol_info.trade_tick_size
    point = symbol_info.point

    # Convert SL from points to ticks
    sl_ticks = sl_points * point / tick_size
    if sl_ticks == 0:
        return 0.0
    lot_size = risk_amount / (sl_ticks * tick_value)

    lot_step = symbol_info.volume_step
    lot_size = round(lot_size / lot_step) * lot_step
    return max(symbol_info.volume_min, min(symbol_info.volume_max, lot_size))

def calculate_sl_tp(df, signal):
    """Determine SL from last swing low/high, TP1=2R, TP2=3R."""
    from config import RR_RATIOS
    price = df['close'].iloc[-1]
    swing_high = df['swing_high'].dropna().iloc[-1] if not df['swing_high'].dropna().empty else df['high'].max()
    swing_low = df['swing_low'].dropna().iloc[-1] if not df['swing_low'].dropna().empty else df['low'].min()

    if signal == 'buy':
        sl = swing_low
        risk = price - sl
        tp1 = price + risk * RR_RATIOS[0]
        tp2 = price + risk * RR_RATIOS[1]
    else:
        sl = swing_high
        risk = sl - price
        tp1 = price - risk * RR_RATIOS[0]
        tp2 = price - risk * RR_RATIOS[1]
    return sl, tp1, tp2