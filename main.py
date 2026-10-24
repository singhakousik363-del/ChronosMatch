"""ChronosMatch: Zero-Copy High-Frequency Trading Engine."""

from src.order_book import Order, OrderBook


def main():
    book = OrderBook()

    print("=== ChronosMatch Matching Engine ===")

    book.submit_order(Order(1, "SELL", 10100, 5))
    print("Submitted SELL order: ID=1, Price=101.00, Qty=5")

    book.submit_order(Order(2, "BUY", 10000, 3))
    print("Submitted BUY order: ID=2, Price=100.00, Qty=3")
    print("No trade: buy price is below sell price.")

    trades = book.submit_order(Order(3, "BUY", 10100, 3))
    print("Submitted BUY order: ID=3, Price=101.00, Qty=3")

    for trade in trades:
        print(
            f"TRADE: Buy ID={trade.buy_order_id}, "
            f"Sell ID={trade.sell_order_id}, "
            f"Price={trade.price / 100:.2f}, "
            f"Qty={trade.quantity}"
        )

    print(f"Best bid: {book.best_bid()}")
    print(f"Best ask: {book.best_ask()}")
    print(f"Total trades: {len(book.trades)}")


if __name__ == "__main__":
    main()
