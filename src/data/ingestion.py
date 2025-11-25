import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.core.config import settings
from src.core.logging import logger
from src.data.schemas import PlayerStats
from src.data.models import Base, PlayerStatsSQL
import datetime

def ingest_data(file_path: str):
    """
    Reads Excel file, validates with Pydantic, and saves to SQLite.
    """
    logger.info(f"Reading data from {file_path}...")
    
    # Read Excel, header is at index 1 (row 2)
    try:
        df = pd.read_excel(file_path, header=1)
    except Exception as e:
        logger.error(f"Failed to read Excel: {e}")
        raise

    # Rename the weird 3PM column
    # It usually comes as datetime.time(15, 0) which is 3PM
    # We need to find this column and rename it to "3PM"
    
    new_columns = {}
    for col in df.columns:
        if isinstance(col, datetime.time) and col.hour == 15 and col.minute == 0:
            new_columns[col] = "3PM"
    
    if new_columns:
        df = df.rename(columns=new_columns)
        logger.info(f"Renamed columns: {new_columns}")

    # Database Setup
    engine = create_engine(settings.DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    logger.info("Validating and inserting records...")
    valid_count = 0
    errors = []

    for index, row in df.iterrows():
        try:
            # Convert row to dict, handle NaN
            row_dict = row.to_dict()
            
            # Pydantic Validation
            player_data = PlayerStats(**row_dict)
            
            # Map to SQL Model
            db_player = PlayerStatsSQL(
                player=player_data.player,
                team=player_data.team,
                age=player_data.age,
                gp=player_data.gp,
                w=player_data.w,
                l=player_data.l,
                min=player_data.min,
                pts=player_data.pts,
                fgm=player_data.fgm,
                fga=player_data.fga,
                fg_pct=player_data.fg_pct,
                three_pm=player_data.three_pm,
                three_pa=player_data.three_pa,
                three_p_pct=player_data.three_p_pct,
                ftm=player_data.ftm,
                fta=player_data.fta,
                ft_pct=player_data.ft_pct,
                oreb=player_data.oreb,
                dreb=player_data.dreb,
                reb=player_data.reb,
                ast=player_data.ast,
                tov=player_data.tov,
                stl=player_data.stl,
                blk=player_data.blk,
                pf=player_data.pf,
                plus_minus=player_data.plus_minus
            )
            
            session.add(db_player)
            valid_count += 1
            
        except Exception as e:
            errors.append(f"Row {index}: {e}")
            # logger.warning(f"Validation error at row {index}: {e}")

    session.commit()
    session.close()
    
    logger.info(f"Successfully inserted {valid_count} records.")
    if errors:
        logger.warning(f"Encountered {len(errors)} errors. First 5: {errors[:5]}")
