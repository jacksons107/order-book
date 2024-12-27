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


def test_cancel_order(order_book):
    """Test if a limit order is cancelled correctly."""
    limit_order = Order(0, Side.bid, OrderType.limit, 100.0, 100.0)
    order_book.add_order(limit_order)
    cancelled = order_book.cancel_order(limit_order.get_id())
    assert len(order_book.orders) == 0
    assert len(order_book.bids) == 0
    assert cancelled == True


def test_modify_order(order_book):
    limit_order = Order(0, Side.bid, OrderType.limit, 100.0, 100.0)
    modification = Modify(limit_order.get_id(), 200.0, 50.0)
    order_book.add_order(limit_order)
    assert order_book.orders[0].get_price() == 100.0
    assert order_book.orders[0].get_quantity() == 100.0
    order_book.modify_order(modification)
    assert len(order_book.orders) == 1
    assert len(order_book.bids) == 1
    assert order_book.orders[0].get_price() == 200.0
    assert order_book.orders[0].get_quantity() == 50.0
    # print(order_book.bids[200.0])

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


def test_add_market_order_combo_fill(order_book):
    """Fill market order with multiple limit orders"""
    limit_order_1 = Order(0, Side.bid, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.bid, OrderType.limit, 100.0, 50.0)
    market_order = Order(2, Side.ask, OrderType.market, 0.0, 100.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    assert len(order_book.orders) == 2
    assert len(order_book.bids) == 1
    assert len(order_book.bids[100.0][0]) == 2
    trade = order_book.add_order(market_order)
    assert len(trade.bids) == 2
    assert len(trade.asks) == 2
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0
    # for elem in trade.asks:
    #   print((elem.price, elem.quantity))


def test_add_market_order_combo_fill_leftover(order_book):
    """Fill market order with multiple limit orders and some left over"""
    limit_order_1 = Order(0, Side.bid, OrderType.limit, 100.0, 75.0)
    limit_order_2 = Order(1, Side.bid, OrderType.limit, 100.0, 50.0)
    market_order = Order(2, Side.ask, OrderType.market, 0.0, 100.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    assert len(order_book.orders) == 2
    assert len(order_book.bids) == 1
    assert len(order_book.bids[100.0][0]) == 2
    trade = order_book.add_order(market_order)
    assert len(trade.bids) == 2
    assert len(trade.asks) == 2
    assert len(order_book.orders) == 1
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 1
    # for elem in trade.asks:
    #   print((elem.price, elem.quantity))

def test_bids_ordering(order_book):
    """Make sure bids is actually ordered correctly"""
    limit_order_1 = Order(0, Side.bid, OrderType.limit, 100.0, 75.0)
    limit_order_2 = Order(1, Side.bid, OrderType.limit, 50.0, 50.0)
    limit_order_3 = Order(2, Side.bid, OrderType.limit, 75.0, 100.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    order_book.add_order(limit_order_3)
    # print(order_book.bids)


def test_asks_ordering(order_book):
    """Make sure asks is actually ordered"""
    limit_order_1 = Order(0, Side.ask, OrderType.limit, 100.0, 75.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 50.0, 50.0)
    limit_order_3 = Order(2, Side.ask, OrderType.limit, 75.0, 100.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    order_book.add_order(limit_order_3)
    # print(order_book.asks)


def test_add_limit_immediate_fill(order_book):
    """Add a limit order that should be immediately filled"""
    limit_order_1 = Order(0, Side.bid, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 100.0, 50.0)
    order_book.add_order(limit_order_1)
    assert len(order_book.bids) == 1
    trade = order_book.add_order(limit_order_2)
    assert len(trade.bids) == 1
    assert len(trade.asks) == 1
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0


def test_add_limit_no_fill(order_book):
    """Add a limit order that should not be filled"""
    limit_order_1 = Order(0, Side.bid, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 200.0, 50.0)
    order_book.add_order(limit_order_1)
    assert len(order_book.bids) == 1
    trade = order_book.add_order(limit_order_2)
    assert len(trade.bids) == 0
    assert len(trade.asks) == 0
    assert len(order_book.orders) == 2
    assert len(order_book.asks) == 1
    assert len(order_book.bids) == 1


def test_add_limit_partial_fill(order_book):
    """Add a limit order that should be partially filled and remain on the book"""
    limit_order_1 = Order(0, Side.bid, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 100.0, 100.0)
    order_book.add_order(limit_order_1)
    assert len(order_book.bids) == 1
    trade = order_book.add_order(limit_order_2)
    assert len(trade.bids) == 1
    assert len(trade.asks) == 1
    assert len(order_book.orders) == 1
    assert len(order_book.asks) == 1
    assert len(order_book.bids) == 0


def test_add_limit_combo_fill(order_book):
    """Add a limit order that should be filled by multiple opposing orders of the same price level"""
    limit_order_1 = Order(0, Side.ask, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 100.0, 100.0)
    limit_order_3 = Order(2, Side.bid, OrderType.limit, 100.0, 150.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    trade = order_book.add_order(limit_order_3)
    assert len(trade.bids) == 2
    assert len(trade.asks) == 2
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0


def test_add_limit_combo_fill_multi_level(order_book):
    """Add a limit order that should be filled by multiple opposing orders of the different price levels"""
    limit_order_1 = Order(0, Side.bid, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.bid, OrderType.limit, 150.0, 100.0)
    limit_order_3 = Order(2, Side.ask, OrderType.limit, 100.0, 150.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    trade = order_book.add_order(limit_order_3)
    assert len(trade.bids) == 2
    assert len(trade.asks) == 2
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0
    # for elem in trade.asks:
    #   print((elem.price, elem.quantity))



def test_add_limit_combo_fill_multi_level_stop(order_book):
    """Add a limit order that should be filled by multiple opposing orders of the different price levels and stop at a unacceptable price"""
    limit_order_1 = Order(0, Side.bid, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.bid, OrderType.limit, 150.0, 75.0)
    limit_order_3 = Order(2, Side.bid, OrderType.limit, 50.0, 150.0)
    limit_order_4 = Order(3, Side.ask, OrderType.limit, 100.0, 150.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    order_book.add_order(limit_order_3)
    trade = order_book.add_order(limit_order_4)
    assert len(trade.bids) == 2
    assert len(trade.asks) == 2
    assert len(order_book.orders) == 2
    assert len(order_book.asks) == 1
    assert len(order_book.bids) == 1
    # for elem in trade.asks:
    #   print((elem.price, elem.quantity))
    # print(order_book.asks)


def test_add_fok_kill_quantity(order_book):
    """Add a fillOrKill order that cannot be fully filled because of quantity"""
    limit_order = Order(0, Side.ask, OrderType.limit, 100.0, 50.0)
    fok_order = Order(1, Side.bid, OrderType.fillOrKill, 100.0, 100.0)
    order_book.add_order(limit_order)
    trade = order_book.add_order(fok_order)
    assert len(trade.bids) == 0
    assert len(trade.asks) == 0
    assert len(order_book.orders) == 1
    assert len(order_book.asks) == 1
    assert len(order_book.bids) == 0


def test_add_fok_kill_price(order_book):
    """Add a fillOrKill order that cannot be fully filled because of price"""
    limit_order = Order(0, Side.ask, OrderType.limit, 100.0, 1000.0)
    fok_order = Order(1, Side.bid, OrderType.fillOrKill, 50.0, 100.0)
    order_book.add_order(limit_order)
    trade = order_book.add_order(fok_order)
    assert len(trade.bids) == 0
    assert len(trade.asks) == 0
    assert len(order_book.orders) == 1
    assert len(order_book.asks) == 1
    assert len(order_book.bids) == 0


def test_add_fok_kill_quantity_multilevel(order_book):
    """Add a fillOrKill order that cannot be fully filled because of quantity over multiple price levels"""
    limit_order_1 = Order(0, Side.ask, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 50.0, 50.0)
    fok_order = Order(2, Side.bid, OrderType.fillOrKill, 100.0, 150.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    trade = order_book.add_order(fok_order)
    assert len(trade.bids) == 0
    assert len(trade.asks) == 0
    assert len(order_book.orders) == 2
    assert len(order_book.asks) == 2
    assert len(order_book.bids) == 0


def test_add_fok_kill_price_multilevel(order_book):
    """Add a fillOrKill order that cannot be fully filled because of price over multiple price levels"""
    limit_order_1 = Order(0, Side.ask, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 150.0, 100.0)
    fok_order = Order(2, Side.bid, OrderType.fillOrKill, 100.0, 150.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    trade = order_book.add_order(fok_order)
    assert len(trade.bids) == 0
    assert len(trade.asks) == 0
    assert len(order_book.orders) == 2
    assert len(order_book.asks) == 2
    assert len(order_book.bids) == 0


def test_add_fok_fill(order_book):
    """Add a fillOrKill order that is filled by one opposing order"""
    limit_order = Order(0, Side.ask, OrderType.limit, 100.0, 100.0)
    fok_order = Order(1, Side.bid, OrderType.fillOrKill, 100.0, 100.0)
    order_book.add_order(limit_order)
    trade = order_book.add_order(fok_order)
    assert len(trade.bids) == 1
    assert len(trade.asks) == 1
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0


def test_add_fok_fill_multiple(order_book):
    """Add a fillOrKill order that is filled by one multiple orders at the same price level"""
    limit_order_1 = Order(0, Side.ask, OrderType.limit, 100.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 100.0, 50.0)
    fok_order = Order(2, Side.bid, OrderType.fillOrKill, 100.0, 100.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    trade = order_book.add_order(fok_order)
    assert len(trade.bids) == 2
    assert len(trade.asks) == 2
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0


def test_add_fok_fill_multilevel(order_book):
    """Add a fillOrKill order that is filled by one multiple orders at the multiple price levels"""
    limit_order_1 = Order(0, Side.ask, OrderType.limit, 50.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 100.0, 50.0)
    fok_order = Order(2, Side.bid, OrderType.fillOrKill, 100.0, 100.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    trade = order_book.add_order(fok_order)
    assert len(trade.bids) == 2
    assert len(trade.asks) == 2
    assert len(order_book.orders) == 0
    assert len(order_book.asks) == 0
    assert len(order_book.bids) == 0


def test_add_fok_fill_multilevel_leftover(order_book):
    """Add a fillOrKill order that is filled by one multiple orders at the multiple price levels with some leftover"""
    limit_order_1 = Order(0, Side.ask, OrderType.limit, 50.0, 50.0)
    limit_order_2 = Order(1, Side.ask, OrderType.limit, 100.0, 75.0)
    fok_order = Order(2, Side.bid, OrderType.fillOrKill, 100.0, 100.0)
    order_book.add_order(limit_order_1)
    order_book.add_order(limit_order_2)
    trade = order_book.add_order(fok_order)
    assert len(trade.bids) == 2
    assert len(trade.asks) == 2
    assert len(order_book.orders) == 1
    assert len(order_book.asks) == 1
    assert len(order_book.bids) == 0