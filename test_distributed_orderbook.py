import requests
import time

def send_order(node_addr, order_type, price, quantity):
    """Send an order to a specific node."""
    print(f"Sending {order_type} order: price={price}, quantity={quantity}")
    response = requests.post(
        f"http://{node_addr}/add_order",
        json={"type": order_type, "price": price, "quantity": quantity},
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
    send_order(leader_node, "bid", 150, 5)
    send_order(leader_node, "ask", 140, 3)

    # Wait for replication
    time.sleep(5)

    # Check order books on all nodes
    for addr in ["127.0.0.1:5000", "127.0.0.1:5001", "127.0.0.1:5002"]:
        print_orderbook(addr)
