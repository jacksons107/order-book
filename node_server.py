import sys
import socket
from threading import Thread
from distributed_orderbook import DistributedOrderBook

def handle_client(client_socket, orderbook):
    try:
        request = client_socket.recv(1024).decode().strip()
        print(f"Received request: {request}")
        
        command, *args = request.split()
        response = None
        print(f"Received command: {command}")
        print(f"Received args: {args}")


        if command == "add_market_order":
            side, quantity = args
            response = orderbook.add_market_order(side, float(quantity))
        elif command == "add_limit_order":
            # print("adding limit")
            side, price, quantity = args
            response = orderbook.add_limit_order(side, float(price), float(quantity))
        elif command == "cancel_order":
            order_id = int(args[0])
            response = orderbook.cancel_order(order_id)
        elif command == "get_state":
            response = orderbook.get_state()
        else:
            response = "ERROR: Unknown command"

        client_socket.sendall(str(response).encode())
    except Exception as e:
        client_socket.sendall(f"ERROR: {e}".encode())
    finally:
        client_socket.close()

def start_server(orderbook, host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # resuseaddr maybe not necessary?
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Node server started at {host}:{port}")

    while True:
        client, _ = server_socket.accept()
        Thread(target=handle_client, args=(client, orderbook)).start()

# if __name__ == "__main__":
#     self_address = "127.0.0.1:8000"
#     peer_addresses = ["127.0.0.1:8001", "127.0.0.1:8002"]
#     orderbook = DistributedOrderBook(self_address, peer_addresses)
#     start_server(orderbook)

if __name__ == "__main__":
    # Read command-line arguments
    host = sys.argv[2]
    self_port = int(sys.argv[4])  # First argument: port of this node
    all_ports = [8000, 8001, 8002]  # Specify all the ports for nodes here
    # host = "127.0.0.1"
    
    # Compute self_address and peer_addresses
    self_address = f"{host}:{self_port}"
    peer_ports = [port for port in all_ports if port != self_port]
    peer_addresses = [f"{host}:{port}" for port in peer_ports]
    
    print(f"Starting node with self_address: {self_address}, peer_addresses: {peer_addresses}")
    
    # Create DistributedOrderBook and start server
    orderbook = DistributedOrderBook(self_address, peer_addresses)
    start_server(orderbook, host, self_port)