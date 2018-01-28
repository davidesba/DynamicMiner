import time
import datetime

class statPoint(object):
    def __init__(self, coin, value, rewards):
        self.coin = coin
        self.value = value
        self.rewards = rewards/960.0
        self.timestamp = time.time()
    def getRevenue(self):
        return self.value * self.rewards

class statsManager(object):
    def __init__(self):
        self.__selList = list()
        self.__allList = list()
    
    def addPoint(self, coin, data):
        self.__selList.append(statPoint(data['coins'][coin]['tag'], data['coins'][coin]['exchange_rate']*10000, float(data['coins'][coin]['estimated_rewards'])))
        maxKey = str()
        maxvalue = 0.0
        for elem in data['coins']:
            if data['coins'][elem]['tag'] == 'NICEHASH':
                continue
            elif data['coins'][elem]['exchange_rate']*10000*float(data['coins'][elem]['estimated_rewards']) > maxvalue:
                maxvalue = data['coins'][elem]['exchange_rate']*10000*float(data['coins'][elem]['estimated_rewards'])
                maxKey = elem
        self.__allList.append(statPoint(data['coins'][maxKey]['tag'], data['coins'][maxKey]['exchange_rate']*10000, float(data['coins'][maxKey]['estimated_rewards'])))

    def getReport(self, flush=False):
        selVal = dict()
        allVal = dict()
        for elem in self.__selList:
            if not elem.coin in selVal.keys():
                selVal[elem.coin] = [1.0, elem.rewards, elem.getRevenue()]
            else:
                selVal[elem.coin][0] += 1.0
                selVal[elem.coin][1] += elem.rewards
                selVal[elem.coin][2] += elem.getRevenue()
        for elem in self.__allList:
            if not elem.coin in allVal.keys():
                allVal[elem.coin] = [1.0, elem.rewards, elem.getRevenue()]
            else:
                allVal[elem.coin][0] += 1.0
                allVal[elem.coin][1] += elem.rewards
                allVal[elem.coin][2] += elem.getRevenue()
        log = '\033[;1m[' + str(datetime.datetime.now()).split('.')[0] + ']\033[;0m Selected:'
        Total = [0.0, 0.0]
        for key in (sorted(selVal.keys(), key=lambda x: selVal[x][0], reverse=True)):
            Total[0] += selVal[key][0]
            Total[1] += selVal[key][2]
            log += ' \033[1;36m%s\033[;0m:\033[1;31m%.2f\033[;0m:\033[0;32m%.5f:%.5f\033[;0m' % (key, selVal[key][0]*0.025, selVal[key][1], selVal[key][2])

        log += ' \033[1;36mTotal\033[;0m:\033[1;31m%.2f\033[;0m:\033[0;32m%.5f\033[;0m\n' % (Total[0]*0.025, Total[1])

        log += '\033[;1m[' + str(datetime.datetime.now()).split('.')[0] + ']\033[;0m All:'
        Total = [0.0, 0.0]
        for key in (sorted(allVal.keys(), key=lambda x: allVal[x][0], reverse=True)):
            Total[0] += allVal[key][0]
            Total[1] += allVal[key][2]
            log += ' \033[1;36m%s\033[;0m:\033[1;31m%.2f\033[;0m:\033[0;32m%.5f:%.5f\033[;0m' % (key, allVal[key][0]*0.025, allVal[key][1], allVal[key][2])

        log += ' \033[1;36mTotal\033[;0m:\033[1;31m%.2f\033[;0m:\033[0;32m%.5f\033[;0m' % (Total[0]*0.025, Total[1])
        print log

        if flush:
            selVal.clear()
            allVal.clear()
        return log