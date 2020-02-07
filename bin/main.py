from __future__ import print_function
import os
import sys
import json
import subprocess
import queue
import time

CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# 0: Print only the final step of aggregating results
# 1: Print content related to SUT and benchmarking
# 2: Print everything

verbose_level = int(sys.argv[1])
VERBOSE_LEVEL_0 = 0
VERBOSE_LEVEL_1 = 1
VERBOSE_LEVEL_2 = 2

ANALYZER_PATH = "analyzer/"
SUT_PATH = "sut/"
WORKLOAD_PATH = "workload/"
DEPLOY_SUT_PATH = SUT_PATH + "deploy-sut.sh"
RUN_WORKLOAD_PATH = WORKLOAD_PATH + "run-caliper.py"
AGGREGATE_RESULTS_PATH = ANALYZER_PATH + "aggregate-html-reports.py"
GET_LAST_RESULT_PATH = ANALYZER_PATH + "get-last-throughput.py"
BACKUP_PATH = ANALYZER_PATH + "backup-old-results.py"


def _get_path(filename):
    return os.path.join(CURRENT_FOLDER, filename)


CONFIG_PATH = os.path.join(_get_path('../config'), 'config.json')


def load_config(path):
    with open(path) as fp:
        config = json.load(fp)

    try:
        return config
    except KeyError:
        message = "You have an incorrect config structure: {}"
        reason = "Can't load config from the 'config' folder"
        raise KeyError(message.format(reason))


config = load_config(CONFIG_PATH)


def run_file(file_path, verbose=True):
    process = subprocess.Popen(
        file_path,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    while True:
        output = process.stdout.readline()
        err_output = process.stderr.readline()
        if verbose:
            print(output.strip())
            print(err_output.strip())

        return_code = process.poll()
        if return_code is not None:
            if return_code:
                raise Exception(
                    'File "{}" has not finished successfully'.format(
                        file_path[1],
                    )
                )

            for output in process.stdout.readlines():
                if verbose:
                    print(output.strip())
            for output in process.stderr.readlines():
                if verbose:
                    print(output.strip())

            break


def get_last_tps(interval, gaslimit):
    run_file(['python', _get_path(GET_LAST_RESULT_PATH), '--interval', str(interval), '--gaslimit',
              str(gaslimit)],
             verbose=verbose_level >= VERBOSE_LEVEL_2)
    tps = 0
    with open('last-tps', "r") as file:
        tps = float(file.read())
    if verbose_level >= VERBOSE_LEVEL_1:
        print("Last execution tps for block interval " + str(interval) + " seconds and " + str(
            gaslimit) + " gas limit: " + str(tps))
    return tps


def find_min_interval():
    intervals = range(1,
                      config['test_param']['maxInterval'] + config['test_param']['intervalStep'],
                      config['test_param']['intervalStep'])
    for interval in intervals:
        try:
            if verbose_level >= VERBOSE_LEVEL_1:
                print('Benchmarking to find minimum block interval value, current configuration ' + str(
                    interval) + ' seconds and ' +
                    str(config['test_param']['defaultGas']) + ' gas limit.')
                print('Building SUT')
            run_file(
                ['bash', _get_path(DEPLOY_SUT_PATH), str(config['eth_param']['nodeNumber']), str(interval),
                 str(config['test_param']['defaultGas']), '0',
                 '--no-user-output-enabled' if verbose_level == VERBOSE_LEVEL_0 else ''],
                verbose=verbose_level >= VERBOSE_LEVEL_2)
            if verbose_level >= VERBOSE_LEVEL_1:
                print('SUT successfully built')
                print('Executing the workload')
            run_file(['python', _get_path(RUN_WORKLOAD_PATH), '--interval', str(interval), '--gaslimit',
                      str(config['test_param']['defaultGas'])],
                     verbose=verbose_level == VERBOSE_LEVEL_2)
            if verbose_level >= VERBOSE_LEVEL_1:
                print('Workload executed')
            # UNCOMMENT ONLY FOR TESTING PURPOSES
            # run_file(
            #    ['sh', _get_path('test.sh'), str(interval),
            #     str(config['test_param']['defaultGas'])])
            if verbose_level >= VERBOSE_LEVEL_1:
                print('Minimum block interval found! ' + str(interval) + ' seconds.')
            return interval
        except Exception as e:
            if verbose_level >= VERBOSE_LEVEL_1:
                print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                    str(interval), str(config['test_param']['defaultGas']), e))

    print(
        'Minimum block interval not found. Check again your setup or '
        'change the configuration values (default and steps values).')
    return -1


