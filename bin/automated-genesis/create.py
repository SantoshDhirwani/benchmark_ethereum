#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Created on Sat Jan  4 17:16:56 2020

@author: ankush.sharma1@ibm.com
"""

import sys
import argparse
import subprocess
import json
import os
import logging
import re

# const in python
PIDFILE = "/tmp/geth.pid"

# Change genesis file here
GENESIS = u"""{
  "config": {
    "chainId": 15,
    "homesteadBlock": 1,
    "eip150Block": 2,
    "eip150Hash": "0x0000000000000000000000000000000000000000000000000000000000000000",
    "eip155Block": 3,
    "eip158Block": 3,
    "byzantiumBlock": 4,
    "clique": {
      "period": 2,
      "epoch": 30000
    }
  },
  "nonce": "0x0",
  "timestamp": "0x5a97adf5",
  "extraData": "",
  "gasLimit": "0x47b760",
  "difficulty": "0x1",
  "mixHash": "0x0000000000000000000000000000000000000000000000000000000000000000",
  "coinbase": "0x0000000000000000000000000000000000000000",
  "alloc": {
      "0x$ADDRESS$": { "balance": "1000000000000000000000" },
"""


def load_keys(key):
    #Load Key for accounts
    try:
        file = open("config.json", "r")
        txt = file.read()
        file.close()
        d = json.loads(txt)
    except:
        logging.error("invalid config file")
        logging.error("please use and modify the pgeth_config.json")
        sys.exit(-1)
    if d.has_key(key):
        return d[key]
    return None


def getDataDir():
    #Load datadir key
    datadir = load_keys("datadir")
    datadir = os.path.expanduser(datadir)
    return datadir


def testDir(path):
    #Check exisitng path and the directory
    if not os.path.exists(path):
        return False
    if not os.path.isdir(path):
        return False
    return True


def testFile(path):
    #Check the exisiting path and the file
    if not os.path.exists(path):
        return False
    if not os.path.isfile(path) and os.access(path, os.X_OK):
        return False
    return True


def testGeth():
    #check if geth is installed
    geth = load_keys("geth")
    if geth:
        if testFile(geth):
            return geth
        logging.error("invalid geth path in config file")
        sys.exit(-1)
    stdpaths = [ "/usr/bin/geth", "/usr/local/bin/geth", "/opt/local/bin/geth" ]
    for p in stdpaths:
        if testFile(p):
            return p
    logging.error("no geth found in classic path. Use the geth param in the config file")
    sys.exit(0)


def strCommand(cmd):
    #joining the commands
    return " ".join(cmd)


def getAddr(i):
    #get the address of account created
    datadir = getDataDir()
    geth = testGeth()
    options = [ "--datadir", datadir ]
    accountsList = [ geth ] + options + ["account", "list"]
    logging.debug("cmd: " + strCommand(accountsList))
    response = subprocess.check_output(accountsList)
    accountQty = len(response.split('\n')) - 1
    if accountQty == 0:
        return None
    if len(response.split('\n'))>=1:
        line = response.split('\n')[i-1]
    exp = re.search(u"{([0-9abcdefABCDEF]+)}", line)
    if exp == None:
        logging.error("No address found in keystore")
        sys.exit(-1)
    result = exp.group(1)
    logging.debug('address found: 0x' + result)
    return result


def initAccount():
    #creating an account and saving password in password.txt
    datadir = getDataDir()
    geth = testGeth()
    options = [ "--datadir", datadir ]
    # create mypassword.txt
    f = open("password.txt", "w")
    f.write(load_keys("password"))
    f.close()
    # create an account
    cmdCreateAccount = [ geth ] + options + [ "--password", "password.txt", "account", "new" ]
    logging.debug("cmd: " + strCommand(cmdCreateAccount))
    subprocess.call(cmdCreateAccount)


def init(args):
    # Create multiple accounts
    i =1
    n =4 #add number of nodes here
    for i in range (1,n+1):
        initAccount()
        if i ==1 : 
            # Create genesis.json file for first time
            address = getAddr(i)
            txt = GENESIS.replace("$ADDRESS$", address)
            f = open("genesis.json", "w")
            f.write(txt)
            f.close()
        else:
            #update genesis.json with new added addreses
            address = getAddr(i)
            f = open("genesis.json", "a")
            textList = ['      ', "\"0x", address, "\"", ":",' ', "{",' ', "\"","balance", "\"", ":",' ', "\"","1000000000000000000000", "\"",' ', "}"]
            for line in textList:
                f.write(line)
            if i != n-1:
                f.write(",")    
            f.write("\n")
            if i == n-1:  
                text = [' ',' ',"}","\n","}"]
                for line1 in text:
                    f.write(line1)
            f.close()       
 
    # Initialize genesis.json change networkid accordingly
    datadir = getDataDir()
    if testDir(os.path.join(datadir, 'chaindata')):
        return 
    geth = testGeth()
    options = [ "--datadir", datadir, "--networkid", "100" ]
    cmdInit = [ geth ] + options + [ "init", "genesis.json"]
    logging.debug("cmd: " + strCommand(cmdInit))


def import_(args):
    """fsdf"""
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S')

    parser = argparse.ArgumentParser(description = 'to be completed')

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    init_parser = subparsers.add_parser('init')
    init_parser.set_defaults(func = init)

    args = parser.parse_args()
    args.func(args)  
