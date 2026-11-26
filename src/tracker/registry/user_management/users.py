import re
from shared_utils.app_logging import get_logger
from tracker.InvalidUserInputError import InvalidUserInputError
from tracker.datastore.connection import get_db
from enum import Enum
from sqlite_utils.db import Table, NotFoundError
import hashlib
import secrets
import string
import bcrypt
from dataclasses import dataclass, asdict

from tracker.registry.validation import FieldValidatorBuilder, validate_chain

_logger = get_logger("users")


@dataclass
class User:
    id: str
    name: str
    peer_key: str
    hashed_password: str
    password_salt: str
    role: str
    created_by: str


_user_name_validator = FieldValidatorBuilder("username").length(1, 25).matches_regex("^[a-zA-Z0-9]+$", "Lower case letters, upper case letters, and numbers only").build()
_password_validator = FieldValidatorBuilder("password").length(12, 30).build()

def _users_table() -> Table:
    return get_db().table("users")


def _generate_secure_string(length):
    characters = string.ascii_letters + string.digits
    return "".join(secrets.choice(characters) for _ in range(length))


def _hash_pass(plaintext_pass: str) -> tuple:
    password_bytes = plaintext_pass.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_pass = bcrypt.hashpw(password_bytes, salt)
    return (
        salt,
        hashed_pass,
    )


def _hash_pass_with_salt(plaintext_pass: str, salt: bytes) -> tuple:
    password_bytes = plaintext_pass.encode("utf-8")
    hashed_pass = bcrypt.hashpw(password_bytes, salt)
    return (salt, hashed_pass)


class UserRole(Enum):
    ROOT = ("ROOT",)
    ADMIN = ("ADMIN",)
    USER = "USER"


def create_user(
    name: str, plaintext_password: str, role: UserRole, created_by: str
) -> str | InvalidUserInputError:
    """
    Creates a new user account. returns the ID of the new user
    """

    possible_validation_error = validate_chain((
        _user_name_validator(name),
        _password_validator(plaintext_password)
    ))

    if possible_validation_error is not None:
        return possible_validation_error
    
    pw_parts = _hash_pass(plaintext_password)
    peer_key = _generate_secure_string(36)
    user = User(
        id=_generate_secure_string(12),
        name=name,
        peer_key=peer_key,
        hashed_password=pw_parts[1],
        password_salt=pw_parts[0],
        role=role.name,
        created_by=created_by,
    )

    table = _users_table()
    table.insert(asdict(user), pk="id")
    return user.id


def authenticate_user(name: str, password: str) -> str | None:
    """
    Authenticates a user given their plaintext password. If incorrect, returns none.
    If correct, returns their user ID
    """
    table: Table = _users_table()
    possible_users = table.rows_where("name=?", [name])
    for user in possible_users:
        hashed_pass = _hash_pass_with_salt(password, user["password_salt"])
        if hashed_pass[1] == user["hashed_password"]:
            return user["id"]
    return None


def authenticate_user_by_peer_key(peer_key: str) -> str | None:
    """
    Authenticates the user by taking in their peer key.
    Returns user_id when success, otherwise none.
    """
    table = _users_table()
    possible_users = table.rows_where("peer_key=?", [peer_key])
    for user in possible_users:
        return user["id"]
    return None


def _generate_secure_password():
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = "".join(secrets.choice(alphabet) for _ in range(14))
    return password


def root_user_check():
    table = _users_table()

    # Table check
    if not table.exists():
        table.create(
            {
                "id": str,
                "name": str,
                "peer_key": str,
                "hashed_password": str,
                "password_salt": str,
                "role": str,
                "created_by": str,
            },
            not_null={
                "name",
                "peer_key",
                "hashed_password",
                "password_salt",
                "role",
                "created_by",
            },
            pk="id",
        )

        table.create_index(["name"], unique=True)
        table.create_index(["peer_key"], unique=True)

    results = table.rows_where("name = 'root'")
    number_of_existing = len([x for x in results])
    if number_of_existing > 1:
        raise Exception("Only 1 root user expected!")
    elif number_of_existing == 0:
        _logger.info("Inserting root user")
        password = _generate_secure_password()
        result = create_user(
            name="root", plaintext_password=password, role=UserRole.ROOT, created_by=""
        )
        assert isinstance(result, str)
        _logger.info(
            f"Root user generated with password: {password} change this on next login"
        )
    else:
        _logger.info("root user check passed")


def get_user_from_key(plaintext_key: str) -> User | None:
    """Given a plaintext peer key, looks up the user who it belongs to. None if not found."""

    hashed_key = hashlib.sha256(plaintext_key.encode("utf-8")).hexdigest()
    table = _users_table()
    results = table.rows_where(f"sha_hashed_peer_key = {hashed_key}")
    try:
        first = results.__next__()
    except StopIteration:
        return None
    return User(**first)


def get_user_by_id(user_id: str) -> User | None:
    table = _users_table()
    try:
        record = table.get([user_id])
        return User(**record)
    except NotFoundError:
        return None
