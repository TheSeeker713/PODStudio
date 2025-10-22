"""
Database Setup - SQLite + SQLModel
Schema: Asset, Job, Pack, Settings

TODO (Step 2+): Define SQLModel models and engine setup
"""

from sqlmodel import create_engine

# Placeholder engine
DATABASE_URL = "sqlite:///./podstudio.db"
engine = create_engine(DATABASE_URL, echo=False)
