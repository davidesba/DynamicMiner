#!/usr/local/bin/python
# -*- coding: utf-8 -*-
from optparse import OptionParser
import subprocess
import sys
from apscheduler.schedulers.background  import BackgroundScheduler
import logging
from base64 import b64encode
import time
import datetime
from coinManager import coinManager


logging.basicConfig()

def copyLog(skipTime=False):
    if ((datetime.datetime.now().hour == 23) and (datetime.datetime.now().minute >= 55)) or skipTime:
        subprocess.call('scp /Users/davides/miners/miner/workfile osmc@192.168.0.156:/home/osmc', shell=True)

class Miner(object):
    def __init__(self, setCoin=''):
        self.__command = 'none'
        self.__process = None
        self.__manager = coinManager(setCoin)
        self.updateManager()

    def updateManager(self):
        new_command = self.__manager.updateData()
        if new_command != self.__command:
            if self.__process:
                self.__process.kill()
            self.__process = subprocess.Popen(new_command, shell=True)
            self.__command = new_command

    def getManager(self):
        return self.__manager

usage = "usage: %prog [options] arg"
parser = OptionParser(usage)
parser.add_option("-m", "--miner", dest="miner", help="Type of miner to use: ubq kmd zen")
parser.add_option('-p', '--priority', dest='priority', help='priority set for coin')

(options, args) = parser.parse_args()

miner = None
miner_select = 'none'

if options.miner:
    print "Mining using " + options.miner.upper()
    miner.getManager().printBalance(options.miner)
    miner_select = options.miner
    miner = Miner(miner_select)
else:
    print "Variable mining"
    miner = Miner()
    if options.priority:
        miner.getManager().setCoinPriority(options.priority)
    scheduler = BackgroundScheduler()
    scheduler.add_job(miner.updateManager, 'interval', minutes=1.5)
    scheduler.start()

exit_program = False
try:
    while not exit_program:
        user_input = raw_input('')
        if user_input == 'print':
            miner.getManager().printTime()
        elif '-p' in user_input:
            miner.getManager().setCoinPriority(user_input.split(' ')[1])
except KeyboardInterrupt:
    miner.getManager().printTime()  
    miner.getManager().end()
    copyLog(skipTime=True)
    sys.exit(0)
