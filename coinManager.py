# -*- coding: utf-8 -*-
import json
import requests
import datetime
import time
import operator
import stats

class Coin(object):
    def __init__(self, name, command, fullName, prio):
        self.__name = name
        self.__diff = 0.0
        self.__prio = prio
        self.__time = 0
        self.__command = command
        self.__fullName = fullName
        self.__revenue = 0.0
    
    def incTime(self):
        self.__time += 1

    def setPrio(self, prio):
        self.__prio = prio

    def getPrio(self):
        return self.__prio

    def setRevenue(self, rev):
        self.__revenue = rev

    def getRevenue(self):
        return self.__revenue + float(self.__prio)

    def updateDiff(self, diff, reset=False):
        if (self.__diff == 0.0) or reset:
            self.__diff = diff
        else:
            self.__diff = (self.__diff + diff)/2.0

    def getDiff(self):
        return self.__diff

    def getName(self):
        return self.__name

    def getFullName(self):
        return self.__fullName

    def getCommand(self):
        return self.__command

    def getTime(self):
        return self.__time

class coinManager(object):
    def __init__(self,setCoin=''):
        self.__coins = dict()
        self.__interval = 1
        self.__statInterval = 1
        self.__selected = 'none'
        self.__onlyCoin = setCoin
        self.__statsMng = stats.statsManager()
        self.__f_out = open('workfile', 'a', 0)
        self.__f_out.write('[' + str(time.time()).split('.')[0] + "] Program Start\n")
        self.updateConfig()
        self.updateDiff()
    
    def end(self):
        self.__f_out.write(self.__statsMng.getReport(True))
        self.__f_out.write('[' + str(time.time()).split('.')[0] + "] Program Stop\n")
        self.__f_out.close()

    def updateConfig(self):
        newCoins = dict()
        with open('config.json') as json_data:
            config = json.load(json_data)
        if self.__onlyCoin != '':
            newCoins = {self.__onlyCoin : Coin(self.__onlyCoin, config['commands'][self.__onlyCoin], config['coin_translate'][self.__onlyCoin], config['coin_priority'][self.__onlyCoin])}
        else:
            for elem in config['active_coins']:
                if not elem in self.__coins:
                    newCoins.update({elem : Coin(elem, config['commands'][elem], config['coin_translate'][elem], config['coin_priority'][elem])})
                else:
                    newCoins.update(self.__coins[elem])
        self.__coins = newCoins
    
    def getMax(self):
        max_rev = 0
        max_dif = 0.0
        preferred = str()
        for coin in (sorted(self.__coins.values(), key=lambda x: x.getRevenue(), reverse=True)):
            if (coin.getRevenue() > max_rev) or ((coin.getRevenue() == max_rev) and (coin.getDiff() > self.__coins[preferred].getDiff())):
                max_rev = coin.getRevenue()
                preferred = coin.getName()
                max_dif = coin.getDiff()
        return preferred

    def updateDiff(self):
        response = requests.get('http://whattomine.com/coins.json?utf8=✓&eth=true&factor%5Beth_hr%5D=20.0&factor%5Beth_p%5D=90.0&grof=true&factor%5Bgro_hr%5D=20.0&factor%5Bgro_p%5D=90.0&x11gf=true&factor%5Bx11g_hr%5D=7.2&factor%5Bx11g_p%5D=90.0&cn=true&factor%5Bcn_hr%5D=430.0&factor%5Bcn_p%5D=70.0&eq=true&factor%5Beq_hr%5D=260.0&factor%5Beq_p%5D=90.0&lre=true&factor%5Blrev2_hr%5D=20300.0&factor%5Blrev2_p%5D=90.0&ns=true&factor%5Bns_hr%5D=598.0&factor%5Bns_p%5D=90.0&lbry=true&factor%5Blbry_hr%5D=170.0&factor%5Blbry_p%5D=90.0&bk2bf=true&factor%5Bbk2b_hr%5D=990.0&factor%5Bbk2b_p%5D=80.0&bk14=true&factor%5Bbk14_hr%5D=1550.0&factor%5Bbk14_p%5D=90.0&pas=true&factor%5Bpas_hr%5D=580.0&factor%5Bpas_p%5D=90.0&bkv=true&factor%5Bbkv_hr%5D=0.0&factor%5Bbkv_p%5D=0.0&factor%5Bcost%5D=0.12&sort=Profit&volume=0&revenue=current&factor%5Bexchanges%5D%5B%5D=&factor%5Bexchanges%5D%5B%5D=bittrex&factor%5Bexchanges%5D%5B%5D=cryptopia&dataset=Main&commit=Calculate&adapt_q_280x=3&adapt_q_380=0&adapt_q_fury=0&adapt_q_470=0&adapt_q_480=0&adapt_q_750Ti=0&adapt_q_10606=1&adapt_q_1070=0&adapt_q_1080=0&adapt_q_1080Ti=0')
        data = json.loads(response.text)
        log = '\033[;1m[' + str(datetime.datetime.now()).split('.')[0] + ']\033[;0m'
        for key, coin in self.__coins.items():
            coin.updateDiff(data['coins'][coin.getFullName()]['difficulty24']/data['coins'][coin.getFullName()]['difficulty'])
            coin.setRevenue(float(data['coins'][coin.getFullName()]['estimated_rewards'])*100000.0*data['coins'][coin.getFullName()]['exchange_rate'])

        for coin in (sorted(self.__coins.values(), key=lambda x: x.getRevenue(), reverse=True)):
            log += ' \033[1;36m%s\033[;0m:\033[1;31m%.2f\033[;0m:\033[0;32m%.2f:%d\033[;0m' % (coin.getName().upper(), coin.getDiff(), coin.getRevenue(), coin.getPrio())
        print log
        maxCoin = self.getMax()
        self.__statsMng.addPoint(self.__coins[maxCoin].getFullName(), data)
        return maxCoin

    def updateData(self):
        self.__interval += 1
        self.__statInterval += 1
        coinMax = self.updateDiff()
        if self.__selected == 'none':
            self.__selected = coinMax
            print '[' + str(datetime.datetime.now()).split('.')[0] + "] Mining " + self.__selected.upper()
            self.__f_out.write('[' + str(time.time()).split('.')[0] + "] Mining " + self.__selected.upper() + '\n')
        else:
            self.__coins[self.__selected].incTime()

        if (coinMax != self.__selected) and ((self.__coins[coinMax].getRevenue() - self.__coins[self.__selected].getRevenue()) > 1.0):
            print '[' + str(datetime.datetime.now()).split('.')[0] + "] Mining " + coinMax.upper()
            self.__f_out.write('[' + str(time.time()).split('.')[0] + "] Mining " + coinMax.upper() + '\n')
            self.__selected = coinMax
        self.__interval = 1
        
        return self.__coins[self.__selected].getCommand()

    def printTime(self):
        log = '[' + str(datetime.datetime.now()).split('.')[0] + ']'
        for key, coin in self.__coins.items():
            log += ' %s: %.5f' % (key.upper(), coin.getTime()*1.5/60)
        print log

    def setCoinPriority(self,data):
        for coin in data.split(','):
            self.__coins[coin.split(':')[0]].setPrio(int(coin.split(':')[1]))
            print 'Setting %s to %d' % (coin.split(':')[0], int(coin.split(':')[1]))

    def getCommand(self, coin):
        with open('config.json') as json_data:
            config = json.load(json_data)
        return config['commands'][coin]
