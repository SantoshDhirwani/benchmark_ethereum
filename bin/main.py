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


config = load_config(CONFIG_PATH)


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


def get_last_tps(interval, gaslimit):
    run_file(['python', _get_path('get-last-throughput.py'), '--interval', str(interval), '--gaslimit',
              str(gaslimit)])
    tps = 0
    with open('last-tps', "r") as file:
        tps = float(file.read())
    print("Last execution tps for block interval " + str(interval) + " seconds and " + str(
        gaslimit) + " gas limit: " + str(tps))
    return tps


def find_min_interval():
    intervals = range(1,
                      config['test_param']['maxInterval'] + config['test_param']['intervalStep'],
                      config['test_param']['intervalStep'])
    for interval in intervals:
        print('Benchmarking to find minimum block interval value, current configuration ' + str(
            interval) + ' seconds and ' +
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
            print('Minimum block interval found! ' + str(interval) + ' seconds.')
            return interval
        except Exception as e:
            print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                str(interval), str(config['test_param']['defaultGas']), e))

    print(
        'Minimum block interval not found. Check again your setup or '
        'change the configuration values (default and steps values).')
    return -1


def find_min_gas_limit(interval):
    upper_bound = config['test_param']['minGas']
    lower_bound = upper_bound
    print("Benchmarking to find minimum block gas limit value for block interval dimension of " + str(
        interval) + " seconds.")
    # Benchmarking to get initial upper bound
    while True:
        try:
            run_file(
                ['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']),
                 str(interval),
                 str(upper_bound), '0'])
            run_file(['python', _get_path('run-caliper.py'), '--interval', str(interval),
                      '--gaslimit',
                      str(upper_bound)])
            # yes
            break
        except Exception as e:
            print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                str(interval), str(upper_bound), e))
        # no
        lower_bound = upper_bound
        upper_bound = int(upper_bound * 2)
    working_upper_bound = upper_bound
    upper_bound = int((upper_bound + lower_bound) / 2)
    print("A working gas limit upper bound has been found: " + str(upper_bound))
    accuracy = config["test_param"]["gasLimitAccuracy"]

    # Benchmarking upper bound
    while True:
        print("Benchmarking with " + str(upper_bound) + " upper bound and " + str(
            lower_bound) + " lower bound to find the minimum gas limit")
        try:
            run_file(
                ['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']),
                 str(interval),
                 str(upper_bound), '0'])
            run_file(['python', _get_path('run-caliper.py'), '--interval', str(interval),
                      '--gaslimit',
                      str(upper_bound)])
            # UNCOMMENT ONLY FOR TESTING PURPOSES
            # run_file(
            #    ['sh', _get_path('test.sh'),
            #     str(config['test_param']['defaultInterval']), str(gas)])

            # Is inside the accuracy expected?
            if accuracy >= (abs(upper_bound - lower_bound)):
                break
            else:
                # yes
                working_upper_bound = upper_bound
                upper_bound = int((upper_bound + lower_bound) / 2)
        except Exception as e:
            print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                str(interval), str(upper_bound), e))
            # no
            lower_bound = upper_bound
            upper_bound = int((lower_bound + working_upper_bound) / 2)

    print("Minimum gas limit bound found: " + str(upper_bound))
    return upper_bound


def find_optimal_parameters():
    results = {}
    peaks = []
    trials = config["test_param"]["numberTrials"]
    sensitivity = config["test_param"]["sensitivity"]
    gas_step = config["test_param"]["gasStep"]
    interval_step = config["test_param"]["intervalStep"]
    # obtaining minimum block interval
    interval = find_min_interval()
    if interval < 0:
        print("Tool execution failed.")
        exit(-1)

    optimal = False

    while not optimal:
        print("Benchmarking with block interval of " + str(interval) + " seconds.")
        stop_reached = False
        # Finding the minimum block gas limit
        gas = find_min_gas_limit(interval)
        if gas < 0:
            # failed to get minimum block gas limit for x interval. Stopping tool execution
            stop_reached = True
        tries = 0
        while not stop_reached:
            print("Benchmarking with block interval of " + str(interval) + " seconds and " + str(gas) + " gas limit.")
            # benchmarking with block interval x and block gas limit y
            try:
                run_file(
                    ['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']),
                     str(interval),
                     str(gas), '0'])
                run_file(['python', _get_path('run-caliper.py'), '--interval', str(interval),
                          '--gaslimit',
                          str(gas)])
                # UNCOMMENT ONLY FOR TESTING PURPOSES
                # run_file(
                #    ['sh', _get_path('test.sh'),
                #     str(config['test_param']['defaultInterval']), str(gas)])
                last_tps = get_last_tps(interval, gas)
                print(str(interval) + "-" + str(gas) + "-" + str(last_tps))
                results[interval][gas] = last_tps
                # Is optimal gas limit for x interval found?
                if len(results[interval]) > trials:
                    pos = trials + 1
                    improvement = False
                    while pos > 1:
                        tmp = results[interval][gas - (pos * gas_step)] / last_tps
                        if tmp > sensitivity:
                            improvement = True
                        pos -= 1
                    if not improvement:
                        # yes
                        stop_reached = True
                        print("Improvement less than the sensitivity given, last feasible gas limit found")
                    else:
                        # no
                        gas += gas_step
                else:
                    # no, we need more trials
                    gas += gas_step
            except Exception as e:
                print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                    str(interval), str(gas), e))
                results[interval][gas] = -1
                # Crash found, yes
                if tries >= trials:
                    stop_reached = True
                else:
                    gas += gas_step
                print("Crash in benchmarking execution, last feasible gas limit found")
            tries += 1

        # optimal gas limit for x block interval found, getting the best TPS of this x block interval
        max_key = 0
        max_value = 0
        for key in results[interval]:
            value = results[interval][key]
            if value > max_value:
                max_value = value
                max_key = key
        last_peak = max_value
        print(
            "Peak in block interval " + str(interval) + " seconds found. Found in "
            + str(max_key) + " gas limit with " + str(last_peak) + " TPS.")
        # saving the last peak in the array of peaks
        peaks.append({str(interval) + ":" + str(max_key), max_value})
        # can we improve more the tps?
        if len(peaks) > trials:
            pos = trials + 1
            improvement = False
            while pos > 1:
                tmp = next(iter(peaks[-pos].values())) / last_peak
                if tmp > sensitivity:
                    improvement = True
                pos -= 1
            if not improvement:
                # no
                optimal = True
                print("Improvement less than the sensitivity given, last feasible combination found")
            else:
                # yes
                interval += interval_step
        else:
            # yes
            interval += interval_step

    # no more improvement expected, getting the maximum tps with its parameters
    max_result = 0
    best_parameters = {}
    for parameters in peaks:
        curr_value = next(iter(parameters.values()))
        if curr_value > max_result:
            max_result = curr_value
            best_parameters = parameters

    return best_parameters


if __name__ == '__main__':
    print('Starting tool execution...')

    # Backing up old results
    run_file(['python', _get_path('backup-old-results.py')])

    # Building SUT for the first time
    run_file(
        ['sh', _get_path('deploy-sut.sh'), str(config['eth_param']['nodeNumber']),
         str(config['test_param']['maxInterval']),
         str(config['test_param']['defaultGas']), '1'])

    result = find_optimal_parameters()
    print("Best result found: " + str(result))

    print('Aggregating all the workload reports')
    run_file(['python', _get_path('aggregate-html-reports.py')])
    # run_file(['python', _get_path('calculate-optimal-values.py')])
    exit(0)
