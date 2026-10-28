import tempfile
import unittest
from pathlib import Path

from src.ring_buffer import RingBuffer


class TestRingBuffer(unittest.TestCase):
    def test_write_and_read_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "orders.bin")

            with RingBuffer(path, capacity=2) as buffer:
                buffer.write_order(1, RingBuffer.BUY, 10100, 5)

                self.assertEqual(
                    buffer.read_order(),
                    {
                        "order_id": 1,
                        "side": "BUY",
                        "price": 10100,
                        "quantity": 5,
                    },
                )
                self.assertIsNone(buffer.read_order())

    def test_full_buffer_rejects_extra_order(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "orders.bin")

            with RingBuffer(path, capacity=1) as buffer:
                buffer.write_order(1, RingBuffer.BUY, 10000, 1)

                with self.assertRaises(BufferError):
                    buffer.write_order(2, RingBuffer.SELL, 10100, 1)

    def test_invalid_order_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "orders.bin")

            with RingBuffer(path) as buffer:
                with self.assertRaises(ValueError):
                    buffer.write_order(1, 9, 10000, 1)


    def test_buffer_reuses_slots_after_reading(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / "orders.bin")

            with RingBuffer(path, capacity=2) as buffer:
                buffer.write_order(1, RingBuffer.BUY, 10000, 1)
                buffer.write_order(2, RingBuffer.SELL, 10100, 2)

                first = buffer.read_order()
                self.assertEqual(first["order_id"], 1)

                buffer.write_order(3, RingBuffer.BUY, 10200, 3)

                second = buffer.read_order()
                third = buffer.read_order()

                self.assertEqual(second["order_id"], 2)
                self.assertEqual(third["order_id"], 3)
                self.assertIsNone(buffer.read_order())


if __name__ == "__main__":
    unittest.main()
