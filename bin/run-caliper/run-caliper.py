import json
import os
import argparse

def update_json(filename):
    parser = argparse.ArgumentParser(description="This script is for running caliper benchmark")
    parser.add_argument("--ipaddress", help="IP Address of the node SUT", required=True)
    parser.add_argument("--port", help="Used port", required=True)
    parser.add_argument("--account", help="The account of the node", required=True)
    parser.add_argument("--password", help="Password for the account", required=True)

    args = parser.parse_args()

    with open(filename, 'r') as read_file:
        data = json.load(read_file)
        
    data["ethereum"]["url"] = args.ipaddress+":"+args.port
    data["ethereum"]["contractDeployerAddress"]= args.account
    data["ethereum"]["contractDeployerAddressPassword"]= args.password
    data["ethereum"]["fromAddress"]= args.account
    data["ethereum"]["fromAddressPassword"]= args.password

    with open('config/network.json', "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)

def main():
    #updpate details for network file
    networkfile = "sample-network.json"
    update_json(networkfile)

    #run the caliper
    bashfile = "run-caliper.sh"
    os.system("bash " + bashfile)
    exit()

if __name__ == '__main__':
    main()
