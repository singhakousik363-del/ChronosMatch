"""Simple throughput benchmark for the ChronosMatch order book."""

import argparse
import sys
import time
from pathlib import Path

# Add the project root so the benchmark can import src.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.order_book import Order, OrderBook


def run_benchmark(pairs: int) -> None:
    if pairs <= 0:
        raise ValueError("Number of pairs must be positive.")

    book = OrderBook()

    start = time.perf_counter()

    for order_id in range(1, pairs + 1):
        book.submit_order(Order(order_id, "SELL", 10100, 1))
        book.submit_order(Order(pairs + order_id, "BUY", 10100, 1))

    elapsed = time.perf_counter() - start
    total_orders = pairs * 2
    throughput = total_orders / elapsed if elapsed > 0 else 0

    print("=== ChronosMatch Order Book Benchmark ===")
    print(f"Matched pairs:       {pairs}")
    print(f"Orders submitted:    {total_orders}")
    print(f"Trades generated:    {len(book.trades)}")
    print(f"Elapsed time:        {elapsed:.6f} seconds")
    print(f"Throughput:          {throughput:,.0f} orders/second")

    if len(book.trades) != pairs:
        raise RuntimeError("Unexpected trade count; benchmark result is invalid.")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure basic ChronosMatch order-book throughput."
    )
    parser.add_argument(
        "--pairs",
        type=int,
        default=10000,
        help="Number of sell/buy pairs to process (default: 10000).",
    )
    args = parser.parse_args()
    run_benchmark(args.pairs)


if __name__ == "__main__":
    main()
