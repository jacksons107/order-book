import subprocess

def start_node(script, port, peers):
    args = [
        "python3", script, 
        "--host", "127.0.0.1", 
        "--port", str(port), 
        "--peers", ",".join(peers)
    ]
    return subprocess.Popen(args)

if __name__ == "__main__":
    node_ports = [8000, 8001, 8002]
    processes = []
    
    for i, port in enumerate(node_ports):
        peers = [f"127.0.0.1:{p}" for p in node_ports if p != port]
        proc = start_node("node_server.py", port, peers)
        processes.append(proc)
    
    try:
        for proc in processes:
            proc.wait()
    except KeyboardInterrupt:
        for proc in processes:
            proc.terminate()
