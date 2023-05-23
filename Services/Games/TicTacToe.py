import numpy as np


class TicTacToe:
    def __init__(self):
        self.p1 = None
        self.p2 = None
        self.board = np.array([[0, 0, 0],
                               [0, 0, 0],
                               [0, 0, 0]])
        self.current = None
        self.finished = False
        self.winners = None

    def SetState(self, p1, p2, current, board=np.array([[0, 0, 0], [0, 0, 0], [0, 0, 0]])):
        self.p1 = p1
        self.p2 = p2
        self.board = board
        self.current = current

    def GetMoves(self):
        moves = []
        for i in range(np.shape(board)[0]):
            for j in range(np.shape(board)[1]):
                if board[i][j] == 0:
                    moves.append((i, j))
        return moves

    def SetMoves(self, move):
        if self.current == p1:
            self.board[move[0], move[1]] = 1
            self.current = self.p2
        else:
            self.board[move[0], move[1]] = 2
            self.current = self.p1

    def GameEnd(self):
        if (board[0, 0] == board[0, 1] and board[0, 1] == board[0, 2]) or (board[0, 0] == board[1, 0] and board[1, 0] == board[2, 0]) or (board[0, 0] == board[1, 1] and board[1, 1] == board[2, 2]):
            self.finished = True
            if (board[0, 0] == 1):
                self.winners = [self.p1]
            else:
                self.winners = [self.p2]
            return True

        if (board[0, 1] == board[1, 1] and board[1, 1] == board[2, 1]) or (board[1, 0] == board[1, 1] and board[1, 1] == board[1, 2]) or (board[2, 0] == board[1, 1] and board[1, 1] == board[0, 2]):
            self.finished = True
            if (board[1, 1] == 1):
                self.winners = [self.p1]
            else:
                self.winners = [self.p2]
            return True

        if (board[2, 0] == board[2, 1] and board[2, 1] == board[2, 2]) or (board[2, 2] == board[1, 2] and board[1, 2] == board[0, 2]):
            self.finished = True
            if (board[2, 2] == 1):
                self.winners = [self.p1]
            else:
                self.winners = [self.p2]
            return True

    def GetWinners(self):
        return self.winners
