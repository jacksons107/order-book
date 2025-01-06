from distributed_orderbook import DistributedOrderBook
import sys
import time


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('Usage: %s self_port partner1_port partner2_port ...' % sys.argv[0])
        sys.exit(-1)

    port = int(sys.argv[1])
    partners = ['localhost:%d' % int(p) for p in sys.argv[2:]]
    o = DistributedOrderBook('localhost:%d' % port, partners)
    
    while o._getLeader() is None:
        print("no leader - partner node")
        time.sleep(0.5)

    while True:
      print(f"Node: {port}")
      o.get_state()
      time.sleep(3)