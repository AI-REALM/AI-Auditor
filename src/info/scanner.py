import subprocess
import json

# Define the Node.js script's path
node_script_path = 'src\\info\\chart\\scanner.js'


def get_scanner_data(address, chain_id, type_analysis):
    # Execute the Node.js script using subprocess
    process = subprocess.run(['node', node_script_path, address, str(chain_id), type_analysis], capture_output=True, text=True)

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

def get_scanner_general_result(address, chain_id):
    data = get_scanner_data(address=address, chain_id=chain_id, type_analysis="all")
    if data == False or data["project"] == None:
        return None
    else:
        pass
    project_name = data["project"]["name"]
    airealm_score = data["score"]["score"]
    contractname = data["project"]["contractName"]
    issues = []
    for i in data["project"]["coreIssues"]:
        if i["issues"] != []:
            issues.append(i)
        else:
            pass
    for i in data["holderAnalysis"]["issues"]:
        if i["issues"] != []:
            issues.append(i)
        else:
            pass
    for i in data["liquidityAnalysis"]["issues"]:
        if i["issues"] != []:
            issues.append(i)
        else:
            pass
    owner = data["holderAnalysis"]["owner"]
    ownerbalance = data["holderAnalysis"]["ownerBalance"]
    ownerBalancePercentage = data["holderAnalysis"]["ownerBalancePercentage"]

    creator = data["holderAnalysis"]["creator"]
    creatorbalance =  data["holderAnalysis"]["creatorBalance"]
    creatorBalancePercentage = data["holderAnalysis"]["creatorBalancePercentage"]

    supply = data["holderAnalysis"]["tokenTotalSupply"]

    iiquidity = float(data["liquidityAnalysis"]["totalLiquidity"])
    totalLockedPercent = data["liquidityAnalysis"]["totalLockedPercent"]
    totalUnlockedPercent = data["liquidityAnalysis"]["totalUnlockedPercent"]

    return_value = {
        "project_name": project_name, 
        "airealm_score": airealm_score, 
        "contractname": contractname,
        "issues": issues, 
        "owner": owner, 
        "ownerbalance": ownerbalance,
        "ownerBalancePercentage": ownerBalancePercentage,
        "creator": creator, 
        "creatorbalance": creatorbalance,
        "creatorBalancePercentage": creatorBalancePercentage,
        "supply": supply, 
        "totalLockedPercent": totalLockedPercent,
        "totalUnlockedPercent": totalUnlockedPercent,
        "iiquidity": iiquidity
    }
    return return_value

def get_scanner_issues_result(address, chain_id):
    data = get_scanner_data(address=address, chain_id=chain_id, type_analysis="issues")
    if data == False or data["project"] == None:
        return None
    else:
        pass
    issues = []
    for i in data["project"]["coreIssues"]:
        if i["issues"] != []:
            issues.append(i)
        else:
            pass
    for i in data["holderAnalysis"]["issues"]:
        if i["issues"] != []:
            issues.append(i)
        else:
            pass
    for i in data["liquidityAnalysis"]["issues"]:
        if i["issues"] != []:
            issues.append(i)
        else:
            pass

    return_value = {
        "issues": issues
    }
    return return_value

def get_scanner_liquidity_result(address, chain_id):
    data = get_scanner_data(address=address, chain_id=chain_id, type_analysis="liquidity")
    return data["liquidityAnalysis"]

def get_scanner_holders_result(address, chain_id):
    data = get_scanner_data(address=address, chain_id=chain_id, type_analysis="holders")
    return data["holderAnalysis"]


# get_scanner_data("0x2170ed0880ac9a755fd29b2688956bd959f933f8", '56')