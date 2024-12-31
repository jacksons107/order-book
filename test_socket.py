import socket

def send_request(host, port, message):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect((host, port))
        sock.sendall(message.encode())
        response = sock.recv(4096).decode()
        print(f"Response: {response}")

if __name__ == "__main__":
    host = "127.0.0.1"
    port = 8000  # Connect to one of the node servers

    # Test commands
    send_request(host, port, "add_limit_order ask 100.0 5.0")
    send_request(host, port, "get_state")
