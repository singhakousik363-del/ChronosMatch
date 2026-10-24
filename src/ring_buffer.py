"""Fixed-size shared-memory ring buffer for ChronosMatch."""

import mmap
import os
import struct
from pathlib import Path


class RingBuffer:
    """Single-process ring buffer backed by a memory-mapped file."""

    HEADER = struct.Struct("<QQ")
    SLOT = struct.Struct("<Q B 7x Q Q")
    BUY = 1
    SELL = 2

    def __init__(self, path: str, capacity: int = 64):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")

        self.path = Path(path)
        self.capacity = capacity
        self.slot_size = self.SLOT.size
        self.size = self.HEADER.size + capacity * self.slot_size

        self.file = open(self.path, "w+b")
        self.file.truncate(self.size)
        self.map = mmap.mmap(self.file.fileno(), self.size)
        self.HEADER.pack_into(self.map, 0, 0, 0)

    def write_order(
        self, order_id: int, side: int, price: int, quantity: int
    ) -> None:
        if side not in (self.BUY, self.SELL):
            raise ValueError("Side must be BUY or SELL")
        if price <= 0 or quantity <= 0:
            raise ValueError("Price and quantity must be positive")

        head, tail = self.HEADER.unpack_from(self.map, 0)

        if head - tail >= self.capacity:
            raise BufferError("Ring buffer is full")

        offset = self.HEADER.size + (head % self.capacity) * self.slot_size
        self.SLOT.pack_into(
            self.map, offset, order_id, side, price, quantity
        )
        self.HEADER.pack_into(self.map, 0, head + 1, tail)

    def read_order(self) -> dict | None:
        head, tail = self.HEADER.unpack_from(self.map, 0)

        if tail >= head:
            return None

        offset = self.HEADER.size + (tail % self.capacity) * self.slot_size
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
        self.map.close()
        self.file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.close()
