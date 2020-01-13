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
                    'File "{}" has not finished successfully'.format(
                        file_path[1],
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
    
    for interval in intervals:
        for gas in gasLimit:
            print('Building SUT with block interval ' + str(interval) + 's and ' + str(gas) + ' block gas limit')
            run_file(['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']), str(interval), str(gas)])
            #run_file(['python'],_get_path('run_caliper.py'), '----ipaddress',  '35.189.235.103', '--port', 8545,
            #                   '--account', '0x6aB8F5Cc686e543e3773fA6CA14513316fCEBCDa', '--password', 'cloudproto')

    print('Aggregating all the workload reports')
    run_file(['python', _get_path('aggregate-html-reports.py')])
    run_file(['python', _get_path('calculate-optimal-values.py')])
