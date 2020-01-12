import json
import os
import argparse


def load_args():
    parser = argparse.ArgumentParser(description="This script is for running caliper benchmark")
    parser.add_argument("--ipaddress", help="IP Address of the node SUT", required=True)
    parser.add_argument("--port", help="Used port", required=True)
    parser.add_argument("--account", help="The account of the node", required=True)
    parser.add_argument("--password", help="Password for the account", required=True)
    parser.add_argument("--interval", help="Block interval", required=True)
    parser.add_argument("--gaslimit", help="Block gas limit", required=True)

    return parser.parse_args()


def update_json(filename, args):
    with open(filename, 'r') as read_file:
        data = json.load(read_file)
        
    data["ethereum"]["url"] = "http://"+args.ipaddress+":"+args.port
    data["ethereum"]["contractDeployerAddress"]= args.account
    data["ethereum"]["contractDeployerAddressPassword"]= args.password
    data["ethereum"]["fromAddress"]= args.account
    data["ethereum"]["fromAddressPassword"]= args.password

    with open('caliper-config/networks/ethereum/1node-clique/ethereum.json', "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)


def main():
    #load args
    config = load_args()
    #updpate details for network file
    networkfile = "caliper-config/sample-network.json"
    update_json(networkfile, config)

    #run the caliper
    bashfile = "run-caliper.sh"
    reportname = config.interval + "seconds-" + config.gaslimit + ".html"
    os.system("bash " + bashfile + " " + reportname)
    exit(0)


if __name__ == '__main__':
    main()
