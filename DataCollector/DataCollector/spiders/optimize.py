from operator import itemgetter

class playerSort(object):
    def __init__(self, playerList):
        playerList = sorted(playerList, key=itemgetter('projection'), reverse=True)
        self.positionList = set( [player['position'] for player in playerList] )
        self.byPosition = {}
        self.prunedByPosition = {}
        for pos in self.positionList:
            self.byPosition[pos] = [ player for player in playerList if player['position'] == pos ]
            for i, player in enumerate(self.byPosition[pos]):
                if i == 0:
                    self.prunedByPosition[pos] = [ player ]
                    lastSalary = player['salary']
                    lastProjection = player['projection']
                elif ( player['salary'] < lastSalary ) and ( player['projection'] > 0 ):
                    self.prunedByPosition[pos].append(player)
                    lastSalary = player['salary']
                    lastProjection = player['projection']       