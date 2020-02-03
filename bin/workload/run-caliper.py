import json
import os
import argparse

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))


def _get_path(filename):
    return os.path.join(CURRENT_FOLDER, filename)


def load_config(path):
    print('Reading user configuration...')
    with open(path) as fp:
        config = json.load(fp)

    try:
        return config
    except KeyError:
        message = "You have an incorrect config structure: {}"
        reason = "Can't load config from the 'config' folder"
        raise KeyError(message.format(reason))


def load_args():
    parser = argparse.ArgumentParser(description="This script is for running caliper benchmark")
    parser.add_argument("--interval", help="Block interval", required=True)
    parser.add_argument("--gaslimit", help="Block gas limit", required=True)

    return parser.parse_args()


def update_json(filename, args):
    config = open('run_caliper.conf', 'r')
    instance = config.readline()
    config.close()
    with open(filename, 'r') as read_file:
        data = json.load(read_file)
    instance_data = instance.split(':')

    data["ethereum"]["url"] = "http://" + instance_data[0] + ":" + instance_data[1]
    data["ethereum"]["contractDeployerAddress"] = "0x" + instance_data[2]
    data["ethereum"]["contractDeployerAddressPassword"] = instance_data[3].split('\n')[0]
    data["ethereum"]["fromAddress"] = "0x" + instance_data[2]
    data["ethereum"]["fromAddressPassword"] = instance_data[3].split('\n')[0]

    with open('workload/caliper-config/networks/ethereum/1node-clique/ethereum.json', "w") as jsonFile:
        json.dump(data, jsonFile, indent=4)


# get config for attempt
CONFIG_PATH = os.path.join(_get_path('../../config'), 'config.json')


def main():
    # load args
    config = load_args()
    # updpate details for network file
    networkfile = "workload/caliper-config/sample-network.json"
    update_json(networkfile, config)

    # run the caliper
    config_general = load_config(CONFIG_PATH)
    attempt = config_general['run_caliper']['attempt']
    bashfile = "workload/run-caliper.sh"
    reportname = config.interval + "seconds-" + config.gaslimit + ".html"
    # running in number of attempts if it's failing (attempts variable getting from config)
    for i in range(attempt):
        # running run-caliper.sh with reportname
        run_command = os.system("bash " + bashfile + " " + reportname)
        if run_command == 0:
            print("Running caliper success.")
            break

        # if it reach the maximum attempt, printing error message
        if i == attempt - 1:
            print("Meet maximum retry. Running caliper error.")
            # exit(-1)
            raise Exception('Caliper execution failed ' + str(attempt) + ' times')
        else:
            print("Caliper retrying...")
            pass
    exit(0)


if __name__ == '__main__':
    main()
