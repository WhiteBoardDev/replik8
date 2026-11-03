from tracker.TorrentFile import TorrentFile
from tracker.bencoder import Bencoder, AcceptedBencoderTypes, parse_bencoded_message
from tracker.users import get_user_by_id
from tracker.InvalidUserInputError import InvalidUserInputError

from tracker.registry.RegistryItem import RegistryItem
from tracker.registry.torrent_registry import get_item_by_info_hash


def _registry_item_name_to_file_name(name: str) -> str:
    return f"{name}.torrent"


def _registry_item_to_bencoded(registry_item: RegistryItem, announce_url: str) -> bytes:

    root_dict: dict[str, AcceptedBencoderTypes] = {
        "announce": announce_url,
        "info": parse_bencoded_message(registry_item.info_bytes),
    }
    bencoded = Bencoder().withDict(root_dict).asBytes()

    # Sanity check to ensure construction of info is valid

    computed_info_hash = TorrentFile(
        _registry_item_name_to_file_name(registry_item.name), bencoded
    ).compute_info_hash_v1()
    assert computed_info_hash == registry_item.info_hash_v1, (
        "Failed to construct info hash that matches registry item"
    )

    return bencoded


def bencode_torrent_for_user(
    user_id: str, info_hash: bytes, announce_url_base: str
) -> tuple[str, bytes] | InvalidUserInputError:
    registry_item = get_item_by_info_hash(info_hash)

    if isinstance(registry_item, InvalidUserInputError):
        return registry_item

    user = get_user_by_id(user_id)

    if user is None:
        return InvalidUserInputError("user not found")

    return (
        _registry_item_name_to_file_name(registry_item.name),
        _registry_item_to_bencoded(
            registry_item, f"{announce_url_base}/{user.peer_key}"
        ),
    )
