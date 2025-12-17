# import os
# from dotenv import load_dotenv
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, scoped_session

# # Load env vars from .env at project root
# load_dotenv()
# DATABASE_URL = os.getenv("DATABASE_URL")
# if not DATABASE_URL:
#     raise RuntimeError("DATABASE_URL missing in .env")

# # Create engine; pool_pre_ping avoids stale connections
# engine = create_engine(DATABASE_URL, future=True, pool_pre_ping=True, echo=False)

# # Scoped session factory: call Session() to get a session; remember to close()
# Session = scoped_session(sessionmaker(bind=engine, autoflush=False, autocommit=False))


# app/db.py
import os
from urllib.parse import urlparse

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import streamlit as st  # we are in a Streamlit app, this is fine

# Load local .env for local dev (optional)
load_dotenv()

# 1. Prefer DATABASE_URL from env (local dev)
DATABASE_URL = os.getenv("DATABASE_URL")

# 2. If not set, fall back to Streamlit secrets (Cloud)
if not DATABASE_URL:
    DATABASE_URL = st.secrets.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in env or Streamlit secrets")

# Debug: show which host we’re actually hitting (no password)
parsed = urlparse(DATABASE_URL)
host = parsed.hostname
st.write(f"DB host in use: {host}")

# Create engine; Supabase requires SSL but SQLAlchemy + psycopg2
# will negotiate this automatically with the URL.
engine = create_engine(
    DATABASE_URL,
    future=True,
    pool_pre_ping=True,
    echo=False,
)

Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
