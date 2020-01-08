from __future__ import print_function
import os
import subprocess


current_folder = os.path.dirname(os.path.abspath(__file__))


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
        ['python', os.path.join(
            current_folder,
            'aggregate-reports/aggregate-html-reports.py',
        )],
        ['bash', os.path.join(
            current_folder,
            'build-tag-push-docker-image.sh',
        )],
    ]

    for f in files:
        run_file(f)
