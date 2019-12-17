import pandas as pd

def readFile():
    read_file = pd.read_csv('mockup/random_sample.csv', index_col=0)
    return read_file

def findMax(dictionary):
    key = dictionary.values.max()
    return key

def main():
    dict_file = readFile()
    max_value = findMax(dict_file)
    print(dict_file)
    print (max_value)

if __name__ == '__main__':
    main()