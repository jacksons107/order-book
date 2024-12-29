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

  # def add_bid(self, elem: TradeElement):
  #   self.bids.append(elem)

  # def add_ask(self, elem: TradeElement):
  #   self.asks.append(elem)


class OrderBook:

  def __init__(self):
    self.bids = SortedDict(lambda x: -x)  #{float : [[int], float]}
    # self._bids_reversed = SortedDict()
    # self.bids = self._bids_reversed.__reversed__()
    self.asks = SortedDict()
    self.orders = {} # {int : Order}
    self.trades = []

  def get_state(self):
    return {"bids" : self.bids, "asks" : self.asks, "trades" : self.trades}

  def orders_insert(self, order: Order):
    id = order.get_id()
    if id in self.orders:
      raise Exception ("Order ID already exists")
    self.orders[id] = order


  def bids_insert(self, order: Order):
    price = order.get_price()
    if price in self.bids:
      self.bids[price][0].append(order.get_id())
      self.bids[price][1] += order.get_quantity()
    else:
      self.bids[price] = [[order.get_id()], order.get_quantity()]
      # self._bids_reversed[price] = [[order.get_id()], order.get_quantity()]
      # self.bids = self._bids_reversed.__reversed__()

  def asks_insert(self, order: Order):
    price = order.get_price()
    if price in self.asks:
      self.asks[price][0].append(order.get_id())
      self.asks[price][1] += order.get_quantity()
    else:
      self.asks[price] = [[order.get_id()], order.get_quantity()]

  def cancel_order(self, id: int) -> bool:
    order_to_cancel = self.orders[id]
    if order_to_cancel == None:
      return False
    cancel_price = order_to_cancel.get_price()
    cancel_side = order_to_cancel.get_side()
    cancel_quantity = order_to_cancel.get_quantity()
    if cancel_side == Side.bid:
      cancel_level = self.bids[cancel_price]  # [[int], float]
      if cancel_level == None:
        return False
      cancel_level[0].remove(id)
      cancel_level[1] -= cancel_quantity
      if cancel_level[1] == 0:
        self.bids.__delitem__(cancel_price)
    else:
      cancel_level = self.asks[cancel_price]  # [[int], float]
      if cancel_level == None:
        return False
      cancel_level[0].remove(id)
      cancel_level[1] -= cancel_quantity
      if cancel_level[1] == 0:
        self.asks.__delitem__(cancel_price)
    del self.orders[id]
    return True
  
  def modify_order(self, modify: Modify) -> bool:
    id = modify.get_id()
    order_to_modify = self.orders[id]
    modified_side = order_to_modify.get_side()
    modified_type = order_to_modify.get_type()
    if self.cancel_order(id) == False:
      return False
    new_order = Order(id, modified_side, modified_type, modify.get_price(), modify.get_quantity())
    self.add_order(new_order)
    return True

  def fill_order(self, side: Side, quantity_remaining: float): # -> (float, [TradeElement])
    '''
    - attempts to fill quantity_remaining worth from best price level on opposite side 
    - removes orders from bids/asks that are used to fill the trade
    - deletes price level if empty after orders are used for trade
    - returns tuple with quantity_remaining after filling and list of trade elements
    '''
    if side == Side.bid:
      top_level = self.asks.peekitem(0)  # (float : [[int], float])
    else:
      top_level = self.bids.peekitem(0)  # (float : [[int], float])
    if top_level == None:
      return None
    fills = []
    for id in top_level[1][0]:
      fill = self.orders[id]
      fill_quantity = fill.get_quantity()
      if quantity_remaining >= fill_quantity:
        quantity_remaining -= fill_quantity  
        fill_elem = TradeElement(fill.get_id(), fill.get_price(), fill_quantity)
        fills.append(fill_elem)
        self.cancel_order(fill.get_id())
      else:
        fill_quantity -= quantity_remaining
        fill_elem = TradeElement(fill.get_id(), fill.get_price(), quantity_remaining)
        fills.append(fill_elem)
        modified_fill = Modify(fill.get_id(), fill.get_price(), fill_quantity)
        self.modify_order(modified_fill)
        quantity_remaining = 0.0
        break

    return (quantity_remaining, fills)
  
  def can_fully_fill(self, side: Side, price: float, quantity_remaining: float) -> bool:
    if side == Side.bid:
      opposite_book = self.asks
    else:
      opposite_book = self.bids
    if opposite_book == None:
      return False
    for level in opposite_book.items(): # level : (float : [[int], float])
      if quantity_remaining <= 0:
        return True
      if side == Side.bid and level[0] > price:
        return False
      if side == Side.ask and level[0] < price:
        return False
      quantity_remaining -= level[1][1]


    return quantity_remaining <= 0
  

  def add_trade(self, trade: Trade):
    if len(trade.bids) > 0 and len(trade.asks) > 0:
      self.trades.append(trade)

  

  def add_order(self, order: Order) -> Trade:
    trade = Trade()
    order_type = order.get_type()
    side = order.get_side()
    
    if order_type == OrderType.market:
      if side == Side.bid and len(self.asks) != 0:
        quantity_remaining = order.get_quantity()
        # bid_elem = TradeElement(order.get_id(), order.get_price(), order.get_quantity())
        # trade.bids.append(bid_elem)
        while quantity_remaining > 0.0 and len(self.asks) != 0:
          fills = self.fill_order(side, quantity_remaining) #(float, [TradeElement])
          quantity_filled = quantity_remaining - fills[0]
          quantity_remaining = fills[0]
          trade.asks += fills[1]
          bid_elem = TradeElement(order.get_id(), fills[1][0].price, quantity_filled)
          trade.bids.append(bid_elem)
     
        self.add_trade(trade)
        return trade

      elif side == Side.ask and len(self.bids) != 0:
        quantity_remaining = order.get_quantity()
        # ask_elem = TradeElement(order.get_id(), order.get_price(), quantity_remaining)
        # trade.asks.append(ask_elem)
        while quantity_remaining > 0.0 and len(self.bids) != 0:
          fills = self.fill_order(side, quantity_remaining) #(float, [TradeElement])
          quantity_filled = quantity_remaining - fills[0]
          quantity_remaining = fills[0]
          trade.bids += fills[1]
          ask_elem = TradeElement(order.get_id(), fills[1][0].price, quantity_filled)
          trade.asks.append(ask_elem)
        self.add_trade(trade)
        return trade

      else:

        self.add_trade(trade)
        return trade
       
    elif order_type == OrderType.limit:
      if side == Side.bid and len(self.asks) != 0:
        price = order.get_price()
        top_level = self.asks.peekitem(0) # (float : [[int], float])
        if top_level[0] > price:
          self.orders_insert(order)
          self.bids_insert(order)
          self.add_trade(trade)
          return trade
        else:
          quantity_remaining = order.get_quantity()
          while quantity_remaining > 0.0 and len(self.asks) != 0 and top_level[0] <= price:
            fills = self.fill_order(side, quantity_remaining) #(float, [TradeElement])
            quantity_filled = quantity_remaining - fills[0]
            quantity_remaining = fills[0]
            trade.asks += fills[1]
            bid_elem = TradeElement(order.get_id(), top_level[0], quantity_filled)
            trade.bids.append(bid_elem)
            if len(self.asks) != 0:
              top_level = self.asks.peekitem(0) # (float : [[int], float])
          # bid_elem = TradeElement(order.get_id(), order.get_price(), order.get_quantity() - quantity_remaining)
          # print(bid_elem.price)
          # trade.bids.append(bid_elem)
          if quantity_remaining > 0.0:
            bid_remaining = Order(order.get_id(), side, order_type, price, quantity_remaining)
            self.bids_insert(bid_remaining)
            self.orders_insert(bid_remaining)

          self.add_trade(trade)
          return trade

      elif side == Side.ask and len(self.bids) != 0:
        price = order.get_price()
        top_level = self.bids.peekitem(0) # (float : [[int], float])
        if top_level[0] < price:
          self.orders_insert(order)
          self.asks_insert(order)
          self.add_trade(trade)
          self.add_trade(trade)
          return trade 
        else:
          quantity_remaining = order.get_quantity()
          while quantity_remaining > 0.0 and len(self.bids) != 0 and top_level[0] >= price:
            fills = self.fill_order(side, quantity_remaining) #(float, [TradeElement])
            quantity_filled = quantity_remaining - fills[0]
            quantity_remaining = fills[0]
            trade.bids += fills[1]
            ask_elem = TradeElement(order.get_id(), top_level[0], quantity_filled)
            trade.asks.append(ask_elem)
            if len(self.bids) != 0:
              top_level = self.bids.peekitem(0) # (float : [[int], float])
          # ask_elem = TradeElement(order.get_id(), order.get_price(), order.get_quantity() - quantity_remaining)
          # print(ask_elem.price)
          # trade.asks.append(ask_elem)
          if quantity_remaining > 0.0:
            ask_remaining = Order(order.get_id(), side, order_type, price, quantity_remaining)
            self.asks_insert(ask_remaining)
            self.orders_insert(ask_remaining)

          self.add_trade(trade)
          return trade

      else:
        self.orders_insert(order)
        if side == Side.bid:
          self.bids_insert(order)
        else:
          self.asks_insert(order)
        self.add_trade(trade)
        return trade

    elif order_type == OrderType.fillOrKill:
      price = order.get_price()
      if not self.can_fully_fill(side, price, order.get_quantity()):
        self.add_trade(trade)
        return trade
      if side == Side.bid:
        top_level = self.asks.peekitem(0) # (float : [[int], float])
        quantity_remaining = order.get_quantity()
        while quantity_remaining > 0.0 and len(self.asks) != 0 and top_level[0] <= price:
          fills = self.fill_order(side, quantity_remaining) #(float, [TradeElement])
          quantity_filled = quantity_remaining - fills[0]
          quantity_remaining = fills[0]
          trade.asks += fills[1]
          bid_elem = TradeElement(order.get_id(), top_level[0], quantity_filled)
          trade.bids.append(bid_elem)
          if len(self.asks) != 0:
            top_level = self.asks.peekitem(0) # (float : [[int], float])

        self.add_trade(trade)
        return trade

      else:
          top_level = self.bids.peekitem(0) # (float : [[int], float])
          quantity_remaining = order.get_quantity()
          while quantity_remaining > 0.0 and len(self.bids) != 0 and top_level[0] >= price:
            fills = self.fill_order(side, quantity_remaining) #(float, [TradeElement])
            quantity_filled = quantity_remaining - fills[0]
            quantity_remaining = fills[0]
            trade.bids += fills[1]
            ask_elem = TradeElement(order.get_id(), top_level[0], quantity_filled)
            trade.asks.append(ask_elem)
            if len(self.bids) != 0:
              top_level = self.bids.peekitem(0) # (float : [[int], float])

          self.add_trade(trade)
          return trade


    else:

      self.add_trade(trade)
      return trade
