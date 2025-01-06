from pysyncobj import SyncObj, replicated
from pysyncobj.batteries import ReplCounter
from orderbook import OrderBook, Modify, Order, OrderType, Side
from pysyncobj import SyncObjConf
import logging


logging.basicConfig(level=logging.DEBUG)

class DistributedOrderBook(OrderBook, SyncObj):

  def __init__(self, self_node, other_nodes):
    conf = SyncObjConf(fullDumpFile='/tmp/dump.log')
    SyncObj.__init__(self, self_node, other_nodes, conf=conf)
    OrderBook.__init__(self)
    # self.port = self_node
    # self.order_num = 0

    # self.id_num = ReplCounter()
    # self.id_num.set(0, synch=True)
    # self.is_initialized = False
    # print("DistributedOrderBook initialized.")

  # def initialize_state(self):
  #   # This method can be called later to safely set the state
  #   if not self.is_initialized:
  #       self.id_num.set(0, synch=True)
  #       self.is_initialized = True

  # @replicated
  # def add_test(self):
  #     print("Test method executed")

  def get_status(self):
    return super().getStatus()


  def get_state(self):
    # print("Getting state")
    print(super().get_state())
    # return super().get_state()

  # def inc_order_num(self):
  #   self.order_num += 1

  # def get_order_num(self):
  #   return self.order_num
  
  # def get_port(self):
  #   return self.port
  
  # def get_order_id(self):
  #   self.inc_order_num()
  #   order_num = self.get_order_num()
  #   port = self.get_port()
  #   return f"{port}-{order_num}"


  # @replicated
  # def get_id(self):
  #   self.id_num.inc(synch=True)
  #   return self.id_num

  # @replicated
  # def get_id(self):
  #   return super().get_id()

  @replicated
  def add_market_order(self, id: str, side: str, quantity: float):
    if side == "bid":
      order_side = Side.bid
    elif side == "ask":
      order_side = Side.ask
    order = Order(id, order_side, OrderType.market, 0.0, quantity)
    return super().add_order(order)
  
  @replicated
  def add_limit_order(self, id: str, side: str, price: float, quantity: float):
    if side == "bid":
      order_side = Side.bid
    elif side == "ask":
      order_side = Side.ask
    order = Order(id, order_side, OrderType.limit, price, quantity)
    return super().add_order(order)
  
  @replicated
  def add_fillOrKill_order(self, id: str, side: str, price: float, quantity: float):
    if side == "bid":
      order_side = Side.bid
    elif side == "ask":
      order_side = Side.ask
    order = Order(id, order_side, OrderType.fillOrKill, price, quantity)
    return super().add_order(order)
  
  @replicated
  def modify_order(self, id: str, price: float, quantity: float):
    modify = Modify(id, price, quantity)
    return super()._modify_order(modify)
  
  @replicated
  def cancel_order(self, id: str):
    return super()._cancel_order(id)
