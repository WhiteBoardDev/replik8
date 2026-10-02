from shared_utils.app_logging import get_logger
from sqlite3 import IntegrityError
from tracker.InvalidUserInputError import InvalidUserInputError
import dataclasses
from tracker.datastore.connection import get_db
from sqlite_utils.db import Table, NotFoundError
from ..RegistryItem import RegistryItem

_logger = get_logger("registry_data_access")

def get_by_path(path: str) -> list[RegistryItem]:
    """
    Returns registry items matching the exact path given
    """
    table = _get_table()
    items_at_path = table.rows_where("path = ?", [path]) 
    return [ _from_dict(x) for x in items_at_path]

def _get_table() -> Table:
    table = get_db().table('torrent_registry')
    return table

def _from_dict(row_dict: dict) -> RegistryItem:
    return RegistryItem(
        name=row_dict['name'],
        path=row_dict['path'],
        info_hash=row_dict['info_hash'],
        owner_user_id=row_dict['owner_user_id'],
        description=row_dict['description'],
        total_size=row_dict['total_size'],
        files = row_dict['files']
    ) 


def get_by_info_hash(info_hash: bytes) -> RegistryItem | InvalidUserInputError:
    table = _get_table()
    try:
        record = table.get([info_hash])
        return _from_dict(record)
    except NotFoundError:
        return InvalidUserInputError("Registry item not found")

def insert_registry_item(registry_item: RegistryItem) -> InvalidUserInputError | None:
    table = _get_table()
    try:
        table.insert(dataclasses.asdict(registry_item), pk=['info_hash'])
    except IntegrityError as e:
        _logger.warning(e)
        return InvalidUserInputError("Attempted to add duplicate item!")

def delete_registry_item(info_hash: bytes):
    table = _get_table()
    table.delete(pk_values=[info_hash])