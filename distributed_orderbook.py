from pysyncobj import SyncObj, replicated
from pysyncobj.batteries import ReplCounter
from orderbook import OrderBook, Modify, Order, OrderType, Side


class DistributedOrderBook(OrderBook, SyncObj):

  def __init__(self, self_node, other_nodes):
    SyncObj.__init__(self, self_node, other_nodes)
    OrderBook.__init__(self)
    self.id_num = ReplCounter()
    self.id_num.set(0, synch=True)

  def get_state(self):
    return super().get_state()

  @replicated
  def get_id(self):
    self.id_num.inc(synch=True)
    return self.id_num

  @replicated
  def add_market_order(self, side: str, quantity: float):
    if side == "bid":
      order_side = Side.bid
    elif side == "ask":
      order_side = Side.ask
    order = Order(self.get_id(), order_side, OrderType.market, 0.0, quantity)
    return super().add_order(order)
  
  @replicated
  def add_limit_order(self, side: str, price: float, quantity: float):
    if side == "bid":
      order_side = Side.bid
    elif side == "ask":
      order_side = Side.ask
    order = Order(self.get_id(), order_side, OrderType.limit, price, quantity)
    return super().add_order(order)
  
  @replicated
  def add_fillOrKill_order(self, side: str, price: float, quantity: float):
    if side == "bid":
      order_side = Side.bid
    elif side == "ask":
      order_side = Side.ask
    order = Order(self.get_id(), order_side, OrderType.fillOrKill, price, quantity)
    return super().add_order(order)
  
  @replicated
  def modify_order(self, id: int, price: float, quantity: float):
    modify = Modify(id, price, quantity)
    return super().modify_order(modify)
  
  @replicated
  def cancel_order(self, id):
    return super().cancel_order(id)
