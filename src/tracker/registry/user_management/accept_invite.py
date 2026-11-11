from tracker.InvalidUserInputError import InvalidUserInputError
from .users import create_user, UserRole
from .invites import InvitePairs, consume_invite, peek_invite


def accept_invite(
    invite_pairs: InvitePairs, requested_username: str, new_password: str
) -> InvalidUserInputError | None:
    """
    Handles coordination between invites and user modules
    """
    possible_invite = peek_invite(invite_pairs)
    if isinstance(possible_invite, str):
        possible_created_user = create_user(
            requested_username, new_password, UserRole.USER, possible_invite
        )
        if isinstance(possible_created_user, str):
            consumed_invite_user_id = consume_invite(invite_pairs)
            assert consumed_invite_user_id == possible_invite
        else:
            return possible_created_user
    else:
        return possible_invite
