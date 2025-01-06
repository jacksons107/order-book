import subprocess


def launch_raft_nodes(test_path, partner_path):
    """
    Launch three instances of the PySyncObj-based Raft script with different ports.

    Args:
        script_path (str): Path to the Python script implementing the Raft counter.
    """
    # Define the ports for each node
    nodes = [
        ("5003", ["5001", "5002"]),
        ("5001", ["5003", "5002"]),
        ("5002", ["5003", "5001"]),
    ]

    processes = []

    try:
        node_port, partner_ports = nodes[0]
        cmd = [
                "python", test_path,
                node_port,
            ] + partner_ports
        print(f"Launching test node on port {node_port} with partners {partner_ports}...")
        process = subprocess.Popen(cmd)
        processes.append(process)
        # Launch each node as a separate subprocess
        for node_port, partner_ports in nodes[1:]:
            cmd = [
                "python", partner_path,
                node_port,
            ] + partner_ports
            print(f"Launching partner node on port {node_port} with partners {partner_ports}...")
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
    # testing_path = "local_orderbook_simulation.py"
    test_path = "testing_node.py"
    partner_path = "partner_node.py"
    launch_raft_nodes(test_path, partner_path)
