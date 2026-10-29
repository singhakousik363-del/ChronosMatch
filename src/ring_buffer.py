
"""Fixed-size shared-memory ring buffer for ChronosMatch."""

import mmap
import struct
from pathlib import Path


class RingBuffer:
    """Single-process ring buffer backed by a memory-mapped file."""

    HEADER = struct.Struct("<QQ")
    SLOT = struct.Struct("<Q B 7x Q Q")

    BUY = 1
    SELL = 2
    MAX_UINT64 = 0xFFFFFFFFFFFFFFFF

    def __init__(self, path: str, capacity: int = 64):
        if not isinstance(capacity, int) or isinstance(capacity, bool):
            raise ValueError("Capacity must be a positive integer")

        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        self.path = Path(path)
        self.capacity = capacity
        self.slot_size = self.SLOT.size
        self.size = self.HEADER.size + capacity * self.slot_size

        self.file = open(self.path, "w+b")
        self.file.truncate(self.size)

        try:
            self.map = mmap.mmap(self.file.fileno(), self.size)
            self.HEADER.pack_into(self.map, 0, 0, 0)
        except Exception:
            self.file.close()
            raise

    def write_order(
        self, order_id: int, side: int, price: int, quantity: int
    ) -> None:
        if (
            not isinstance(order_id, int)
            or isinstance(order_id, bool)
            or not 0 <= order_id <= self.MAX_UINT64
        ):
            raise ValueError(
                "Order ID must be a non-negative 64-bit integer"
            )

        if side not in (self.BUY, self.SELL):
            raise ValueError("Side must be BUY or SELL")

        if (
            not isinstance(price, int)
            or isinstance(price, bool)
            or not 0 < price <= self.MAX_UINT64
        ):
            raise ValueError("Price must be a positive 64-bit integer")

        if (
            not isinstance(quantity, int)
            or isinstance(quantity, bool)
            or not 0 < quantity <= self.MAX_UINT64
        ):
            raise ValueError("Quantity must be a positive 64-bit integer")

        head, tail = self.HEADER.unpack_from(self.map, 0)

        if head - tail >= self.capacity:
            raise BufferError("Ring buffer is full")

        offset = (
            self.HEADER.size
            + (head % self.capacity) * self.slot_size
        )

        self.SLOT.pack_into(
            self.map, offset, order_id, side, price, quantity
        )
        self.HEADER.pack_into(self.map, 0, head + 1, tail)

    def read_order(self) -> dict | None:
        head, tail = self.HEADER.unpack_from(self.map, 0)

        if tail >= head:
            return None

        offset = (
            self.HEADER.size
            + (tail % self.capacity) * self.slot_size
        )

        order_id, side, price, quantity = self.SLOT.unpack_from(
            self.map, offset
        )

        self.HEADER.pack_into(self.map, 0, head, tail + 1)

        return {
            "order_id": order_id,
            "side": "BUY" if side == self.BUY else "SELL",
            "price": price,
            "quantity": quantity,
        }

    def close(self) -> None:
        """Close the memory map and its backing file."""
        if not self.map.closed:
            self.map.close()

        if not self.file.closed:
            self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
