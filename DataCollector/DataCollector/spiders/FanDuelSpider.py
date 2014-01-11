from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
from scrapy.http import FormRequest
import re
import itertools
import time
from math import *
from optimize import *
from Numberjack import *

from DataCollector.items import PlayerItem

class FanDuelSpider(BaseSpider):
    name = "FanDuelNBA"
    allowed_domains = ["fanduel.com", "numberfire.com"]
    start_urls = ["https://www.fanduel.com/nextnbagame"]

    def parse(self, response):

        sel = Selector(response)
        fanDuelAllPlayerData = sel.xpath('//script/text()').re('FD\.playerpicker\.allPlayersFullData \= \{(.*)\}')
        fanDuelAllPlayerData = re.findall(r"\[([^\]]+)\]", fanDuelAllPlayerData[0])

        players = []
        for playerFullData in fanDuelAllPlayerData:
            player = PlayerItem()
            playerFullData = playerFullData.split(',')
            player['name'] = playerFullData[1].strip(' "\'\t\r\n')
            player['position'] = playerFullData[0].strip(' "\'\t\r\n')
            player['salary'] = int(playerFullData[5].strip(' "\'\t\r\n'))
            player['projection'] = 0
            
            players.append(player)
        print "NUMBER OF PLAYERS: " + str(len(players))
        request = Request("https://www.numberfire.com/nba/fantasy/fantasy-basketball-projections", callback=self.parseNumberFire)
        request.meta['players'] = players
        return request

    def parseNumberFire(self, response):

        alias = {'Bradley Beal' : 'Brad Beal', 'Phil Pressey' : 'Phil (Flip) Pressey', 'Viacheslav Kravtsov' : 'Vyacheslav Kravtsov', 'MarShon Brooks' : 'Marshon Brooks'}
        notFound = []
        
        players = response.meta['players']
        nameIndexer = dict((p['name'], i) for i, p in enumerate(players))

        sel = Selector(response)
        numberfireData = sel.xpath('//script/text()')

        allPlayersNameID = numberfireData.re('"id":"([^"]+","name":"[^"]+)","slug"')
        dictNameID = dict(NameID.split('","name":"') for NameID in allPlayersNameID)

        allPlayersData = numberfireData.re('(\{"nba_player_id[^\}]+)\}')

        for playerData in allPlayersData:

            playerID = re.search('(?<=nba_player_id":")([^"]+)', playerData).group(0)
            playerName = dictNameID[playerID]
            index = nameIndexer.get(playerName, -1)
            if index == -1:
                try:
                    playerName = alias[playerName]
                    index = nameIndexer.get(playerName, -1)
                except:
                    notFound.append(dictNameID[playerID])
            else:
                players[index]['projection'] = float(re.search('(?<="fanduel_fp":)([^,]+)', playerData).group(0))

        print "Double check that these players aren't available for tonight's game:"
        print notFound

        players = playerSort(players)
        self.optimize(['Mistral'], players)

    def optimize(self, libs, players):

        PGs = players.prunedByPosition['PG']
        PGprojection = [ int(player['projection']*100) for player in players.prunedByPosition['PG']]
        PGsalary = [ int(player['salary']) for player in players.prunedByPosition['PG']]
        SGs = players.prunedByPosition['SG']
        SGprojection = [ int(player['projection']*100) for player in players.prunedByPosition['SG']]
        SGsalary = [ int(player['salary']) for player in players.prunedByPosition['SG']]

        PFs = players.prunedByPosition['PF']
        PFprojection = [ int(player['projection']*100) for player in players.prunedByPosition['PF']]
        PFsalary = [ int(player['salary']) for player in players.prunedByPosition['PF']]
        SFs = players.prunedByPosition['SF']
        SFprojection = [ int(player['projection']*100) for player in players.prunedByPosition['SF']]
        SFsalary = [ int(player['salary']) for player in players.prunedByPosition['SF']]

        Cs = players.prunedByPosition['C']
        Cprojection = [ int(player['projection']*100) for player in players.prunedByPosition['C']]
        Csalary = [ int(player['salary']) for player in players.prunedByPosition['C']]

        PG = VarArray(len(PGs))
        SG = VarArray(len(SGs))
        PF = VarArray(len(PFs))
        SF = VarArray(len(SFs))
        C = VarArray(len(Cs))


        salaryCap = 60000
        totalSalary = Variable(0, 1000000)
        totalProjection = Variable(0, 1000000)

        model = Model(
            Sum(PG) == 2,
            Sum(SG) == 2,
            Sum(PF) == 2,
            Sum(SF) == 2,
            Sum(C) == 1,
            Sum(PG, PGprojection) + Sum(SG, SGprojection) + Sum(PF, PFprojection) + Sum(SF, SFprojection) + Sum(C, Cprojection) == totalProjection,
            Sum(PG, PGsalary) + Sum(SG, SGsalary) + Sum(PF, PFsalary) + Sum(SF, SFsalary) + Sum(C, Csalary) == totalSalary,
            totalSalary <= salaryCap,
            Maximise(totalProjection)
            )

        for library in libs:
            
            solver = model.load(library) # Load up model into solver
            solver.setVerbosity(1)
            solver.setTimeLimit(600)
            solver.setHeuristic('MinDomain', 'Random', 10)

            solver.solve() # Now Solve
            
            roster = self.buildRoster(PGs, PG, SGs, SG, PFs, PF, SFs, SF, Cs, C)
            print ''
            for player in roster:
                print player['position'] + ":\t" + player['name'] + "\t Projection: " + str(player['projection']) + "\t Salary: " + str(player['salary'])
            rosterProjection = sum([ player['projection'] for player in roster ])
            print ''
            print 'Team Totals'
            print 'Projection:', rosterProjection, ' Salary: $', totalSalary.solution()
            print ''

    def buildRoster(self, PGs, PG, SGs, SG, PFs, PF, SFs, SF, Cs, C):
        roster = []
        PG = re.sub('\[|\]', '', PG.solution())
        PG = PG.split(',')
        for index, boolean in enumerate(PG):
            if int(boolean) == 1:
                roster.append(PGs[index]) 
        SG = re.sub('\[|\]', '', SG.solution())
        SG = SG.split(',')
        for index, boolean in enumerate(SG):
            if int(boolean) == 1:
                roster.append(SGs[index]) 
        PF = re.sub('\[|\]', '', PF.solution())
        PF = PF.split(',')
        for index, boolean in enumerate(PF):
            if int(boolean) == 1:
                roster.append(PFs[index]) 
        SF = re.sub('\[|\]', '', SF.solution())
        SF = SF.split(',')
        for index, boolean in enumerate(SF):
            if int(boolean) == 1:
                roster.append(SFs[index]) 
        C = re.sub('\[|\]', '', C.solution())
        C = C.split(',')
        for index, boolean in enumerate(C):
            if int(boolean) == 1:
                roster.append(Cs[index]) 

        return roster 