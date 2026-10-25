# ChronosMatch

ChronosMatch is a Python-based prototype of a high-frequency trading
engine. It connects a memory-mapped ring buffer to an order book
that matches buy and sell orders.

## Features

- Price-time priority order matching
- Memory-mapped order ring buffer
- Pipeline connecting queued orders to the matching engine
- Trade generation and best bid/ask tracking
- Automated unit and integration tests

## Architecture

1. Orders are written into the ring buffer.
2. The pipeline reads queued orders.
3. Orders are submitted to the matching engine.
4. Matching orders generate trades.
5. The order book maintains unmatched orders.

## Requirements

- Python 3.10 or newer recommended

The project uses Python standard-library modules for its current
demo and tests.

## Run the Demo

```bash
python3 main.py
```

## Run Tests

```bash
python3 -m unittest discover -s tests -v
```

## Current Status

This is a prototype for learning and demonstrating order matching
and buffer-to-engine integration. It is not production-ready
trading infrastructure.
