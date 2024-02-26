import subprocess
import json

# Define the Node.js script's path
node_script_path = 'src\\info\\chart\\address.js'


def get_account_info(address):
    # Execute the Node.js script using subprocess
    process = subprocess.run(['node', node_script_path, address], capture_output=True, text=True)

    # Check if the subprocess ran successfully
    if process.returncode == 0:
        # Get the stdout from the Node.js script and parse the JSON
        output = process.stdout
        data = json.loads(output)  # Parse the JSON output from Node.js
        print("Data received from Node.js:", data)
        if "errors" in data:
            print("Errors")
        else:
            wallet = int(data["wallet"].split("$")[-1].strip().replace(",", ""))

            contain_cryto = {}
            for i in data["cryptoInfo"]:
                key = i.split("$")[0]
                for y in data["chainInfo"]:
                    # print(key.lower(), y["displayName"].lower())
                    if key.lower() == y["displayName"].lower():
                        contain_cryto[y["abbr"]] = {
                            "name" : y["displayName"],
                            "amount" : float(i.split("$")[-1].strip().replace(",", "")),
                            "chainid" : y["metadata"]["absoluteChainId"]
                        }
                    
            print(wallet)
            print(contain_cryto)
            # Handle the error as needed
    else:
        print("Node.js script failed with return code:", process.returncode)

get_account_info("0x2170ed0880ac9a755fd29b2688956bd959f933f8")