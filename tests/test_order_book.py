import unittest

from src.order_book import Order, OrderBook


class TestOrderBook(unittest.TestCase):

    def setUp(self):
        self.book = OrderBook()

    def test_orders_do_not_match_when_prices_do_not_cross(self):
        self.book.submit_order(Order(1, "BUY", 100, 5))
        trades = self.book.submit_order(Order(2, "SELL", 105, 3))

        self.assertEqual(trades, [])
        self.assertEqual(self.book.best_bid(), 100)
        self.assertEqual(self.book.best_ask(), 105)

    def test_buy_order_matches_resting_sell(self):
        self.book.submit_order(Order(1, "SELL", 100, 5))
        trades = self.book.submit_order(Order(2, "BUY", 100, 3))

        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].price, 100)
        self.assertEqual(trades[0].quantity, 3)
        self.assertEqual(self.book.best_ask(), 100)

    def test_sell_order_matches_resting_buy(self):
        self.book.submit_order(Order(1, "BUY", 105, 4))
        trades = self.book.submit_order(Order(2, "SELL", 100, 2))

        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0].buy_order_id, 1)
        self.assertEqual(trades[0].sell_order_id, 2)
        self.assertEqual(trades[0].quantity, 2)
        self.assertEqual(self.book.best_bid(), 105)

    def test_price_time_priority(self):
        self.book.submit_order(Order(1, "SELL", 100, 2))
        self.book.submit_order(Order(2, "SELL", 100, 3))

        trades = self.book.submit_order(Order(3, "BUY", 100, 4))

        self.assertEqual(
            [(trade.sell_order_id, trade.quantity) for trade in trades],
            [(1, 2), (2, 2)],
        )

    def test_invalid_order_is_rejected(self):
        with self.assertRaises(ValueError):
            self.book.submit_order(Order(1, "BUY", 0, 5))

        with self.assertRaises(ValueError):
            self.book.submit_order(Order(2, "SELL", 100, 0))


if __name__ == "__main__":
    unittest.main()
