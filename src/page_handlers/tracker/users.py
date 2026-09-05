from sqlite_utils.db import Table
from datastore.connection import get_db
import hashlib
import secrets
import string
import bcrypt
from dataclasses import dataclass, asdict

@dataclass
class User():
    id: str
    display_name: str
    sha_hashed_peer_key: str
    hashed_password: str
    password_salt: str

def _users_table() -> Table:
    return get_db().table("users")

def _generate_secure_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def _hash_pass(plaintext_pass: str):
    password_bytes = plaintext_pass.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(password_bytes, salt)
    return (salt, hashed_pass)


def create_user(display_name: str, plaintext_password: str):
    """Creates a new user in the system.
    TODO: How are new users created? Invite system?
    """

    pw_parts = _hash_pass(plaintext_password)
    plaintext_peer_key = _generate_secure_string(36)
    hashed_peer = hashlib.sha256(plaintext_peer_key.encode("utf-8")).hexdigest()
    user = User(
        id=_generate_secure_string(12),
        display_name=display_name,
        sha_hashed_peer_key=hashed_peer,
        hashed_password=pw_parts[1],
        password_salt=pw_parts[0]
    )

    table = _users_table()
    table.insert(asdict(user))
    return {
        "plaintext_peer_key": plaintext_peer_key
    }

def get_user_from_key(plaintext_key: str) -> User | None:
    """ Given a plaintext peer key, looks up the user who it belongs to. None if not found."""

    hashed_key = hashlib.sha256(plaintext_key.encode("utf-8")).hexdigest()
    table = _users_table()
    results = table.rows_where(f"sha_hashed_peer_key = {hashed_key}")
    try:
        first = results.__next__()
    except StopIteration:
       return None 
    return User(**first)