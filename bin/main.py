from __future__ import print_function
import os
import json
import subprocess


CURRENT_FOLDER = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(CURRENT_FOLDER, 'config.json')


def _get_path(filename):
    return os.path.join(CURRENT_FOLDER, filename)


def load_number_of_nodes(path):
    with open(path) as fp:
        config = json.load(fp)

    try:
        return config['parameters']['nodesNumber']
    except KeyError:
        message = "You have an incorrect config structure: {}"
        reason = "Can't load value from path 'parameters/nodesNumber'"
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
                    'File "{}" was not finished successfully'.format(
                        file_path[1],
                    )
                )

            for output in process.stdout.readlines():
                print(output.strip())

            break


if __name__ == '__main__':
    number_of_nodes = load_number_of_nodes(CONFIG_PATH)

    files = [
        ['python', _get_path('aggregate-reports/aggregate-html-reports.py')],
        ['bash', _get_path('build-tag-push-docker-image.sh')],
        ['python', _get_path('create_vms_as_nodes.py'),
         '--nodes', str(number_of_nodes)]
    ]

    for f in files:
        run_file(f)
