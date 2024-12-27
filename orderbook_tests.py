import pytest
from orderbook import OrderBook, Order, Trade, Modify, TradeElement, OrderType, Side

@pytest.fixture
def order_book():
    """Fixture to create a fresh order book for each test."""
    return OrderBook()

def test_add_market_order_empty(order_book):
    """Test if a market order is processed correctly."""
    market_order = Order(0, Side.bid, OrderType.market, 0.0, 100.0)
    trade = order_book.add_order(market_order)
    assert len(order_book.orders) == 0
    assert len(trade.bids) == 0
    assert len(trade.asks) == 0


def test_add_limit_order_empty(order_book):
    """Test if a limit order is processed correctly."""
    limit_order = Order(0, Side.bid, OrderType.limit, 100.0, 100.0)
    trade = order_book.add_order(limit_order)
    assert len(order_book.orders) == 1
    assert len(order_book.bids) == 1
    assert order_book.orders[0] == limit_order
    assert len(trade.bids) == 0
    assert len(trade.asks) == 0


def test_add_market_order_full_fill(order_book):
    """Test if market order is fully filled when possible by one previous order"""
    limit_order = Order(0, Side.bid, OrderType.limit, 100.0, 100.0)
    market_order = Order(1, Side.ask, OrderType.market, 0.0, 100.0)
    order_book.add_order(limit_order)
    assert len(order_book.orders) == 1
    assert len(order_book.bids) == 1
    trade = order_book.add_order(market_order)
    assert len(trade.bids) == 1
    assert len(trade.asks) == 1
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0

def test_add_market_order_partial_fill(order_book):
    """Test if market order is partially filled when possible by one previous order"""
    limit_order = Order(0, Side.bid, OrderType.limit, 100.0, 50.0)
    market_order = Order(1, Side.ask, OrderType.market, 0.0, 100.0)
    order_book.add_order(limit_order)
    assert len(order_book.orders) == 1
    assert len(order_book.bids) == 1
    trade = order_book.add_order(market_order)
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0
    assert len(trade.bids) == 1
    assert len(trade.asks) == 1


def test_add_market_order_leftover(order_book):
    """Test if there is left over limit order after a market order fills"""
    limit_order = Order(0, Side.bid, OrderType.limit, 100.0, 150.0)
    market_order = Order(1, Side.ask, OrderType.market, 0.0, 100.0)
    order_book.add_order(limit_order)
    assert len(order_book.orders) == 1
    assert len(order_book.bids) == 1
    trade = order_book.add_order(market_order)
    assert len(trade.bids) == 1
    assert len(trade.asks) == 1
    assert len(order_book.orders) == 1
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 1

# @pytest.mark.parametrize(
#     "order_type, side, quantity, price, expected_length",
#     [
#         ("market", "buy", 100, None, 1),
#         ("limit", "sell", 50, 150, 1),
#         ("market", "sell", 0, None, 0),  # Invalid order with zero quantity
#     ],
# )
# def test_order_variants(order_book, order_type, side, quantity, price, expected_length):
#     """Test various orders."""
#     order = {"type": order_type, "side": side, "quantity": quantity}
#     if price:
#         order["price"] = price
#     order_book.add_order(order)
#     assert len(order_book.orders) == expected_length

# def test_process_orders(order_book):
#     """Test processing orders (e.g., matching market orders with limit orders)."""
#     limit_order = {"type": "limit", "side": "sell", "quantity": 100, "price": 10}
#     market_order = {"type": "market", "side": "buy", "quantity": 50}

#     order_book.add_order(limit_order)
#     order_book.add_order(market_order)
#     order_book.process_orders()  # Assuming your `OrderBook` has a method for matching orders

#     assert len(order_book.orders) == 1  # Only partially filled limit order remains
#     remaining_order = order_book.orders[0]
#     assert remaining_order["quantity"] == 50  # 100 - 50 market buy

# def test_concurrent_order_handling(order_book):
#     """Test concurrency handling in the order book."""
#     from concurrent.futures import ThreadPoolExecutor

#     def add_orders():
#         for _ in range(100):
#             order_book.add_order({"type": "market", "side": "buy", "quantity": 1})

#     with ThreadPoolExecutor(max_workers=5) as executor:
#         futures = [executor.submit(add_orders) for _ in range(5)]

#         for future in futures:
#             future.result()

#     assert len(order_book.orders) == 500  # 100 orders x 5 threads

