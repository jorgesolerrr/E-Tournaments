import numpy as np
from .game_interface import IGame

class TicTacToe(IGame):
    def __init__(self):
        super().__init__()
        self.p1 = None
        self.p2 = None
        self.board = None
        
        

    def SetState(self, players, current):
        self.p1 = players[0]
        self.p2 = players[1]
        self.board = np.array([[0, 0, 0],
                               [0, 0, 0],
                               [0, 0, 0]])
        self.current = current

    def GetMoves(self):
        moves = []
        for i in range(np.shape(self.board)[0]):
            for j in range(np.shape(self.board)[1]):
                if self.board[i][j] == 0:
                    moves.append((i, j))
        return moves

    def SetMove(self, move):
        if self.current == self.p1:
            self.board[move[0], move[1]] = 1
            self.current = self.p2
        else:
            self.board[move[0], move[1]] = 2
            self.current = self.p1

    def GameEnd(self):
        if (self.board[0, 0] != 0 and self.board[0, 0] == self.board[0, 1] and self.board[0, 1] == self.board[0, 2]) or (self.board[0, 0] != 0 and self.board[0, 0] == self.board[1, 0] and self.board[1, 0] == self.board[2, 0]) or (self.board[0, 0] != 0 and self.board[0, 0] == self.board[1, 1] and self.board[1, 1] == self.board[2, 2]):
            self.finished = True
            if (self.board[0, 0] == 1):
                self.winners = [self.p1]
            else:
                self.winners = [self.p2]
            return True

        if (self.board[1, 1] != 0 and self.board[0, 1] == self.board[1, 1] and self.board[1, 1] == self.board[2, 1]) or (self.board[1, 1] != 0 and self.board[1, 0] == self.board[1, 1] and self.board[1, 1] == self.board[1, 2]) or (self.board[1, 1] != 0 and self.board[2, 0] == self.board[1, 1] and self.board[1, 1] == self.board[0, 2]):
            self.finished = True
            if (self.board[1, 1] == 1):
                self.winners = [self.p1]
            else:
                self.winners = [self.p2]
            return True

        if (self.board[2, 2] != 0 and self.board[2, 0] == self.board[2, 1] and self.board[2, 1] == self.board[2, 2]) or (self.board[2, 2] != 0 and self.board[2, 2] == self.board[1, 2] and self.board[1, 2] == self.board[0, 2]):
            self.finished = True
            if (self.board[2, 2] == 1):
                self.winners = [self.p1]
            else:
                self.winners = [self.p2]
            return True

        for i in range(np.shape(self.board)[0]):
            for j in range(np.shape(self.board)[1]):
                if self.board[i, j] == 0:
                    return False
        self.finished = True
        return True

    def GetWinners(self):
        return self.winners
