"""
Implement your AI here
Do not change the API signatures for _init_ or _call_
_call_ must return a valid action
"""
import numpy as np
import gomoku as gm

class Submission:
    def __init__(self, boardSize, winSize):
        self.boardSize = boardSize
        self.winSize = winSize
        self.enhancedGomoku = EnhancedGomoku(boardSize, winSize)

    def __call__(self, state):
        return self.getBestPossibleMove(state)
    
    def isWithinCenterRange(self, row, column, mid, midRange):
        return abs(row - mid) <= midRange and abs(column - mid) <= midRange

    def getBestPossibleMove(self, state):
        minPlayer = gm.MIN
        maxPlayer = gm.MAX
        bestScore = -np.inf
        bestMove = None

        # action = state.valid_actions()
        priorityActionList = self.getPriorityActions(state)

        for row, column in priorityActionList:
            if CheckIfPostionIsOccupied(gm.EMPTY, state, row, column):

                self.setBoardState(state, minPlayer, row, column, 1)
                minPlayerScore = self.enhancedGomoku.getCurrentPlayerScore(state, minPlayer) 
                maxPlayerScore = self.enhancedGomoku.getCurrentPlayerScore(state, maxPlayer)
                overallScore = minPlayerScore - maxPlayerScore
                self.setBoardState(state, minPlayer, row, column, 0)

                if overallScore > bestScore:
                    bestScore = overallScore
                    bestMove = (row, column)

        return bestMove

    def setBoardState(self, state, minPlayer, row, column, bit):
        state.board[minPlayer, row, column] = bit

    def getPriorityActions(self, state):
        actionsList = []
        
        for row in range(self.boardSize):
            for column in range(self.boardSize):
                self.CheckCentreRegion(state, actionsList, row, column)

        return [idx for idx, _ in sorted(actionsList, key = lambda y: y[1], reverse = True)]

    def CheckCentreRegion(self, state, actionsList, row, column):
        mid = 7
        midRange = 3

        if CheckIfPostionIsOccupied(gm.EMPTY, state, row, column):
            order = 0
            if self.isWithinCenterRange(row, column, mid, midRange):
                order += 1
            actionsList.append(((row, column), order))

class EnhancedGomoku:

    def __init__(self, boardSize, winSize):
        self.boardSize = boardSize
        self.winSize = winSize

    def getCurrentPlayerScore(self, state, player):
        playerScore = 0

        for row in range(self.boardSize):
            for column in range(self.boardSize):
                if state.board[player, row, column] == 1:
                    playerScore += self.checkForPatterns(state, player, row, column)
        
        return playerScore

    def checkForPatterns(self, state, player, row, column):
        possibleDirectionToCheck = [(1, 0), (0, 1), (1, 1), (1, -1)]
        totalScore = 0

        for dRow, dColumn in possibleDirectionToCheck:
            lineScore, openEndScore = self.evaluateScore(state, player, row, column, dRow, dColumn)
            totalScore += self.advancedEvaluation(lineScore, openEndScore)
        
        return totalScore

    def evaluateScore(self, state, player, row, column, dRow, dColumn):
        lineScore = 0
        openEndScore = 0
        lineScore, openEndScore =   self.checkSpacesForward(
            state, player, row, column, dRow, dColumn, lineScore, openEndScore)
        lineScore, openEndScore = self.checkSpacesBackwards(
            state, player, row, column, dRow, dColumn, lineScore, openEndScore)

        return lineScore, openEndScore

    def checkSpacesBackwards(
            self, state, player, row, column, dRow, dColumn, lineScore, openEndScore):
        for i in range(1, self.winSize):
            nextRow, nextColumn = row - (i * dRow), column - (i * dColumn)
            if self.checkIfGoingOutOfBound(nextRow, nextColumn):
                break
            if CheckIfPostionIsOccupied(player, state, nextRow, nextColumn):
                lineScore += 1
            elif CheckIfPostionIsOccupied(gm.EMPTY, state, nextRow, nextColumn):
                openEndScore += 1
                break
            else:
                break
        return lineScore, openEndScore


    def checkSpacesForward(
            self, state, player, row, column, dRow, dColumn, lineScore, openEndScore):
        for i in range(1, self.winSize):
            nextRow, nextColumn = row + (i * dRow), column + (i * dColumn)
            if self.checkIfGoingOutOfBound(nextRow, nextColumn):
                break
            if CheckIfPostionIsOccupied(player, state, nextRow, nextColumn):
                lineScore += 1
            elif CheckIfPostionIsOccupied(gm.EMPTY, state, nextRow, nextColumn):  
                openEndScore += 1
                break
            else:
                break
        return lineScore, openEndScore
    
    def checkIfGoingOutOfBound(self, nextrow, nextColumn):
        return not (0 <= nextrow < self.boardSize 
            and 0 <= nextColumn < self.boardSize)

    def advancedEvaluation(self, lineScore, openEndScore):
        winSize = self.winSize
        if lineScore >= winSize - 1:
            return np.inf
        elif lineScore == winSize - 2:
            if openEndScore == 2:
                return 20000
            elif openEndScore == 1:
                return 10000
            else:
                return openEndScore
        elif lineScore >= 2:
            score = 1000 * lineScore
            if openEndScore:
                score *= 2 
            return score
        else:
            return openEndScore
        
def CheckIfPostionIsOccupied(player, state, row, column):
    return state.board[player, row, column] == 1
