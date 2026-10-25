"""ChronosMatch: Ring Buffer to Order Book demo."""

import tempfile
from pathlib import Path

from src.order_book import OrderBook
from src.ring_buffer import RingBuffer
from src.pipeline import process_buffer


def main():
    print("=== ChronosMatch Trading Engine ===")

    with tempfile.TemporaryDirectory() as temp_dir:
        buffer_path = str(Path(temp_dir) / "orders.bin")

        with RingBuffer(buffer_path, capacity=8) as buffer:
            book = OrderBook()

            # Queue three orders in the ring buffer.
            orders = [
                (1, RingBuffer.SELL, 10100, 5),
                (2, RingBuffer.BUY, 10000, 3),
                (3, RingBuffer.BUY, 10100, 3),
            ]

            for order_id, side, price, quantity in orders:
                side_name = "BUY" if side == RingBuffer.BUY else "SELL"
                buffer.write_order(order_id, side, price, quantity)
                print(
                    f"Queued {side_name}: ID={order_id}, "
                    f"Price={price / 100:.2f}, Qty={quantity}"
                )

            print("\n--- Processing orders ---")
            trades = process_buffer(buffer, book)

            if trades:
                for trade in trades:
                    print(
                        f"TRADE: Buy ID={trade.buy_order_id}, "
                        f"Sell ID={trade.sell_order_id}, "
                        f"Price={trade.price / 100:.2f}, "
                        f"Qty={trade.quantity}"
                    )
            else:
                print("No trades executed.")

            best_bid = book.best_bid()
            best_ask = book.best_ask()

            print("\n--- Order Book Summary ---")
            print(
                f"Best bid: {best_bid / 100:.2f}"
                if best_bid is not None
                else "Best bid: None"
            )
            print(
                f"Best ask: {best_ask / 100:.2f}"
                if best_ask is not None
                else "Best ask: None"
            )
            print(f"Total trades: {len(book.trades)}")


if __name__ == "__main__":
    main()
