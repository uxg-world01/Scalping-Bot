# filters.py – Spread, session, and optional news filter
import MetaTrader5 as mt5
from config import MAX_SPREAD, LONDON_OPEN, LONDON_CLOSE, NY_OPEN, NY_CLOSE
from datetime import datetime, timezone

def news_filter():
    return False   # dummy, no news avoidance

def spread_filter(symbol):
    info = mt5.symbol_info_tick(symbol)
    if info is None:
        return False
    spread = (info.ask - info.bid) * 10**mt5.symbol_info(symbol).digits
    return spread > MAX_SPREAD.get(symbol, 100)

def session_filter():
    now = datetime.now(timezone.utc)
    hour = now.hour
    return not ((LONDON_OPEN <= hour < LONDON_CLOSE) or (NY_OPEN <= hour < NY_CLOSE))

def all_filters_pass(symbol):
    if news_filter():
        return False
    if spread_filter(symbol):
        return False
    if session_filter():
        return False
    return True