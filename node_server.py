import socket
from threading import Thread
from distributed_orderbook import DistributedOrderBook

def handle_client(client_socket, orderbook):
    try:
        request = client_socket.recv(1024).decode().strip()
        print(f"Received request: {request}")
        
        command, *args = request.split()
        response = None

        if command == "add_market_order":
            side, quantity = args
            response = orderbook.add_market_order(side, float(quantity))
        elif command == "add_limit_order":
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

def start_server(orderbook, host="127.0.0.1", port=8000):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(5)
    print(f"Node server started at {host}:{port}")

    while True:
        client, _ = server_socket.accept()
        Thread(target=handle_client, args=(client, orderbook)).start()

if __name__ == "__main__":
    self_address = "127.0.0.1:8000"
    peer_addresses = ["127.0.0.1:8001"]
    orderbook = DistributedOrderBook(self_address, peer_addresses)
    start_server(orderbook)
