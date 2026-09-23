import dataclasses
from tracker.datastore.connection import get_db
from sqlite_utils.db import Table
from .RegistryItem import RegistryItem

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


def get_by_info_hash(info_hash: bytes) -> RegistryItem:
    table = _get_table()
    record = table.get([info_hash])
    return _from_dict(record)

def insert_registry_item(registry_item: RegistryItem):
    table = _get_table()
    table.insert(dataclasses.asdict(registry_item), pk=['info_hash'])