import subprocess

def launch_raft_nodes(script_path):
    """
    Launch three instances of the PySyncObj-based Raft script with different ports.

    Args:
        script_path (str): Path to the Python script implementing the Raft counter.
    """
    # Define the ports for each node
    nodes = [
        ("5000", ["5001", "5002"]),
        ("5001", ["5000", "5002"]),
        ("5002", ["5000", "5001"]),
    ]

    processes = []

    try:
        # Launch each node as a separate subprocess
        for node_port, partner_ports in nodes:
            cmd = [
                "python", script_path,
                node_port,
            ] + partner_ports
            print(f"Launching node on port {node_port} with partners {partner_ports}...")
            process = subprocess.Popen(cmd)
            processes.append(process)

        # Wait for all processes to complete
        for process in processes:
            process.wait()

    except KeyboardInterrupt:
        print("KeyboardInterrupt received. Terminating all processes...")
        for process in processes:
            process.terminate()

if __name__ == "__main__":
    # Replace 'script.py' with the path to your PySyncObj Raft script
    script_path = "local_orderbook_simulation.py"
    launch_raft_nodes(script_path)
