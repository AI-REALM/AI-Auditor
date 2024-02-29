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
        # print("Data received from Node.js:", data)
        if "errors" in data:
            print("Errors")
            return False
        else:
            wallet_info = {}
            for i in data["wallet"]:
                wallet_info[i.split("$")[0]] = float(i.split("$")[-1].strip().replace(",", ""))
            
            contain_general_info = {}
            
            for i in data["cryptoInfo"]:
                contain_general_info[i.split("$")[0]] = float(i.split("$")[-1].strip().replace(",", ""))

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
            return_value = {
                "address": data["address"],
                "wallet": wallet_info,
                "general_info": contain_general_info,
                "contain_crypto": contain_cryto
            }
            return return_value
            # Handle the error as needed
    else:
        print("Node.js script failed with return code:", process.returncode)
        return False

# print(get_account_info("0x2170ed0880ac9a755fd29b2688956bd959f933f8"))