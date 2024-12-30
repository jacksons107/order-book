import argparse
import time
from distributed_orderbook import DistributedOrderBook

def run_node(self_addr, partner_addrs):
    node = DistributedOrderBook(self_addr=self_addr, partner_addrs=partner_addrs)

    print(f"Node {self_addr} started and awaiting commands...")
    try:
        # Keep the node running until interrupted
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"Node {self_addr} shutting down...")
        node.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DistributedOrderBook Node")
    parser.add_argument("--self_addr", required=True, help="Address of this node")
    parser.add_argument("--partner_addrs", nargs="+", required=True, help="Addresses of other nodes")
    args = parser.parse_args()

    run_node(args.self_addr, args.partner_addrs)
