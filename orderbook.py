from enum import Enum
from sortedcontainers import SortedDict


class Side(Enum):
  bid = 1
  ask = 2

class OrderType(Enum):
  market = 0
  limit = 1
  fillOrKill = 2
  modify = 3
  cancel = 4


class Order:

  def __init__(self, id: int, side: Side, order_type: OrderType, price: float, quantity: float):
    self.id = id
    self.side = side
    self.order_type = order_type
    self.price = price
    self.quantity = quantity

  def get_id(self):
    return self.id
  
  def get_side(self):
    return self.side

  def get_type(self):
    return self.order_type
  
  def get_price(self):
    return self.price
  
  def get_quantity(self):
    return self.quantity



class OrderBook:

  def __init__(self):
    self.bids = SortedDict(lambda x: -x)
    self.asks = SortedDict()
    self.orders = {int : [Order]}

  def orders_insert(self, order: Order):
    id = order.get_id()
    if id in self.orders:
      raise Exception ("Order ID already exists")
    self.orders[id] = order

  def bids_insert(self, order: Order):
    price = order.get_price()
    if price in self.bids:
      self.bids[price].append(order.get_id())
    else:
      self.bids[price] = [order.get_id()]

  def asks_insert(self, order: Order):
    price = order.get_price()
    if price in self.asks:
      self.asks[price].append(order.get_id())
    else:
      self.asks[price] = [order.get_id()]