def find_min_gas_limit(interval):
    upper_bound = config['test_param']['minGas']
    lower_bound = upper_bound
    if verbose_level >= VERBOSE_LEVEL_1:
        print("Benchmarking to find minimum block gas limit value for block interval dimension of " + str(
            interval) + " seconds.")
    # Benchmarking to get initial upper bound
    while True:
        try:
            if verbose_level >= VERBOSE_LEVEL_1:
                print(
                    "Benchmarking with block interval of " + str(interval) + " seconds and " + str(
                        upper_bound) + " gas limit.")
                print('Building SUT')
            run_file(
                ['bash', _get_path(DEPLOY_SUT_PATH), str(config['eth_param']['nodeNumber']),
                 str(interval),
                 str(upper_bound), '0', '--no-user-output-enabled' if verbose_level == VERBOSE_LEVEL_0 else ''],
                verbose=verbose_level == VERBOSE_LEVEL_2)
            if verbose_level >= VERBOSE_LEVEL_1:
                print('SUT successfully built')
                print('Executing the workload')
            run_file(['python', _get_path(RUN_WORKLOAD_PATH), '--interval', str(interval),
                      '--gaslimit',
                      str(upper_bound)], verbose=verbose_level == VERBOSE_LEVEL_2)
            if verbose_level >= VERBOSE_LEVEL_1:
                print('Workload executed')
            # yes
            break
        except Exception as e:
            if verbose_level >= VERBOSE_LEVEL_1:
                print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                    str(interval), str(upper_bound), e))
        # no
        lower_bound = upper_bound
        upper_bound = int(upper_bound * 2)
    working_upper_bound = upper_bound
    upper_bound = int((upper_bound + lower_bound) / 2)
    if verbose_level >= VERBOSE_LEVEL_1:
        print("A working gas limit upper bound has been found: " + str(upper_bound))
    accuracy = config["test_param"]["gasLimitAccuracy"]

    # Benchmarking upper bound
    while True:
        try:
            if verbose_level >= VERBOSE_LEVEL_1:
                print("Benchmarking with " + str(upper_bound) + " upper bound and " + str(
                    lower_bound) + " lower bound to find the minimum gas limit")
                print('Building SUT')
            run_file(
                ['bash', _get_path(DEPLOY_SUT_PATH), str(config['eth_param']['nodeNumber']),
                 str(interval),
                 str(upper_bound), '0', '--no-user-output-enabled' if verbose_level == VERBOSE_LEVEL_0 else ''],
                verbose=verbose_level >= VERBOSE_LEVEL_2)
            if verbose_level >= VERBOSE_LEVEL_1:
                print('SUT successfully built')
                print('Executing the workload')
            run_file(['python', _get_path(RUN_WORKLOAD_PATH), '--interval', str(interval),
                      '--gaslimit', str(upper_bound)], verbose=verbose_level >= VERBOSE_LEVEL_2)
            if verbose_level >= VERBOSE_LEVEL_1:
                print('Workload executed')
            # UNCOMMENT ONLY FOR TESTING PURPOSES
            # run_file(
            #    ['sh', _get_path('test.sh'),
            #     str(config['test_param']['defaultInterval']), str(gas)])

            if verbose_level >= VERBOSE_LEVEL_1:
                print('Calculating if the gas limit is under accuracy bounds')
            # Is inside the accuracy expected?
            if accuracy >= (abs(upper_bound - lower_bound)):
                break
            else:
                # no
                if verbose_level >= VERBOSE_LEVEL_1:
                    print('Not inside accuracy bounds, continuing find minimum gas limit execution')
                working_upper_bound = upper_bound
                upper_bound = int((upper_bound + lower_bound) / 2)
        except Exception as e:
            if verbose_level >= VERBOSE_LEVEL_1:
                print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                    str(interval), str(upper_bound), e))
            # no
            lower_bound = upper_bound
            upper_bound = int((lower_bound + working_upper_bound) / 2)
    if verbose_level >= VERBOSE_LEVEL_1:
        print("Minimum gas limit bound found: " + str(upper_bound))
    return upper_bound


