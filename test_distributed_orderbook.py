import requests
import time


def send_market_order(node_addr, side: str, quantity: float):
  print(f"Sending market order: side={side}, quantity={quantity}")
  response = requests.post(
    f"http://{node_addr}/add_market_order",
    json={"side": side, "quantity": quantity},
  )
  if response.ok:
    print(f"Order successfully added on node {node_addr}.")
  else:
    print(f"Failed to add order on node {node_addr}: {response.status_code}")

def send_limit_order(node_addr, side: str, price: float, quantity: float):
  print(f"Sending limit order: side={side}, price={price}, quantity={quantity}")
  response = requests.post(
    f"http://{node_addr}/add_limit_order",
    json={"side": side, "price": price, "quantity": quantity},
  )
  if response.ok:
    print(f"Order successfully added on node {node_addr}.")
  else:
    print(f"Failed to add order on node {node_addr}: {response.status_code}")

def send_fillOrKill_order(node_addr, side: str, price: float, quantity: float):
  print(f"Sending fillOrKill order: side={side}, price={price}, quantity={quantity}")
  response = requests.post(
    f"http://{node_addr}/add_fillOrKill_order",
    json={"side": side, "price": price, "quantity": quantity},
  )
  if response.ok:
    print(f"Order successfully added on node {node_addr}.")
  else:
    print(f"Failed to add order on node {node_addr}: {response.status_code}")

def print_orderbook(node_addr):
    """Print the order book state from a specific node."""
    response = requests.get(f"http://{node_addr}/get_orderbook")
    if response.ok:
        orderbook = response.json()
        print(f"Order book on {node_addr}: {orderbook}")
    else:
        print(f"Failed to fetch order book from node {node_addr}: {response.status_code}")

if __name__ == "__main__":
    # Wait for cluster to stabilize
    print("Waiting for nodes to stabilize...")
    time.sleep(10)

    leader_node = "127.0.0.1:5000"  # Adjust as needed

    # Add some orders
    print_orderbook(leader_node)
    send_limit_order(leader_node, "ask", 150.0, 10.0)
    print_orderbook(leader_node)
    send_limit_order(leader_node, "ask", 100.0, 10.0)
    print_orderbook(leader_node)
    send_fillOrKill_order(leader_node, "bid", 140.0, 5)
    print_orderbook(leader_node)
    send_market_order(leader_node, "bid", 10.0)
    print_orderbook(leader_node)

    # Wait for replication
    time.sleep(5)

    # Check order books on all nodes
    for addr in ["127.0.0.1:5000", "127.0.0.1:5001", "127.0.0.1:5002"]:
        print_orderbook(addr)
