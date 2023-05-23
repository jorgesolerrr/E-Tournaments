class TicTacToe:
    def __init__(self):
        self.p1 = None
        self.p2 = None
        self.board = [[0, 0, 0],
                      [0, 0, 0],
                      [0, 0, 0]]
        self.current = None

    def SetState(p1, p2, current, board=[[0, 0, 0], [0, 0, 0], [0, 0, 0]]):
        self.p1 = p1
        self.p2 = p2
        self.board = board
        self.current = current