def find_optimal_parameters():
    results = {}
    peaks = []
    interval_queue = queue.Queue()
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
        if verbose_level >= VERBOSE_LEVEL_1:
            print("Performing benchmarks with block interval of " + str(interval) + " seconds.")
        results[interval] = {}
        stop_reached = False
        # Finding the minimum block gas limit
        gas = find_min_gas_limit(interval)
        if gas < 0:
            # failed to get minimum block gas limit for x interval. Stopping tool execution
            stop_reached = True
        tries = 0
        gaslimit_queue = queue.Queue()
        while not stop_reached:
            if verbose_level >= VERBOSE_LEVEL_1:
                print(
                    "Benchmarking with block interval of " + str(interval) + " seconds and " + str(gas) + " gas limit.")
            # benchmarking with block interval x and block gas limit y
            try:
                if verbose_level >= VERBOSE_LEVEL_1:
                    print('Building SUT')
                run_file(
                    ['bash', _get_path(DEPLOY_SUT_PATH), str(config['eth_param']['nodeNumber']),
                     str(interval),
                     str(gas), '0', '--no-user-output-enabled' if verbose_level == VERBOSE_LEVEL_0 else ''],
                    verbose=verbose_level >= VERBOSE_LEVEL_2)
                if verbose_level >= VERBOSE_LEVEL_1:
                    print('SUT successfully built')
                    print('Executing the workload')
                run_file(['python', _get_path(RUN_WORKLOAD_PATH), '--interval', str(interval),
                          '--gaslimit', str(gas)], verbose=verbose_level >= VERBOSE_LEVEL_2)
                if verbose_level >= VERBOSE_LEVEL_1:
                    print('Workload executed')
                # UNCOMMENT ONLY FOR TESTING PURPOSES
                # run_file(
                #    ['sh', _get_path('test.sh'),
                #     str(config['test_param']['defaultInterval']), str(gas)])
                if verbose_level >= VERBOSE_LEVEL_1:
                    print('Obtaining peak and checking to continue or not')
                last_tps = get_last_tps(interval, gas)
                results[interval][gas] = last_tps
                # Is optimal gas limit for x interval found?
                if gaslimit_queue.qsize() >= trials:
                    tmp_queue = queue.Queue()
                    improvement = False
                    while not gaslimit_queue.empty():
                        x = gaslimit_queue.get(False)
                        tmp_queue.put(x)
                        tmp = 1 - (x / last_tps)
                        if verbose_level >= VERBOSE_LEVEL_2:
                            print("Sensitivity: " + str(tmp))
                        if tmp > sensitivity:
                            improvement = True
                    gaslimit_queue = tmp_queue
                    gaslimit_queue.get()
                    gaslimit_queue.put(last_tps)
                    if not improvement:
                        # yes
                        stop_reached = True
                        if verbose_level >= VERBOSE_LEVEL_1:
                            print("Improvement less than the sensitivity given, last feasible gas limit found")
                    else:
                        # no
                        if verbose_level >= VERBOSE_LEVEL_1:
                            print("No improvement found, continue with interval " + str(interval) + " seconds")
                        gas += gas_step
                else:
                    # no, we need more trials
                    if verbose_level >= VERBOSE_LEVEL_1:
                        print("Tool needs more data, continue with interval " + str(interval) + " seconds")
                    gaslimit_queue.put(last_tps)
                    gas += gas_step
            except Exception as e:
                if verbose_level >= VERBOSE_LEVEL_1:
                    print('Failed execution with configuration %s seconds and %s gas limit. Reason: %s' % (
                        str(interval), str(gas), e))
                results[interval][gas] = -1
                gaslimit_queue.put(-1)
                # Crash found, yes
                if tries > trials:
                    stop_reached = True
                    if verbose_level >= VERBOSE_LEVEL_1:
                        print("Crash in benchmarking execution, last feasible gas limit found")
                else:
                    if verbose_level >= VERBOSE_LEVEL_1:
                        print("Tool needs more data, continue with interval " + str(interval) + " seconds")
                    gas += gas_step

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
        if verbose_level >= VERBOSE_LEVEL_1:
            print(
                "Peak in block interval " + str(interval) + " seconds found. Found in "
                + str(max_key) + " gas limit with " + str(last_peak) + " TPS.")
        # saving the last peak in the array of peaks
        peaks.append({str(interval) + ":" + str(max_key): max_value})
        # can we improve more the tps?
        if len(peaks) > trials:
            if verbose_level >= VERBOSE_LEVEL_1:
                print("Checking to continue for more intervals or not")
            pos = trials + 1
            improvement = False
            while pos > 1:
                if verbose_level >= VERBOSE_LEVEL_2:
                    print("Peak calc: " + str(peaks[-pos].values()))
                tmp = 1 - (next(iter(peaks[-pos].values())) / last_peak)
                if tmp > sensitivity:
                    improvement = True
                pos -= 1
            if not improvement:
                # no
                optimal = True
                if verbose_level >= VERBOSE_LEVEL_1:
                    print("Improvement less than the sensitivity given, peak found")
            else:
                # no
                if verbose_level >= VERBOSE_LEVEL_1:
                    print("No improvement found, continue execution")
                interval += interval_step
        else:
            # no
            if verbose_level >= VERBOSE_LEVEL_1:
                print("Tool needs more data, continue execution")
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
    print('Starting tool execution')
    start_time = time.time()
    # Backing up old results
    run_file(['python', _get_path(BACKUP_PATH)], verbose=verbose_level == VERBOSE_LEVEL_2)

    # Building SUT for the first time
    print('Building the SUT')
    run_file(
        ['bash', _get_path(DEPLOY_SUT_PATH), str(config['eth_param']['nodeNumber']),
         str(config['test_param']['maxInterval']),
         str(config['test_param']['defaultGas']), '1',
         '--no-user-output-enabled' if verbose_level == VERBOSE_LEVEL_0 else ''],
        verbose=verbose_level >= VERBOSE_LEVEL_2)
    print('SUT successfully built')
    print('Starting calculation of optimal block interval and block gas limit for maximum throughput')
    result = find_optimal_parameters()
    print("Best result found: " + str(result))
    if verbose_level >= VERBOSE_LEVEL_1:
        print('Aggregating all the workload reports')
    key = list(result.keys())[0]
    throughput = result[key]
    interval = key.split(":")[0]
    gaslimit = key.split(":")[1]
    exec_time = (time.time() - start_time)
    run_file(['python', _get_path(AGGREGATE_RESULTS_PATH), "--interval", interval,
              "--gaslimit", gaslimit, "--throughput", str(throughput),"--executiontime", str(exec_time)],verbose=verbose_level == VERBOSE_LEVEL_2)
    print("Execution time: " + str(exec_time))
    exit(0)
