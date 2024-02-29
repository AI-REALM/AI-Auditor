import subprocess
import json

# Define the Node.js script's path
node_script_path = 'src\\info\\chart\\search.js'


def get_scanner_data(address):
    # Execute the Node.js script using subprocess
    process = subprocess.run(['node', node_script_path, address], capture_output=True, text=True)

    # Check if the subprocess ran successfully
    if process.returncode == 0:
        # Get the stdout from the Node.js script and parse the JSON
        output = process.stdout
        data = json.loads(output)  # Parse the JSON output from Node.js
        # print("Data received from Node.js:", data)
        return data
    else:
        # print("Node.js script failed with return code:", process.returncode)
        return False

def search_address_result(address):
    data = get_scanner_data(address=address)
    if data == False or data["contract"]["results"] == []:
        return None
    else:
        pass
    result = []
    for i in data["contract"]["results"]:
        for y in data["chaininfo"]:
            if y["metadata"]["absoluteChainId"] == i["network"]:
                lk = i
                lk["networkname"] = y["displayName"]
                result.append(lk)
                break
        
    return result

# print(search_address_result("0x2170ed0880ac9a755fd29b2688956bd959f933f8"))