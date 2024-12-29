from pysyncobj import SyncObj, replicated
from orderbook import OrderBook


class DistributedOrderBook(OrderBook, SyncObj):

  def __init__(self, self_node, other_nodes):
    SyncObj.__init__(self, self_node, other_nodes)
    OrderBook.__init__(self)

  @replicated
  def add_order(self, order):
    return super().add_order(order)
  
  @replicated
  def modify_order(self, modify):
    return super().modify_order(modify)
  
  @replicated
  def cancel_order(self, id):
    return super().cancel_order(id)