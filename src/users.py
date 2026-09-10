from src.datastore.connection import get_db
from enum import Enum
from sqlite_utils.db import Table
import hashlib
import secrets
import string
import bcrypt
from dataclasses import dataclass, asdict

@dataclass
class User():
    id: str
    name: str
    peer_key: str
    hashed_password: str
    password_salt: str
    role: str 

def _users_table() -> Table:
    return get_db().table("users")

def _generate_secure_string(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(characters) for _ in range(length))

def _hash_pass(plaintext_pass: str) -> tuple:
    password_bytes = plaintext_pass.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(password_bytes, salt)
    return (salt, hashed_pass,)

def _hash_pass_with_salt(plaintext_pass: str, salt: bytes) -> tuple:
    password_bytes = plaintext_pass.encode('utf-8')
    hashed_pass = bcrypt.hashpw(password_bytes, salt)
    return (salt, hashed_pass)

class UserRole(Enum):
    ROOT = 'ROOT',
    ADMIN = 'ADMIN',
    USER = 'USER'

def create_user(name: str, plaintext_password: str, role: UserRole):
    pw_parts = _hash_pass(plaintext_password)
    peer_key = _generate_secure_string(36)
    user = User(
        id=_generate_secure_string(12),
        name=name,
        peer_key=peer_key,
        hashed_password=pw_parts[1],
        password_salt=pw_parts[0],
        role=role.name
    )

    table = _users_table()
    table.insert(asdict(user))
    return {
        "id": user.id 
    }

def authenticate_user(name: str, password: str) -> str | None:
    """
    Authenticates a user given their plaintext password. If incorrect, returns none.
    If correct, returns their user ID
    """
    table = _users_table()
    possible_users = table.rows_where("name=?", [name])
    for user in possible_users:
        hashed_pass = _hash_pass_with_salt(password, user['password_salt'])
        if hashed_pass[1] == user['hashed_password']:
            return user['id']
    return None



def root_user_check():
    table = _users_table()
    results = table.rows_where("role = 'ROOT'")
    number_of_existing = len([x for x in results])
    if number_of_existing > 1:
        raise Exception("Only 1 root user expected!")
    elif number_of_existing == 0:
        create_user("root", "changeme", UserRole.ROOT)

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