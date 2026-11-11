from shared_utils.app_logging import get_logger
from sqlite3 import IntegrityError
from tracker.InvalidUserInputError import InvalidUserInputError
import dataclasses
from tracker.datastore.connection import get_db
from sqlite_utils.db import Table, NotFoundError
from ..RegistryItem import RegistryItem, RegistryItemFile

_logger = get_logger("registry_data_access")


def get_by_path(path: str) -> list[RegistryItem]:
    """
    Returns registry items matching the exact path given
    """
    table = _get_table()
    items_at_path = table.rows_where("path = ?", [path])
    return [_from_dict(x, []) for x in items_at_path]


def _get_table() -> Table:
    table = get_db().table("torrent_registry")
    return table


def _get_registry_item_files_table() -> Table:
    return get_db().table("registry_item_files")


def _get_registry_item_files(info_hash: bytes) -> list[RegistryItemFile]:
    table = _get_registry_item_files_table()
    rows = table.rows_where("info_hash = ?", [info_hash])
    return [RegistryItemFile(path=row["path"], length=row["length"]) for row in rows]


def _insert_registry_item_files(info_hash: bytes, files: list[RegistryItemFile]):
    table = _get_registry_item_files_table()
    data = [
        {
            "info_hash": info_hash,
            "file_sequence": i,
            "path": file.path,
            "length": file.length,
        }
        for i, file in enumerate(files)
    ]
    table.insert_all(data, pk=("info_hash", "file_sequence"))


def _from_dict(
    row_dict: dict, registry_item_files: list[RegistryItemFile]
) -> RegistryItem:
    return RegistryItem(
        name=row_dict["name"],
        path=row_dict["path"],
        info_hash_v1=row_dict["info_hash_v1"],
        info_hash_v2=row_dict["info_hash_v2"],
        info_bytes=row_dict["info_bytes"],
        owner_user_id=row_dict["owner_user_id"],
        description=row_dict["description"],
        total_size=row_dict["total_size"],
        files=registry_item_files,
    )


def get_by_info_hash(info_hash: bytes) -> RegistryItem | InvalidUserInputError:
    table = _get_table()
    results = table.rows_where(
        "info_hash_v1 = ? OR info_hash_v2 = ?", [info_hash, info_hash]
    )
    for row in results:
        return _from_dict(row, _get_registry_item_files(info_hash))
    return InvalidUserInputError("Registry item not found")


def insert_registry_item(registry_item: RegistryItem) -> InvalidUserInputError | None:
    item_dict = dataclasses.asdict(registry_item)
    del item_dict["files"]
    table = _get_table()
    try:
        _insert_registry_item_files(registry_item.info_hash_v1, registry_item.files)
        table.insert(record=item_dict, pk=["info_hash_v1"])
    except IntegrityError as e:
        _logger.warning(e)
        return InvalidUserInputError("Attempted to add duplicate item!")


def delete_registry_item(info_hash_v1: bytes):
    table = _get_table()
    table.delete(pk_values=[info_hash_v1])
