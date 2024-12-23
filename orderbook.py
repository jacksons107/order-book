from enum import Enum
from sortedcontainers import SortedDict


class Side(Enum):
  bid = 1
  ask = 2

class OrderType(Enum):
  market = 0
  limit = 1
  fillOrKill = 2


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

  
class Modify:

  def __init__(self, id: int, price: float, quantity: float):
    self.id = id
    self.price = price
    self.quantity = quantity

  def get_id(self):
    return self.id
  
  def get_price(self):
    return self.price
  
  def get_quantity(self):
    return self.quantity

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
  
  def modify_order(self, modify: Modify) -> bool:
    id = modify.get_id()
    order_to_modify = self.orders[id]
    modified_side = order_to_modify.get_side()
    modified_type = order_to_modify.get_type()
    if order_to_modify.get_side() != modified_side:
      return False
    if self.cancel_order(id) == False:
      return False
    new_order = Order(id, modified_side, modified_type, modify.get_price(), modify.get_quantity())
    self.add_order(new_order)
    return True
  

  def add_order(self, order: Order) -> Trade:
    trade = Trade()
    order_type = order.get_type()
    side = order.get_side()
    
    if order_type == OrderType.market:
      if side == Side.bid and self.asks.__len__() != 0:
        quantity_remaining = order.get_quantity()
        bid_elem = TradeElement(order.get_id(), order.get_price(), quantity_remaining)
        trade.add_bid(bid_elem)
        while quantity_remaining > 0.0 and self.asks.__len__() != 0:
          top_item = self.asks.peektiem(0)  # (float : [int])
          if top_item == None:
            break
          for id in top_item[1]:
            ask = self.orders[id]
            ask_quantity = ask.get_quantity()
            if quantity_remaining >= ask_quantity:
              quantity_remaining -= ask_quantity  
              ask_elem = TradeElement(ask.get_id(), ask.get_price(), ask_quantity)
              trade.add_ask(ask_elem)
              self.cancel_order(ask.get_id())
            else:
              ask_quantity -= quantity_remaining
              ask_elem = TradeElement(ask.get_id(), ask.get_price(), quantity_remaining)
              trade.add_ask(ask_elem)
              modified_ask = Modify(ask.get_id(), ask.get_price(), ask_quantity)
              self.modify_order(modified_ask)
              quantity_remaining = 0.0
        return trade
      elif side == Side.ask and self.bids.__len__() != 0:
        quantity_remaining = order.get_quantity()
        ask_elem = TradeElement(order.get_id(), order.get_price(), quantity_remaining)
        trade.add_ask(ask_elem)
        while quantity_remaining > 0.0 and self.asks.__len__() != 0:
          top_item = self.bids.peektiem(0)  # (float : [int])
          if top_item == None:
            break
          for id in top_item[1]:
            bid = self.orders[id]
            bid_quantity = bid.get_quantity()
            if quantity_remaining >= bid_quantity:
              quantity_remaining -= bid_quantity  
              bid_elem = TradeElement(bid.get_id(), bid.get_price(), bid_quantity)
              trade.add_bid(bid_elem)
              self.cancel_order(bid.get_id())
            else:
              bid_quantity -= quantity_remaining
              bid_elem = TradeElement(ask.get_id(), ask.get_price(), quantity_remaining)
              trade.add_bid(bid_elem)
              modified_bid = Modify(bid.get_id(), bid.get_price(), bid_quantity)
              self.modify_order(modified_bid)
              quantity_remaining = 0.0
        return trade
      else:
        return trade
       
    elif order_type == OrderType.limit:
      pass
    elif order_type == OrderType.fillOrKill:
      pass
    else:
      return trade