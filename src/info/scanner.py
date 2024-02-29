import subprocess
import json

# Define the Node.js script's path
node_script_path = 'src\\info\\chart\\scanner.js'


def get_scanner_data(address, chain_id, project, liquidity, holder, score):
    # Execute the Node.js script using subprocess
    process = subprocess.run(['node', node_script_path, address, str(chain_id), project, liquidity, holder, score], capture_output=True, text=True)

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

def get_scanner_general_result(address, chain_id, liquidity):
    if liquidity:
        data = get_scanner_data(address=address, chain_id=chain_id, project="T", liquidity="T", holder="T", score= "T")
    else:
        data = get_scanner_data(address=address, chain_id=chain_id, project="T", liquidity="F", holder="F", score= "T")
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
    if data["holderAnalysis"]:
        for i in data["holderAnalysis"]["issues"]:
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
    
    else:
        owner = None
        ownerbalance = None
        ownerBalancePercentage = None

        creator = None
        creatorbalance =  None
        creatorBalancePercentage = None

        supply = None

    if data["liquidityAnalysis"]:
        for i in data["liquidityAnalysis"]["issues"]:
            if i["issues"] != []:
                issues.append(i)
            else:
                pass

        liquidity = float(data["liquidityAnalysis"]["totalLiquidity"])
        totalLockedPercent = data["liquidityAnalysis"]["totalLockedPercent"]
        totalUnlockedPercent = data["liquidityAnalysis"]["totalUnlockedPercent"]
    else:
        liquidity = None
        totalLockedPercent = None
        totalUnlockedPercent = None

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
        "liquidity": liquidity
    }
    return return_value

def get_scanner_issues_result(address, chain_id, liquidity):
    if liquidity:
        data = get_scanner_data(address=address, chain_id=chain_id, project="T", liquidity="T", holder="T", score="F")
    else:
        data = get_scanner_data(address=address, chain_id=chain_id, project="T", liquidity="F", holder="F", score="F")
    
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
    if data["holderAnalysis"]:
        for i in data["holderAnalysis"]["issues"]:
            if i["issues"] != []:
                issues.append(i)
            else:
                pass
    if data["liquidityAnalysis"]:
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
    data = get_scanner_data(address=address, chain_id=chain_id, project="F", liquidity="T", holder="F", score="F")
    return data["liquidityAnalysis"]

def get_scanner_holders_result(address, chain_id):
    data = get_scanner_data(address=address, chain_id=chain_id, project="F", liquidity="F", holder="T", score="F")
    return data["holderAnalysis"]


# get_scanner_data("0x2170ed0880ac9a755fd29b2688956bd959f933f8", '56')