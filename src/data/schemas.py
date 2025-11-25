from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import Optional
import datetime

class PlayerStats(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    player: str = Field(alias="Player")
    team: str = Field(alias="Team")
    age: int = Field(alias="Age")
    gp: int = Field(alias="GP")
    w: int = Field(alias="W")
    l: int = Field(alias="L")
    min: float = Field(alias="Min")
    pts: float = Field(alias="PTS")
    fgm: float = Field(alias="FGM")
    fga: float = Field(alias="FGA")
    fg_pct: float = Field(alias="FG%")
    
    # Handle the weird 3PM column which might be datetime or string
    three_pm: float = Field(alias="3PM") 
    
    three_pa: float = Field(alias="3PA")
    three_p_pct: float = Field(alias="3P%")
    ftm: float = Field(alias="FTM")
    fta: float = Field(alias="FTA")
    ft_pct: float = Field(alias="FT%")
    oreb: float = Field(alias="OREB")
    dreb: float = Field(alias="DREB")
    reb: float = Field(alias="REB")
    ast: float = Field(alias="AST")
    tov: float = Field(alias="TOV")
    stl: float = Field(alias="STL")
    blk: float = Field(alias="BLK")
    pf: float = Field(alias="PF")
    plus_minus: float = Field(alias="+/-")
    
    @field_validator('three_pm', mode='before')
    @classmethod
    def parse_three_pm(cls, v):
        # Fix for the weird datetime issue in Excel
        if isinstance(v, datetime.time):
            # If it's 15:00:00, it might mean 3.0? Or is it column index?
            # Actually, looking at the header list: 'datetime.time(15, 0)' was the HEADER name.
            # The values are likely floats.
            # But we need to alias the field correctly.
            # If the header is weird, we handle it in ingestion.
            return float(v)
        return v

class PlayerStatsCreate(PlayerStats):
    pass

class PlayerStatsDB(PlayerStats):
    id: int
