import json
import os

def update_json(filename):
    ipaddress = input("Please type your node's IP (with http or https): ")
    port = input("Please type your used port: ")
    nodeaddress = input("Type your node address : ")
    nodepassword = input("Type your node address password: ")

    with open(filename, 'r') as read_file:
        data = json.load(read_file)
        
    data["ethereum"]["url"] = ipaddress+":"+port
    data["ethereum"]["contractDeployerAddress"]= nodeaddress
    data["ethereum"]["contractDeployerAddressPassword"]= nodepassword
    data["ethereum"]["fromAddress"]= nodeaddress
    data["ethereum"]["fromAddressPassword"]= nodepassword

    with open("/hyperledger/caliper/workspace/network.json", "w") as jsonFile:
        json.dump(data, jsonFile)

def main():
    #updpate details for network file
    networkfile = "sample-network.json"
    update_json(networkfile)

    #run the caliper
    os.system("run-caliper.sh")
    exit()

if __name__ == '__main__':
    main()
