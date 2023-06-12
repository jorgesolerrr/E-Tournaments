# import socket
# import docker
# from os import getcwd
# from Tournaments import League
# from tools import Player_Schema, Game_Schema

# game = Game_Schema(amount_players=2, name="TicTacToe")

# players = []

# for i in range(5):
#     players.append(Player_Schema(id=i, type="random"))


# l = League("LaLiga", game, "league", players)

# l.CreateTournamentEnv(2, [5020,5021])

# c = docker.from_env()
# print(c.containers.list())

