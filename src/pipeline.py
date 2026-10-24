"""Connect the memory-mapped ring buffer to the order book."""

from src.order_book import Order, OrderBook, Trade
from src.ring_buffer import RingBuffer


def process_buffer(buffer: RingBuffer, book: OrderBook) -> list[Trade]:
    """Read queued orders and submit them to the matching engine."""
    all_trades: list[Trade] = []

    while True:
        item = buffer.read_order()
        if item is None:
            break

        order = Order(
            order_id=item["order_id"],
            side=item["side"],
            price=item["price"],
            quantity=item["quantity"],
        )
        all_trades.extend(book.submit_order(order))

    return all_trades
