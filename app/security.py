from passlib.hash import pbkdf2_sha256

def hash_password(pw: str) -> str:
    """Return a salted PBKDF2-SHA256 hash for storage."""
    return pbkdf2_sha256.hash(pw)

def verify_password(pw: str, hash_: str) -> bool:
    """Check a plain password against a stored PBKDF2-SHA256 hash."""
    return pbkdf2_sha256.verify(pw, hash_)
