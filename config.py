# config.py – Pure price‑action scalper configuration

import os


def _env_list(name, default):
    raw = os.getenv(name, "")
    if not raw:
        return default
    return [item.strip() for item in raw.split(",") if item.strip()]


SYMBOLS = _env_list("SYMBOLS", [
    "EURUSD", "GBPUSD", "USDJPY", "USDCHF", "USDCAD", "AUDUSD", "NZDUSD",
    "EURGBP", "EURJPY", "GBPJPY", "AUDJPY", "CADJPY", "CHFJPY",
    "EURAUD", "EURCAD", "GBPAUD", "GBPCAD", "AUDCAD", "AUDNZD", "NZDJPY",
    "XAUUSD", "XAGUSD", "US30", "NAS100", "SPX500", "GER30", "USOIL",
    "BTCUSD", "ETHUSD",
])
PRIMARY_TF = "5min"          # main timeframe for signals
SECONDARY_TF = "1min"        # optional fine‑tuning (not used by default)

# Session times (UTC)
LONDON_OPEN = 8
LONDON_CLOSE = 17
NY_OPEN = 13
NY_CLOSE = 22

# Risk & trade parameters
RISK_PER_TRADE = 0.01        # 1% of account equity
RR_RATIOS = [2.0, 3.0]       # first TP = 2R, second TP = 3R
TRAIL_ACTIVATE_AFTER = 1.5   # activate trailing after 1.5R profit
TRAIL_DISTANCE = 0.5         # trail stop at 0.5R from current price

# Market structure settings
SWING_LOOKBACK = 5           # bars for swing high/low detection
STRUCTURE_SWING_COUNT = 3    # last 3 swings to define trend

# Volume filter (range market only)
VOLUME_LOOKBACK = 20         # bars for average volume
VOLUME_THRESHOLD = 1.5       # candle volume > 1.5 * average

# Spread filter (points)
MAX_SPREAD = {
    "XAUUSD": 50,
    "XAGUSD": 60,
    "BTCUSD": 150,
    "ETHUSD": 120,
    "US30": 200,
    "NAS100": 180,
    "SPX500": 120,
    "GER30": 160,
    "USOIL": 80,
    "EURUSD": 10,
    "GBPUSD": 15,
    "USDJPY": 10,
    "USDCHF": 12,
    "USDCAD": 14,
    "AUDUSD": 12,
    "NZDUSD": 14,
    "EURGBP": 14,
    "EURJPY": 16,
    "GBPJPY": 24,
    "AUDJPY": 18,
    "CADJPY": 18,
    "CHFJPY": 18,
    "EURAUD": 18,
    "EURCAD": 18,
    "GBPAUD": 24,
    "GBPCAD": 24,
    "AUDCAD": 18,
    "AUDNZD": 20,
    "NZDJPY": 18
}

# Optional: ATR for SL distance fallback (if no swing points)
USE_ATR_FALLBACK = True
ATR_PERIOD = 14
ATR_MULTIPLIER_SL = 1.5      # SL = price ± ATR * multiplier
