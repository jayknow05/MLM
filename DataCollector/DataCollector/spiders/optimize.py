from operator import itemgetter

def optimizeRoster(players):
    players = playerSort(players)
    players.gradient(20000)
    print players.byPosition['PG'][10]
    # print gradient(players.pg, 10000, 0)

class Roster(object):
    def __init__(self, players):
        self.players = players
        self.pg = [ players[1], players[2] ]
        self.sg = [ players[3], players[4] ]
        self.pf = [ players[5], players[6] ]
        self.sf = [ players[7], players[8] ]
        self.c = players[9]
    def salary(self):
        return sum( [ player['salary'] for player in self.players ] )
    def projection(self):
        return sum( [ player['projection'] for player in self.players ] )
    def margin(self, salaryCap):
        return self.salary() - salaryCap

class playerSort(object):
    def __init__(self, playerList):
        playerList = sorted(playerList, key=itemgetter('projection'), reverse=True)
        self.positionList = set( [player['position'] for player in playerList] )
        self.byPosition = {}
        for pos in self.positionList:
            self.byPosition[pos] = [ player for player in playerList if player['position'] == pos ]

    def gradient(self, capMargin):
    
        byPlayer = {}
       
        for pos in self.positionList:
            
            for currPlayer in self.byPosition[pos]:
                for nextPlayer in self.byPosition[pos]:

                    s1 = nextPlayer['salary']
                    s2 = currPlayer['salary']
                    
                    if abs(capMargin) < abs(s1 - s2):
                        salarySaved = capMargin
                    else:
                        salarySaved = s1 - s2

                    p1 = nextPlayer['projection']
                    p2 = currPlayer['projection']

                    pointCost = p1 - p2
                    if pointCost == 0:
                        pointCost = 0.0001

                    gradient = salarySaved/pointCost
                    currPlayer['gradient'].append(gradient)        