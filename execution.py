# execution.py – Order sending and management
import MetaTrader5 as mt5
import time

def send_order(symbol, order_type, volume, sl, tp, comment="ScalpBot"):
    if order_type == 'buy':
        trade_type = mt5.ORDER_TYPE_BUY
        price = mt5.symbol_info_tick(symbol).ask
    else:
        trade_type = mt5.ORDER_TYPE_SELL
        price = mt5.symbol_info_tick(symbol).bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": volume,
        "type": trade_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": comment,
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"Order failed: {result.comment}")
        return None
    return result.order

def close_position(position_id):
    pos = mt5.positions_get(ticket=position_id)
    if pos is None or len(pos) == 0:
        return None
    pos = pos[0]
    tick = mt5.symbol_info_tick(pos.symbol)
    order_type = mt5.ORDER_TYPE_BUY if pos.type == 1 else mt5.ORDER_TYPE_SELL
    price = tick.bid if order_type == mt5.ORDER_TYPE_SELL else tick.ask
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": pos.symbol,
        "volume": pos.volume,
        "type": order_type,
        "position": pos.ticket,
        "price": price,
        "deviation": 20,
        "magic": 123456,
        "comment": "Close by ScalpBot",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    return result

def modify_sl(position_id, new_sl):
    pos = mt5.positions_get(ticket=position_id)
    if pos is None or len(pos) == 0:
        return None
    pos = pos[0]
    request = {
        "action": mt5.TRADE_ACTION_SLTP,
        "position": pos.ticket,
        "sl": new_sl,
        "tp": pos.tp,
    }
    result = mt5.order_send(request)
    return result
