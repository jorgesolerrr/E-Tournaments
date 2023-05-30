from Games.TicTacToe import TicTacToe
import random

t = TicTacToe()
t.SetState("Jose", "Pancho", "Jose")

while not t.GameEnd():
    m1 = t.GetMoves()
    p1 = random.choice(m1)
    t.SetMoves(p1)


print(t.board)
print(t.winners)
