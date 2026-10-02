from tracker.InvalidUserInputError import InvalidUserInputError
from .internal.registry_data_access import insert_registry_item,get_by_info_hash, delete_registry_item
from .RegistryItem import RegistryItem
from tracker.registry.registry_navigation import refresh_nagivation_tree
from tracker.TorrentFile import TorrentFile
from shared_utils import app_logging
import re

_logger = app_logging.get_logger("torrent_registry")


def _validate_path(path: str):
    assert re.match(r"^/[a-zA-Z\/ ]*$", path), "Path must contain only alpha characters"

def add_new_item(torrent_file: TorrentFile, user_id: str, description: str, path: str) -> InvalidUserInputError | None:
    """
    Adds a new file to the registry
    """

    info_hash = torrent_file.compute_info_hash()
    _validate_path(path)
    registry_item = RegistryItem(
        name=torrent_file.file_name,
        path=path,
        info_hash=torrent_file.compute_info_hash(),
        owner_user_id=user_id,
        description=description,
        total_size=torrent_file.total_size,
        files=torrent_file.file_names
    )

    insert_resp = insert_registry_item(registry_item)
    if isinstance(insert_resp, InvalidUserInputError):
        return insert_resp
    refresh_nagivation_tree()


def delete_item(authenticated_user_id: str, info_hash: bytes) -> InvalidUserInputError | None:

    registry_item = get_by_info_hash(info_hash)
    if isinstance(registry_item, InvalidUserInputError):
        return registry_item

    if registry_item.owner_user_id != authenticated_user_id:
        return InvalidUserInputError("Unauthorized to delete registry item")

    delete_registry_item(registry_item.info_hash)
    refresh_nagivation_tree()
    # TODO delete peer history?