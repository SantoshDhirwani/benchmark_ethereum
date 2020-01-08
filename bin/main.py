import os
import logging
import subprocess


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
                        file_path[-1],
                    )
                )

            for output in process.stdout.readlines():
                print(output.strip())

            break


if __name__ == '__main__':
    files = [
        ['python', 'aggregate-html-reports.py'],
        ['bash', 'build-tag-push-docker-image.sh'],
    ]

    for f in files:
        run_file(f)
