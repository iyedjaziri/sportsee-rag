from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class PlayerStatsSQL(Base):
    __tablename__ = "player_stats"

    id = Column(Integer, primary_key=True, index=True)
    player = Column(String, index=True)
    team = Column(String)
    age = Column(Integer)
    gp = Column(Integer)
    w = Column(Integer)
    l = Column(Integer)
    min = Column(Float)
    pts = Column(Float)
    fgm = Column(Float)
    fga = Column(Float)
    fg_pct = Column(Float)
    three_pm = Column(Float)
    three_pa = Column(Float)
    three_p_pct = Column(Float)
    ftm = Column(Float)
    fta = Column(Float)
    ft_pct = Column(Float)
    oreb = Column(Float)
    dreb = Column(Float)
    reb = Column(Float)
    ast = Column(Float)
    tov = Column(Float)
    stl = Column(Float)
    blk = Column(Float)
    pf = Column(Float)
    plus_minus = Column(Float)
