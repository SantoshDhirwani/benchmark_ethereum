from __future__ import print_function
import os
import json
import subprocess


CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))



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
    intervals = {5,10,15}
    gasLimit = {10000000,15000000,20000000}
    
    for interval in intervals:
        for gas in gasLimit:
            print('Building SUT with block interval ' + str(interval) + 's and ' + str(gas) + ' block gas limit')
            run_file(['sh', _get_path('deploy-sut.sh'), str(config['parameters']['nodesNumber']), str(interval), str(gas)])
            #run_file(['python3'],_get_path('run_caliper.py'), ...)
    print('Aggregating all the workload reports')
    run_file(['python', _get_path('aggregate-reports/aggregate-html-reports.py')])    

#    files = [
        #['bash', _get_path('build-tag-push-docker-image.sh')],
#        ['python', _get_path('deploy-sut.sh'),
#         '--nodes', str('config')],
#        ['python', _get_path('aggregate-reports/aggregate-html-reports.py')],
#    ]


#    for f in files:
#        run_file(f)
