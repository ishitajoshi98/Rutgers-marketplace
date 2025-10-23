import os
import uuid
from typing import Tuple

ALLOWED_EXTS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_BYTES = 5 * 1024 * 1024  # 5 MB

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def save_uploaded_image(uploaded_file, upload_root: str, user_id: str) -> Tuple[bool, str]:
    """
    Save a Streamlit UploadedFile to disk under uploads/<user_id>/<uuid>.<ext>.
    Returns (ok, relative_path_or_error).
    """
    if uploaded_file is None:
        return False, "No file provided."

    filename = uploaded_file.name or ""
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTS:
        return False, f"Unsupported file type: {ext or 'unknown'}. Allowed: {', '.join(sorted(ALLOWED_EXTS))}"

    # read bytes once
    data = uploaded_file.read()
    if not data:
        return False, "Empty file."
    if len(data) > MAX_BYTES:
        return False, f"File too large ({len(data)} bytes). Max allowed is {MAX_BYTES} bytes."

    # build target path
    user_dir = os.path.join(upload_root, str(user_id))
    ensure_dir(user_dir)
    unique_name = f"{uuid.uuid4().hex}{ext}"
    abs_path = os.path.join(user_dir, unique_name)

    # write
    try:
        with open(abs_path, "wb") as f:
            f.write(data)
    except Exception as e:
        return False, f"Failed to save file: {e}"

    # return relative path stored in DB (normalized with forward slashes)
    rel_path = os.path.relpath(abs_path, start=upload_root).replace("\\", "/")
    return True, rel_path
