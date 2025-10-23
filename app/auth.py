from typing import Optional, Tuple
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from app.db import Session
from app.models import User
from app.security import hash_password, verify_password

RUTGERS_DOMAINS = ("@rutgers.edu", "@scarletmail.rutgers.edu")

def is_rutgers_email(email: str) -> bool:
    e = (email or "").strip().lower()
    return e.endswith(RUTGERS_DOMAINS)

def register_user(name: str, email: str, password: str) -> Tuple[bool, str]:
    """
    Create a user with hashed password; returns (ok, message).
    """
    name = (name or "").strip()
    email = (email or "").strip().lower()
    if not name:
        return False, "Name is required."
    if not is_rutgers_email(email):
        return False, "Please use a Rutgers email (@rutgers.edu or @scarletmail.edu)."
    if not password or len(password) < 6:
        return False, "Password must be at least 6 characters."

    s = Session()
    try:
        # check if email already exists
        existing = s.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if existing:
            return False, "An account with this email already exists."

        u = User(
            name=name,
            email=email,
            password_hash=hash_password(password),
        )
        s.add(u)
        s.commit()
        return True, "Account created. You can now log in."
    except IntegrityError:
        s.rollback()
        return False, "That email is already registered."
    finally:
        s.close()

def authenticate_user(email: str, password: str) -> Optional[User]:
    """
    Return the user if credentials are valid, else None.
    """
    email = (email or "").strip().lower()
    if not email or not password:
        return None

    s = Session()
    try:
        u = s.execute(select(User).where(User.email == email)).scalar_one_or_none()
        if not u:
            return None
        if not verify_password(password, u.password_hash):
            return None
        return u
    finally:
        s.close()
