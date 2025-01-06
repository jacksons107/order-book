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
        print("no leader - testing node")
        time.sleep(0.5)

    o.add_limit_order("bid", 100.0, 10.0)
    o.get_state()
    print("test node done")
    while True:
        #  print("test node done")
         time.sleep(5)