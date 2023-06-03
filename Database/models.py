from Database.database import Base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer
from sqlalchemy.types import String
from sqlalchemy.types import Date


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String, primary_key=False, nullable=False)
    playertype = Column(String, primary_key=False, nullable=False)
    tournament = Column(Integer, ForeignKey("tournament.id"), nullable=True)
    tournamentWinner = Column(Integer, ForeignKey("tournament.id"), nullable=True)
    match = Column(Integer, ForeignKey("match.id"), nullable=True)
    matchWinner = Column(Integer, ForeignKey("match.id"), nullable=True)


class Tournament(Base):
    __tablename__ = 'tournament'
    id = Column(Integer, primary_key=True, nullable=False)
    game = Column(String, primary_key=False, nullable=False)
    startTime = Column(Date, primary_key=False, nullable=False)
    endTime = Column(Date, primary_key=False, nullable=True)
    players = relationship("players")
    winner = relationship("players")


class Match(Base):
    __tablename__ = "match"
    id = Column(Integer, primary_key=True, nullable=False)
    startTime = Column(Date, primary_key=False, nullable=False)
    endTime = Column(Date, primary_key=False, nullable=True)
    players = relationship("players")
    winner = relationship("players")


class ScoreBoard(Base):
    __tablename__ = "scoreboard"
    id = Column(Integer, primary_key=True, nullable=False)
    tournament = Column(Integer, ForeignKey("tournament.id"), nullable=False)
    player = Column(Integer, ForeignKey("players.id"), nullable=False)
    score = Column(Integer, primary_key=False, nullable=False)
