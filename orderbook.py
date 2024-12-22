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

  def __init__(self, id: int, side: Side, order_type: OrderType, price: float, quantity: float, id_to_touch = None):
    self.id = id
    self.side = side
    self.order_type = order_type
    self.price = price
    self.quantity = quantity
    self.id_to_touch = id_to_touch # int or None

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

  def get_id_to_touch(self):
    return self.id_to_touch

class TradeElement:

  def __init__(self, id: int, price: float, quantity: float):
    self.id = id
    self.price = price
    self.quantity = quantity


class Trade:

  def __init__(self):
    self.bids = []
    self.asks = []

  def add_bid(self, elem: TradeElement):
    self.bids.append(elem)

  def add_ask(self, elem: TradeElement):
    self.ask.append(elem)


class OrderBook:

  def __init__(self):
    self.bids = SortedDict(lambda x: -x)  #{float : [int]}
    self.asks = SortedDict()
    self.orders = {int : Order}

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

  def can_match(self, order: Order):
    quantity = order.get_quantity()
    side = order.get_side()

  def cancel_order(self, id: int) -> bool:
    order_to_cancel = self.orders[id]
    if order_to_cancel == None:
      return False
    cancel_price = order_to_cancel.get_price()
    cancel_side = order_to_cancel.get_side()
    if cancel_side == Side.bid:
      cancel_level = self.bids[cancel_price]
      if cancel_level == None:
        return False
      cancel_level.remove(id)
      if cancel_level == []:
        self.bids.__delitem__(cancel_price)
    else:
      cancel_level = self.asks[cancel_price]
      if cancel_level == None:
        return False
      cancel_level.remove(id)
      if cancel_level == []:
        self.asks.__delitem__(cancel_price)
    del self.orders[id]
    return True

  def add_order(self, order: Order) -> bool:
    order_type = order.get_type()
    if order_type == OrderType.market:
      quantity_remaining = order.get_quantity()
      if order.get_side() == Side.bid:
        while quantity_remaining > 0.0:
          top_item = self.asks.peektiem(0)  # (float : [int])
          if top_item == None:
            break
          for id in top_item[1]:
            ask = self.orders[id]
            quantity_remaining -= ask.get_quantity()  #add check for remaining < quantity before this

          
    elif order_type == OrderType.limit:
      pass
    elif order_type == OrderType.fillOrKill:
      pass
    elif order_type == OrderType.modify:
      id = order.get_id_to_touch()
      order_to_modify = self.orders[id]
      modified_side = order_to_modify.get_side()
      modified_type = order_to_modify.get_type()
      if order_to_modify.get_side() != modified_side:
        return False
      self.cancel_order(id)
      new_order = Order(id, modified_side, modified_type, order.get_price(), order.get_quantity())
      return self.add_order(new_order)

    elif order_type == OrderType.cancel:
      id = order.get_id()
      return self.cancel_order(id)
    else:
      raise False