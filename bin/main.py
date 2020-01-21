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


def check_execution(interval, gaslimit):
    run_file(['python', _get_path('get-last-throughput.py'), '--interval', str(interval), '--gaslimit',
                   str(gaslimit)])
    tps = 0
    with open('last-tps', "r") as file:
        tps = float(file.read())
    print(tps)
    #TODO check if last value improved enough to continue benchmarking
    return 0


def find_min_interval(config):
    intervals = range(1,
                      config['test_param']['defaultInterval'] + config['test_param']['intervalStep'],
                      config['test_param']['intervalStep'])
    for interval in intervals:
        print('Benchmarking to find minimum value, current configuration ' + str(interval) + ' seconds and ' +
              str(config['test_param']['defaultGas']) + ' gas limit.')
        try:
            run_file(
                ['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']), str(interval),
                 str(config['test_param']['defaultGas']), '0'])
            run_file(['python', _get_path('run-caliper.py'), '--interval', str(interval), '--gaslimit',
                      str(config['test_param']['defaultGas'])])
            # UNCOMMENT ONLY FOR TESTING PURPOSES
            # run_file(
            #    ['sh', _get_path('test.sh'), str(interval),
            #     str(config['test_param']['defaultGas'])])
            print('Minimum block interval found! - ' + str(interval) + ' seconds.')
            return interval
        except Exception as e:
            print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                str(interval), str(config['test_param']['defaultGas']), e))

    print(
        'Minimum block interval not found. Check again your setup or '
        'change the configuration values (default and steps values).')
    return -1


def find_min_gas_limit(config):
    gasLimit = range(1, config['test_param']['defaultGas'] + config['test_param']['gasStep'],
                     config['test_param']['gasStep'])
    for gas in gasLimit:
        print('Benchmarking to find minimum value, current configuration ' + str(config['test_param'][
                                                                                     'defaultInterval']) + ' seconds and ' +
              str(gas) + ' gas limit.')
        try:
            run_file(
                ['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']),
                 str(config['test_param']['defaultInterval']),
                 str(gas), '0'])
            run_file(['python', _get_path('run-caliper.py'), '--interval', str(config['test_param']['defaultInterval']),
                      '--gaslimit',
                      str(gas)])
            # UNCOMMENT ONLY FOR TESTING PURPOSES
            # run_file(
            #    ['sh', _get_path('test.sh'),
            #     str(config['test_param']['defaultInterval']), str(gas)])
            print('Minimum block gas limit found! - ' + str(gas))
            return gas
        except Exception as e:
            print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                str(config['test_param']['defaultInterval']), str(gas), e))

    print(
        'Minimum block gas limit not found. Check again your setup or '
        'change the configuration values (default and steps values).')
    return -1


if __name__ == '__main__':
    print('Starting tool execution...')
    config = load_config(CONFIG_PATH)

    # Backing up old results
    run_file(['python', _get_path('backup-old-results.py')])

    # Building SUT for the first time
    run_file(
        ['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']),
         str(config['test_param']['defaultInterval']),
         str(config['test_param']['defaultGas']), '1'])

    # Finding the minimum block interval
    min_interval = find_min_interval(config)
    if min_interval < 0:
        print("Tool execution failed.")
        exit(-1)

    # Finding the minimum block gas limit
    min_gas = find_min_gas_limit(config)
    if min_gas < 0:
        print("Tool execution failed.")
        exit(-1)

    # TODO implement algorithm to find maximum range of gaslimit and interval
    print("Starting benchmarking plan execution")
    # Creating new ranges
    intervals = range(min_interval,
                      config['test_param']['maxInterval'] + config['test_param']['intervalStep'],
                      config['test_param']['intervalStep'])
    gasLimit = range(min_gas, config['test_param']['maxGas'] + config['test_param']['gasStep'],
                     config['test_param']['gasStep'])

    for interval in intervals:
        for gas in gasLimit:
            print('Building SUT with block interval ' + str(interval) + 's and ' + str(gas) + ' block gas limit')
            run_file(['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']), str(interval), str(gas),
                      '0'])
            run_file(['python', _get_path('run-caliper.py'), '--interval', str(interval), '--gaslimit', str(gas)])
            if check_execution(interval, gas) is None:
                break

    print('Aggregating all the workload reports')
    run_file(['python', _get_path('aggregate-html-reports.py')])
    # run_file(['python', _get_path('calculate-optimal-values.py')])
    exit(0)
