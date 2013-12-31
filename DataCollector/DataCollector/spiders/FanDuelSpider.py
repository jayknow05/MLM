from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.http import FormRequest
import re
import itertools

from operator import itemgetter

from DataCollector.items import PlayerItem

class FanDuelSpider(BaseSpider):
    name = "FanDuelNBA"
    allowed_domains = ["fanduel.com"]
    start_urls = [
        "https://www.fanduel.com/nextnbagame"
    ]

    def parse(self, response):
        
        sel = Selector(response)
        allPlayersFullData = sel.xpath('//script/text()').re('FD\.playerpicker\.allPlayersFullData \= \{(.*)\}')
        allPlayersFullData = re.findall(r"\[([^\]]+)\]", allPlayersFullData[0])

        players = []
        PGs = []
        SGs = []
        SFs = []
        PFs = []
        Cs = []

        for playerFullData in allPlayersFullData:
            player = PlayerItem()
            playerFullData = playerFullData.split(',')
            player['name'] = playerFullData[1].strip(' "\'\t\r\n')
            player['position'] = playerFullData[0].strip(' "\'\t\r\n')
            player['salary'] = int(playerFullData[5].strip(' "\'\t\r\n'))
            player['average'] = float(playerFullData[6].strip(' "\'\t\r\n'))
            
            pos = player['position']

            if pos == 'PG':
                PGs.append(player)
            elif pos == 'SG':
                SGs.append(player)
            elif pos == 'SF':
                SFs.append(player)
            elif pos == 'PF':
                PFs.append(player)
            elif pos == 'C':
                Cs.append(player)
            # else:
            #     continue

            players.append(player)

        prunedPGs = self.analyzePlayers(PGs) 
        prunedSGs = self.analyzePlayers(SGs) 
        prunedSFs = self.analyzePlayers(SFs) 
        prunedPFs = self.analyzePlayers(PFs) 
        prunedCs = self.analyzePlayers(Cs)

        PG1 = prunedPGs.pop(0)
        PG2 = prunedPGs.pop(0)
        SG1 = prunedSGs.pop(0)
        SG2 = prunedSGs.pop(0)
        SF1 = prunedSFs.pop(0)
        SF2 = prunedSFs.pop(0)
        PF1 = prunedPFs.pop(0)
        PF2 = prunedPFs.pop(0)
        C = prunedCs.pop(0)

        nextPG = prunedPGs.pop(0)
        nextSG = prunedSGs.pop(0)
        nextSF = prunedSFs.pop(0)
        nextPF = prunedPFs.pop(0)
        nextC = prunedCs.pop(0)

        totalSalary = PG1['salary'] + PG2['salary'] + SG1['salary'] + SG2['salary'] + SF1['salary'] + SF2['salary'] + PF1['salary'] + PF2['salary'] + C['salary'] 

        gradientList = [( PG1['salary'] - nextPG['salary']) / (PG1['average'] - nextPG['average']), (PG2['salary'] - nextPG['salary']) / (PG2['average'] - nextPG['average']), ( SG1['salary'] - nextSG['salary']) / (SG1['average'] - nextSG['average']), (SG2['salary'] - nextSG['salary']) / (SG2['average'] - nextSG['average']), ( SF1['salary'] - nextSF['salary']) / (SF1['average'] - nextSF['average']), (SF2['salary'] - nextSF['salary']) / (SF2['average'] - nextSF['average']), ( PF1['salary'] - nextPF['salary']) / (PF1['average'] - nextPF['average']), (PF2['salary'] - nextPF['salary']) / (PF2['average'] - nextPF['average']), (C['salary'] - nextC['salary']) / (C['average'] - nextC['average']) ]


        salaryCap = 60000

        while totalSalary > salaryCap:
            margin = totalSalary - salaryCap
            print margin
            print gradientList
            for gradient in gradientList:
                if gradient >=margin:
                    print "we got an opportunity here!"

            bestOption = gradientList.index(max(gradientList))
            if bestOption == 0:
                PG1 = nextPG
                nextPG = prunedPGs.pop(0)
                gradientList[0] = ( PG1['salary'] - nextPG['salary']) / (PG1['average'] - nextPG['average'])
                gradientList[1] = ( PG2['salary'] - nextPG['salary']) / (PG2['average'] - nextPG['average'])
            elif bestOption == 1:
                PG2 = nextPG
                nextPG = prunedPGs.pop(0)
                gradientList[0] = ( PG1['salary'] - nextPG['salary']) / (PG1['average'] - nextPG['average'])
                gradientList[1] = ( PG2['salary'] - nextPG['salary']) / (PG2['average'] - nextPG['average'])
            elif bestOption == 2:
                SG1 = nextSG
                nextSG = prunedSGs.pop(0)
                gradientList[2] = ( SG1['salary'] - nextSG['salary']) / (SG1['average'] - nextSG['average'])
                gradientList[3] = ( SG2['salary'] - nextSG['salary']) / (SG2['average'] - nextSG['average'])
            elif bestOption == 3:
                SG2 = nextSG
                nextSG = prunedSGs.pop(0)
                gradientList[2] = ( SG1['salary'] - nextSG['salary']) / (SG1['average'] - nextSG['average'])
                gradientList[3] = ( SG2['salary'] - nextSG['salary']) / (SG2['average'] - nextSG['average'])
            elif bestOption == 4:
                SF1 = nextSF
                nextSF = prunedSFs.pop(0)
                gradientList[4] = ( SF1['salary'] - nextSF['salary']) / (SF1['average'] - nextSF['average'])
                gradientList[5] = ( SF2['salary'] - nextSF['salary']) / (SF2['average'] - nextSF['average'])
            elif bestOption == 5:
                SF2 = nextSF
                nextSF = prunedSFs.pop(0)
                gradientList[4] = ( SF1['salary'] - nextSF['salary']) / (SF1['average'] - nextSF['average'])
                gradientList[5] = ( SF2['salary'] - nextSF['salary']) / (SF2['average'] - nextSF['average'])          
            elif bestOption == 6:
                PF1 = nextPF
                nextPF = prunedPFs.pop(0)
                gradientList[6] = ( PF1['salary'] - nextPF['salary']) / (PF1['average'] - nextPF['average'])
                gradientList[7] = ( PF2['salary'] - nextPF['salary']) / (PF2['average'] - nextPF['average'])           
            elif bestOption == 7:
                PF2 = nextPF
                nextPF = prunedPFs.pop(0)
                gradientList[6] = ( PF1['salary'] - nextPF['salary']) / (PF1['average'] - nextPF['average'])
                gradientList[7] = ( PF2['salary'] - nextPF['salary']) / (PF2['average'] - nextPF['average'])                  
            else:
                C = nextC
                nextC = prunedCs.pop(0)
                gradientList[8] = ( C['salary'] - nextC['salary']) / (C['average'] - nextC['average'])          
         

            totalSalary = PG1['salary'] + PG2['salary'] + SG1['salary'] + SG2['salary'] + SF1['salary'] + SF2['salary'] + PF1['salary'] + PF2['salary'] + C['salary']
    
        totalScore = PG1['average'] + PG2['average'] + SG1['average'] + SG2['average'] + SF1['average'] + SF2['average'] + PF1['average'] + PF2['average'] + C['average']
        
        print PG1
        print PG2
        print SG1
        print SG2
        print SF1
        print SF2
        print PF1
        print PF2
        print C    
        print "Total salary: $" + str(totalSalary) + " out of a possible $" + str(salaryCap)  
        print "Average total score: " + str(totalScore)  

    def analyzePlayers(self, playerList):
        sortedPlayerList = sorted(playerList, key=itemgetter('average'), reverse=True)
        prunedPlayerList = []

        for player in sortedPlayerList:
            try:
                if lastSalary <= player['salary']:
                    # print "Removing " + player['name'] + " in favor of " + lastPlayer
                    continue
                else:
                    if lastAverage == player['average']:
                        del prunedPlayerList[-1]
                    prunedPlayerList.append(player)
                    lastSalary = player['salary']
                    lastAverage = player['average']
            except:
                prunedPlayerList.append(player)
                lastSalary = player['salary']
                lastAverage = player['average']

        return prunedPlayerList
