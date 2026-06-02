# backtest.py – Clean vectorized backtest (no future leak)
import pandas as pd
import numpy as np
from datetime import datetime
import MetaTrader5 as mt5
from config import *
from data import add_swing_points, market_structure, get_support_resistance
from strategy import check_signal
from risk_manager import calculate_sl_tp

def backtest(symbol, start_date, end_date, initial_balance=10000):
    mt5.initialize()
    tf = mt5.TIMEFRAME_M5 if PRIMARY_TF == "5min" else mt5.TIMEFRAME_M1
    rates = mt5.copy_rates_range(symbol, tf, start_date, end_date)
    if rates is None:
        return None
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')

    # Initialize empty columns for price‑action data
    for col in ['swing_high', 'swing_low']:
        df[col] = np.nan

    balance = initial_balance
    risk_percent = RISK_PER_TRADE
    trades = []
    position = None
    entry_price = 0
    sl = tp1 = tp2 = 0

    # We need at least 50 bars for structure detection
    for i in range(50, len(df)):
        slice_df = df.iloc[:i+1].copy()
        # Recalculate swing points ONLY on data up to i (no future leak)
        slice_df = add_swing_points(slice_df)

        if position is None:
            signal = check_signal(slice_df)
            if signal:
                sl, tp1, tp2 = calculate_sl_tp(slice_df, signal)
                price = slice_df['close'].iloc[-1]
                # Simplified position sizing (risk amount / sl distance)
                risk_distance = abs(price - sl)
                volume = balance * risk_percent / risk_distance if risk_distance else 0.01
                position = {'signal': signal, 'entry': price, 'sl': sl, 
                            'tp1': tp1, 'tp2': tp2, 'volume': volume}
                entry_price = price
        else:
            # Check exit on current bar
            high, low, close = slice_df['high'].iloc[-1], slice_df['low'].iloc[-1], slice_df['close'].iloc[-1]
            if position['signal'] == 'buy':
                if low <= position['sl']:
                    exit_price = position['sl']
                elif high >= position['tp1']:
                    exit_price = position['tp1']
                else:
                    continue
            else:
                if high >= position['sl']:
                    exit_price = position['sl']
                elif low <= position['tp1']:
                    exit_price = position['tp1']
                else:
                    continue

            profit = (exit_price - entry_price) * position['volume'] if position['signal'] == 'buy' \
                     else (entry_price - exit_price) * position['volume']
            balance += profit
            trades.append({'entry_time': slice_df['time'].iloc[-1], 
                           'exit_time': slice_df['time'].iloc[-1],
                           'signal': position['signal'], 'profit': profit})
            position = None

    if trades:
        trades_df = pd.DataFrame(trades)
        win_rate = (trades_df['profit'] > 0).mean()
        total_profit = trades_df['profit'].sum()
        if len(trades_df[trades_df['profit'] < 0]) > 0:
            profit_factor = trades_df[trades_df['profit']>0]['profit'].sum() / abs(trades_df[trades_df['profit']<0]['profit'].sum())
        else:
            profit_factor = np.inf
        max_dd = (trades_df['profit'].cumsum().min()) / initial_balance
        print(f"{symbol} | Win: {win_rate:.2%} | PF: {profit_factor:.2f} | Max DD: {max_dd:.2%} | Net PnL: {total_profit:.2f}")
        return trades_df
    else:
        print("No trades.")
        return None

if __name__ == "__main__":
    # Example test
    backtest("XAUUSD", datetime(2024,1,1), datetime(2024,6,1))
    