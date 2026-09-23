from .registry_data_access import insert_registry_item
from .RegistryItem import RegistryItem
from tracker.registry.registry_navigation import refresh_nagivation_tree
from tracker.TorrentFile import TorrentFile
from shared_utils import app_logging
import re

_logger = app_logging.get_logger("torrent_registry")


def _validate_path(path: str):
    assert re.match(r"^/[a-zA-Z\/ ]*$", path), "Path must contain only alpha characters"

def add_new_item(torrent_file: TorrentFile, user_id: str, description: str, path: str):
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

    insert_registry_item(registry_item)
    refresh_nagivation_tree()
