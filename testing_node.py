from distributed_orderbook import DistributedOrderBook
import sys
import time

class Trader():
    def __init__(self, port):
        self.order_num = 0
        self.port = port

    def inc_order_num(self):
      self.order_num += 1

    def get_order_num(self):
      return self.order_num
    
    def get_port(self):
      return self.port
    
    def get_order_id(self):
      self.inc_order_num()
      order_num = self.get_order_num()
      port = self.get_port()
      return f"{port}-{order_num}"


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: %s self_port partner1_port partner2_port ...' % sys.argv[0])
        sys.exit(-1)

    port = int(sys.argv[1])
    partners = ['localhost:%d' % int(p) for p in sys.argv[2:]]
    o = DistributedOrderBook('localhost:%d' % port, partners)
    
    while o._getLeader() is None:
        print("no leader - testing node")
        time.sleep(0.5)
    trader = Trader(port)

    o.add_limit_order(trader.get_order_id(), "bid", 100.0, 10.0)
    time.sleep(6)
    print(f"Test node: {port}")
    o.get_state()
    o.add_market_order(trader.get_order_id(), "ask", 5.0)
    time.sleep(3)
    print(f"Test node: {port}")
    o.get_state()
    while True:
        #  print("test node done")
        # print(f"Test node: {port}")
        # o.get_state()
        time.sleep(3)