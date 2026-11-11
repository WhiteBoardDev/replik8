import time
import uuid
from dataclasses import dataclass
import dataclasses
from tracker.InvalidUserInputError import InvalidUserInputError
from tracker.datastore.connection import get_db
from sqlite_utils.db import Table
import secrets
import string
import bcrypt

_max_invalid_secret_attempts = 5


def _get_table() -> Table:
    return get_db().table("invites")


def _user_allowed_to_create_invite(user_id: str) -> None | InvalidUserInputError:
    # TODO assert that the caller has appropriate permission to do so
    return None


def _expire_stale_records():
    # TODO
    return None


@dataclass
class InviteDatabaseRecord:
    invite_id: str
    invite_secret_hash_hex: str
    invite_secret_salt: bytes
    created_by: str
    created_timestamp: int
    invalid_secret_counter: int


def _generate_invite_secret() -> str:
    characters = string.ascii_letters
    return "".join(secrets.choice(characters) for _ in range(8))


def _hash(plaintext: str, salt: bytes | None) -> tuple[bytes, str]:
    plaintext_bytes = plaintext.encode("utf-8")
    if salt is None:
        salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(plaintext_bytes, salt)
    return (
        salt,
        hashed_bytes.hex(),
    )


@dataclass
class InvitePairs:
    invite_id: str
    invite_secret: str


def generate_invite(user_id: str) -> InvitePairs | InvalidUserInputError:
    """
    Generates an invite for a user to share. The invite enables the invited
    person to generate a new account.
    """

    _expire_stale_records()
    possible_error = _user_allowed_to_create_invite(user_id)
    if possible_error is not None:
        return possible_error

    table = _get_table()
    invite_id = uuid.uuid4().bytes.hex()
    invite_secret = _generate_invite_secret()
    secrets = _hash(invite_secret, None)
    invite = InviteDatabaseRecord(
        invite_id=invite_id,
        invite_secret_hash_hex=secrets[1],
        invite_secret_salt=secrets[0],
        created_by=user_id,
        created_timestamp=int(time.time()),
        invalid_secret_counter=0,
    )
    table.insert(dataclasses.asdict(invite), pk=["invite_id"])
    return InvitePairs(invite_id, invite_secret)


def consume_invite(invite_pairs: InvitePairs) -> InvalidUserInputError | str:
    return _handle_invite(invite_pairs, True)


def peek_invite(invite_pairs: InvitePairs) -> InvalidUserInputError | str:
    return _handle_invite(invite_pairs, False)


def is_invite_exists(invite_id: str) -> bool:
    table = _get_table()
    for _ in table.rows_where("invite_id = ?", [invite_id]):
        return True
    return False


def _handle_invite(
    invite_pairs: InvitePairs, should_consume: bool
) -> InvalidUserInputError | str:
    """
    checks if the secret and invite are valid. If so, returns the user_id of the user who
    created the invite.

    Else, returns an InvalidUserInputError
    """

    table = _get_table()
    for row in table.rows_where("invite_id = ?", [invite_pairs.invite_id]):
        if row["invalid_secret_counter"] >= _max_invalid_secret_attempts:
            table.delete([invite_pairs.invite_id])
            return InvalidUserInputError("Too many failed attempts at invite consume")
        else:
            salt = row["invite_secret_salt"]
            actual_secret_hash = _hash(invite_pairs.invite_secret, salt)[1]
            if actual_secret_hash == row["invite_secret_hash_hex"]:
                if should_consume:
                    table.delete([invite_pairs.invite_id])
                created_by = row["created_by"]
                assert isinstance(created_by, str)
                return created_by
            else:
                table.update(
                    [invite_pairs.invite_id],
                    {"invalid_secret_counter": row["invalid_secret_counter"] + 1},
                )
                return InvalidUserInputError("invalid invite secret")
    return InvalidUserInputError("unable to find invite by id")
