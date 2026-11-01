from tracker.bencoder import Bencoder
from tracker.InvalidUserInputError import InvalidUserInputError
from .internal.registry_data_access import *
from .RegistryItem import RegistryItem
from tracker.registry.registry_navigation import refresh_nagivation_tree
from tracker.TorrentFile import TorrentFile
from shared_utils import app_logging
import re
import random
_logger = app_logging.get_logger("torrent_registry")


def _validate_path(path: str):
    assert re.match(r"^/[a-zA-Z\/ ]*$", path), "Path must contain only alpha characters"

def _check_info_for_errors(torrent_file: TorrentFile) -> str | None:
    """
    Checks a given torrent file if it contains valid structure to be accepted by
    this tracker. Returns a string describing the error or None if it is accepted.
    Short circuits upon the first error encountered.
    """

    info = torrent_file.get_info()
    if 'private' not in info or info['private'] != 1:
        return "Must be private torrent"


def _copy_and_customize_info_dict(info_dict_original: dict) -> dict:
    """
    Ensures the file is globally unique by adding a random value to the info dict.
    Only copies specific values from the original info hash to avoid extra fluff and 
    sanitize input.
    """

    updated_info_dict = {
        "private": 1,
        "nonce": random.randint(1,1000000),
        "files": info_dict_original["files"],
        "name": info_dict_original['name'],
        "piece length": info_dict_original['piece length'],
        "pieces": info_dict_original['pieces'],
    }

    return updated_info_dict

def _copy_and_customize_torrent(original: TorrentFile) -> TorrentFile:
    updated_info = _copy_and_customize_info_dict(original.get_info())
    updated_torrent_bytes = Bencoder().withDict({
        "info": updated_info
    }).asBytes()     
    updated_torrent = TorrentFile(original.file_name, updated_torrent_bytes)
    return updated_torrent


def add_new_item(torrent_file: TorrentFile, user_id: str, description: str, path: str) -> InvalidUserInputError | bytes:
    """
    Adds a new file to the registry. returns info_hash of newly item added
    """
    info_errors = _check_info_for_errors(torrent_file)


    # TODO - generate NEW info, and info_hash. inject custom SOURCE key
    # then save entire INFO bencoded into DB for easier downloads
    if info_errors is not None:
        return InvalidUserInputError(info_errors)

    updated_torrent = _copy_and_customize_torrent(torrent_file)
    info_hash = updated_torrent.compute_info_hash()
    _validate_path(path)
    registry_item = RegistryItem(
        name=updated_torrent.file_name.removesuffix('.torrent'),
        path=path,
        info_hash=info_hash,
        info_bytes=Bencoder().withDict(updated_torrent.get_info()).asBytes(),
        owner_user_id=user_id,
        description=description,
        total_size=updated_torrent.total_size,
        files=[RegistryItemFile(path=file[0], length=file[1]) for file in updated_torrent.files],
    )

    insert_resp = insert_registry_item(registry_item)
    if isinstance(insert_resp, InvalidUserInputError):
        return insert_resp
    refresh_nagivation_tree()

    return info_hash


def delete_item(authenticated_user_id: str, info_hash: bytes) -> InvalidUserInputError | None:

    registry_item = get_by_info_hash(info_hash)
    if isinstance(registry_item, InvalidUserInputError):
        return registry_item

    if registry_item.owner_user_id != authenticated_user_id:
        return InvalidUserInputError("Unauthorized to delete registry item")

    delete_registry_item(registry_item.info_hash)
    refresh_nagivation_tree()
    # TODO delete peer history?

def get_item_by_info_hash(info_hash: bytes) -> RegistryItem | InvalidUserInputError:
    return get_by_info_hash(info_hash)