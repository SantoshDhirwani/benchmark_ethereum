from __future__ import print_function
import os
import json
import subprocess


CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))


def _get_path(filename):
    return os.path.join(CURRENT_FOLDER, filename)


CONFIG_PATH = os.path.join(_get_path('../config'), 'config.json')


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


def run_file(file_path):
    process = subprocess.Popen(
        file_path,
        stdout=subprocess.PIPE,
        universal_newlines=True
    )

    while True:
        output = process.stdout.readline()
        print(output.strip())

        return_code = process.poll()
        if return_code is not None:
            if return_code:
                raise Exception(
                    'File "{}" has not finished successfully: RETURN CODE {}'.format(
                        file_path[1], return_code,
                    )
                )

            for output in process.stdout.readlines():
                print(output.strip())

            break


if __name__ == '__main__':
    print('Starting tool execution...')
    config = load_config(CONFIG_PATH)
    #TODO decide how to give these parameters
    intervals = range(config['test_param']['minInterval'], config['test_param']['maxInterval']+config['test_param']['intervalStep'],
        config['test_param']['intervalStep'])
    gasLimit = range(config['test_param']['minGas'], config['test_param']['maxGas']+config['test_param']['gasStep'],
        config['test_param']['gasStep'])

    node_number = config['eth_param']['nodeNumber']

    for i in range(1, node_number + 1):
        node_name = 'ethereum{}'.format(i)
        print('CREATE NODE WITH NAME:', node_name)
        run_file(['python', _get_path('gcp.py'), '--name', node_name])

    for interval in intervals:
         for gas in gasLimit:
            print('Building SUT with block interval ' + str(interval) + 's and ' + str(gas) + ' block gas limit')

            run_file(['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']), str(interval), str(gas),'0'])
            run_file(['python',_get_path('run-caliper.py'), '--interval', str(interval), '--gaslimit', str(gas)])

    print('Aggregating all the workload reports')
    run_file(['python', _get_path('aggregate-html-reports.py')])
    #run_file(['python', _get_path('calculate-optimal-values.py')])
    exit(0)
