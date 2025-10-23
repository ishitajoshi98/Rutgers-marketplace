import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Load env vars from .env at project root
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL missing in .env")

# Create engine; pool_pre_ping avoids stale connections
engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, echo=False)

# Scoped session factory: call Session() to get a session; remember to close()
Session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))
