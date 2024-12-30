import subprocess
import time

def start_node(self_addr, partner_addrs):
    """Start a single node in a new subprocess."""
    args = [
        "python3", "distributed_node.py", 
        "--self_addr", self_addr,
        "--partner_addrs"
    ] + partner_addrs
    return subprocess.Popen(args)

if __name__ == "__main__":
    # Define node addresses
    node_addrs = [
        "127.0.0.1:5000",
        "127.0.0.1:5001",
        "127.0.0.1:5002"
    ]

    # Start all nodes
    processes = []
    try:
        for self_addr in node_addrs:
            partner_addrs = [addr for addr in node_addrs if addr != self_addr]
            proc = start_node(self_addr, partner_addrs)
            processes.append(proc)
            time.sleep(1)  # Delay to avoid race conditions during startup
        
        print("All nodes are running. Press Ctrl+C to stop.")

        # Keep the main process alive
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Shutting down all nodes...")
        for proc in processes:
            proc.terminate()
        for proc in processes:
            proc.wait()
