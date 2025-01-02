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
    n = 0
    old_value = -1
    while True:
        # time.sleep(0.005)
        time.sleep(0.5)
        # if o.getCounter() != old_value:
        #     old_value = o.getCounter()
        #     print(old_value)
        if o._getLeader() is None:
            continue
        # if n < 2000:
        if n < 20:
            o.add_limit_order("bid", 100.0, 10.0)
            o.get_state()
        n += 1
        # if n % 200 == 0:
        # if True:
        #    print('Counter value:', o.getCounter(), o._getLeader(), o._getRaftLogSize(), o._getLastCommitIndex())