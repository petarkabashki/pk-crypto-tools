import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import asyncio
import time
from decimal import Decimal
from typing import Tuple
from tabulate import tabulate

def calculate_position_size(order_price: float, target_price: float, stop_loss_price: float, risk_amount: float, margin_leverage: int, trade_type: str) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal, Decimal]:
    order_price = Decimal(str(order_price))
    target_price = Decimal(str(target_price))
    stop_loss_price = Decimal(str(stop_loss_price))
    risk_amount = Decimal(str(risk_amount))
    trade_type = trade_type.lower()
    if trade_type == "long":
        risk_per_unit = order_price - stop_loss_price
        profit_per_unit = target_price - order_price
    elif trade_type == "short":
        risk_per_unit = stop_loss_price - order_price
        profit_per_unit = order_price - target_price
    else:
        raise ValueError("Invalid trade_type. Must be 'long' or 'short'.")
    units = risk_amount / (risk_per_unit * margin_leverage)
    position_value = units * order_price
    potential_loss = units * risk_per_unit * margin_leverage
    potential_profit = units * profit_per_unit * margin_leverage
    risk2reward = potential_profit / potential_loss if potential_loss != 0 else Decimal('0')
    return units, position_value, risk_per_unit, potential_loss, potential_profit, risk2reward

def print_position_size(order_price: float, target_price: float, stop_loss_price: float, risk_amount: float, margin_leverage: int = 5, trade_type: str = "long"):
    units, position_value, risk_per_unit, potential_loss, potential_profit, risk2reward = calculate_position_size(
        order_price=order_price,
        target_price=target_price,
        stop_loss_price=stop_loss_price,
        risk_amount=risk_amount,
        margin_leverage=margin_leverage,
        trade_type=trade_type
    )
    data = [
        ["order_price", order_price, "units", f"{units:.4f}"],
        ["target_price", target_price, "position_value", f"{position_value:.4f}"],
        ["stop_loss_price", stop_loss_price, "risk_per_unit", f"{risk_per_unit:.4f}"],
        ["risk_amount", risk_amount, "potential_loss", f"{potential_loss:.4f}"],
        ["margin_leverage", margin_leverage, "potential_profit", f"{potential_profit:.4f}"],
        ["trade_type", trade_type, "risk2reward", f"{risk2reward:.4f}"]
    ]
    print(tabulate(data, headers=["Input", "Value", "Output", "Value"], tablefmt="grid"))

print_position_size(
    order_price=2687,
    target_price=2715,
    stop_loss_price=2675,
    risk_amount=500.0,
    margin_leverage=5,
    trade_type="long"
)
