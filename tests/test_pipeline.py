import tempfile
import unittest

from src.order_book import OrderBook
from src.ring_buffer import RingBuffer
from src.pipeline import process_buffer


class TestPipeline(unittest.TestCase):
    def test_buffer_orders_reach_matching_engine(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = f"{temp_dir}/orders.bin"

            with RingBuffer(path, capacity=8) as buffer:
                book = OrderBook()

                buffer.write_order(1, RingBuffer.SELL, 10100, 5)
                buffer.write_order(2, RingBuffer.BUY, 10100, 3)

                trades = process_buffer(buffer, book)

                self.assertEqual(len(trades), 1)
                self.assertEqual(trades[0].buy_order_id, 2)
                self.assertEqual(trades[0].sell_order_id, 1)
                self.assertEqual(trades[0].price, 10100)
                self.assertEqual(trades[0].quantity, 3)
                self.assertEqual(book.best_ask(), 10100)
                self.assertEqual(process_buffer(buffer, book), [])

    def test_empty_buffer_returns_no_trades(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = f"{temp_dir}/empty.bin"

            with RingBuffer(path, capacity=4) as buffer:
                book = OrderBook()

                self.assertIsNone(buffer.read_order())
                self.assertEqual(process_buffer(buffer, book), [])
                self.assertEqual(len(book.trades), 0)

    def test_unmatched_order_remains_in_order_book(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = f"{temp_dir}/unmatched.bin"

            with RingBuffer(path, capacity=4) as buffer:
                book = OrderBook()
                buffer.write_order(10, RingBuffer.BUY, 9900, 2)

                trades = process_buffer(buffer, book)

                self.assertEqual(trades, [])
                self.assertEqual(book.best_bid(), 9900)
                self.assertIsNone(book.best_ask())
                self.assertEqual(len(book.trades), 0)


if __name__ == "__main__":
    unittest.main()
