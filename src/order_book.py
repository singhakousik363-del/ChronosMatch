"""Core price-time priority order book for ChronosMatch."""

from dataclasses import dataclass
from collections import deque
from typing import Deque, Literal


Side = Literal["BUY", "SELL"]


@dataclass
class Order:
    order_id: int
    side: Side
    price: int
    quantity: int


@dataclass
class Trade:
    buy_order_id: int
    sell_order_id: int
    price: int
    quantity: int


class OrderBook:
    """A simple price-time priority matching engine."""

    def __init__(self):
        self.bids: dict[int, Deque[Order]] = {}
        self.asks: dict[int, Deque[Order]] = {}
        self.trades: list[Trade] = []

    def submit_order(self, order: Order) -> list[Trade]:
        if order.price <= 0:
            raise ValueError("Price must be positive")
        if order.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if order.side not in ("BUY", "SELL"):
            raise ValueError("Side must be BUY or SELL")

        new_trades = []

        if order.side == "BUY":
            while order.quantity > 0 and self.asks:
                best_price = min(self.asks)
                if best_price > order.price:
                    break

                queue = self.asks[best_price]
                resting = queue[0]
                quantity = min(order.quantity, resting.quantity)

                trade = Trade(
                    buy_order_id=order.order_id,
                    sell_order_id=resting.order_id,
                    price=resting.price,
                    quantity=quantity,
                )
                new_trades.append(trade)
                self.trades.append(trade)

                order.quantity -= quantity
                resting.quantity -= quantity

                if resting.quantity == 0:
                    queue.popleft()
                if not queue:
                    del self.asks[best_price]

            if order.quantity > 0:
                self.bids.setdefault(order.price, deque()).append(order)

        else:
            while order.quantity > 0 and self.bids:
                best_price = max(self.bids)
                if best_price < order.price:
                    break

                queue = self.bids[best_price]
                resting = queue[0]
                quantity = min(order.quantity, resting.quantity)

                trade = Trade(
                    buy_order_id=resting.order_id,
                    sell_order_id=order.order_id,
                    price=resting.price,
                    quantity=quantity,
                )
                new_trades.append(trade)
                self.trades.append(trade)

                order.quantity -= quantity
                resting.quantity -= quantity

                if resting.quantity == 0:
                    queue.popleft()
                if not queue:
                    del self.bids[best_price]

            if order.quantity > 0:
                self.asks.setdefault(order.price, deque()).append(order)

        return new_trades

    def best_bid(self) -> int | None:
        return max(self.bids) if self.bids else None

    def best_ask(self) -> int | None:
        return min(self.asks) if self.asks else None
