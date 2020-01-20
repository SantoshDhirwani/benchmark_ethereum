import glob
import argparse
import pandas as pd


def load_args():
    parser = argparse.ArgumentParser(description="This script is for running caliper benchmark")
    parser.add_argument("--interval", help="Block interval", required=True)
    parser.add_argument("--gaslimit", help="Block gas limit", required=True)

    return parser.parse_args()


def parse_file(files):
    try:
        my_tables = []
        for file in files:
            tables = pd.read_html(file)
            temp = tables[0]
            temp['fileName'] = file.split('/')[-1]
            my_tables.append(temp)
        return my_tables[0].loc[my_tables[0]['Name'].isin(['transfer'])]['Throughput (TPS)'].values.tolist()[0]
    except Exception as e:
        print('Failed to obtain the TPS for the report. Reason: %s' % e)
    exit(-1)


def main():
    print('Obtaining last result from the caliper report...')
    config = load_args()
    last_report = 'caliper-reports/' + config.interval + 'seconds-' + config.gaslimit + '.html'
    files = glob.glob(last_report)
    tps = parse_file(files)
    with open('last-tps', "w") as file:
        file.write(str(tps))
    exit(0)


if __name__ == '__main__':
    main()