import os
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData, DateTime
from datetime import datetime

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///analytics.db")
engine = create_engine(DATABASE_URL)
metadata = MetaData()

analysis_log = Table("analysis_log", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_id", String),
    Column("feature", String),
    Column("confidence", Float),
    Column("timestamp", DateTime),
)

metadata.create_all(engine)

def log_event(user_id: str, feature: str, confidence: float):
    with engine.connect() as conn:
        conn.execute(
            analysis_log.insert().values(
                user_id=user_id,
                feature=feature,
                confidence=confidence,
                timestamp=datetime.utcnow()
            )
        )
