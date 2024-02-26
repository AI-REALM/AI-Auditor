import subprocess
import json

# Define the Node.js script's path
node_script_path = 'src\\info\\chart\\scanner.js'


def get_scanner_data(address, chain_id):
    # Execute the Node.js script using subprocess
    process = subprocess.run(['node', node_script_path, address, chain_id], capture_output=True, text=True)

    # Check if the subprocess ran successfully
    if process.returncode == 0:
        # Get the stdout from the Node.js script and parse the JSON
        output = process.stdout
        data = json.loads(output)  # Parse the JSON output from Node.js
        print("Data received from Node.js:", data)
    else:
        print("Node.js script failed with return code:", process.returncode)

get_scanner_data("0x2170ed0880ac9a755fd29b2688956bd959f933f8", '56')