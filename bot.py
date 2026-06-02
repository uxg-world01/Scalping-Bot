# bot.py – Live trading loop using pure price‑action strategy
import MetaTrader5 as mt5
import time
import pandas as pd
from config import *
from data import initialize_mt5, fetch_rates, add_swing_points
from filters import all_filters_pass
from strategy import check_signal
from risk_manager import calculate_position_size, calculate_sl_tp
from execution import send_order, modify_sl
from telegram_service import send_vip_signal

def monitor_positions():
    positions = mt5.positions_get()
    if positions is None:
        return
    for pos in positions:
        if pos.magic != 123456:
            continue
        symbol = pos.symbol
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            continue
        current = tick.bid if pos.type == 1 else tick.ask
        entry = pos.price_open
        if pos.type == 0:  # buy
            risk = entry - pos.sl
            profit = current - entry
        else:
            risk = pos.sl - entry
            profit = entry - current
        if risk <= 0:
            continue
        if profit >= risk * TRAIL_ACTIVATE_AFTER:
            new_sl = current - risk * TRAIL_DISTANCE if pos.type == 0 else current + risk * TRAIL_DISTANCE
            if (pos.type == 0 and new_sl > pos.sl) or (pos.type == 1 and new_sl < pos.sl):
                modify_sl(pos.ticket, new_sl)

def run():
    if not initialize_mt5():
        return
    print("Scalping bot started (Pure Price Action)")
    while True:
        try:
            for symbol in SYMBOLS:
                if not all_filters_pass(symbol):
                    continue
                df = fetch_rates(symbol, PRIMARY_TF, bars=200)
                if df is None:
                    continue
                df = add_swing_points(df)

                existing = mt5.positions_get(symbol=symbol)
                if existing and len(existing) > 0:
                    continue

                signal = check_signal(df)
                if signal:
                    sl, tp1, tp2 = calculate_sl_tp(df, signal)
                    price = df['close'].iloc[-1]
                    point = mt5.symbol_info(symbol).point
                    sl_points = abs(price - sl) / point
                    volume = calculate_position_size(symbol, sl_points)
                    # Send order with TP1 (2R); we'll manually manage TP2 later or you can add a second order
                    order = send_order(symbol, signal, volume, sl, tp1, comment=f"PA_Scalp_{signal}")
                    if order:
                        print(f"Entry {signal} on {symbol} @ {price}")
                        send_vip_signal(
                            symbol=symbol,
                            side=signal,
                            entry=price,
                            sl=sl,
                            tp1=tp1,
                            tp2=tp2,
                            source="scalping_bot_v2",
                            timeframe=PRIMARY_TF,
                            status="EXECUTED",
                            order_id=order,
                        )

            monitor_positions()
            time.sleep(10)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    run()
