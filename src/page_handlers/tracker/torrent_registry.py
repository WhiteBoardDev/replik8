import dataclasses
import app_logging
from typing import Set
from sqlite_utils.db import Table
from datastore.connection import get_db
from dataclasses import dataclass

_logger = app_logging.get_logger("torrent_registry")

@dataclass
class RegistryItem():

    """
    Display Name of the item in the registry. Could be a 
    """
    name: str

    """
    The parent navigation path in the registry where the item belongs
    """
    path: str

    """
    The info_hash of the torrent
    """
    info_hash: bytes

    """
    The owner of the registry item
    """
    owner_user_id: str

    def as_dict(self):
        return dataclasses.asdict(self)

def _get_table() -> Table:
    table = get_db().table('torrent_registry')
    return table

def insert_mock_data():
    """
    TODO ditch this when the add torrent feature is complete
    """
    table = _get_table()
    table.drop(ignore=True)


    mock_items = [
            RegistryItem("T1", "/one", info_hash=b'1', owner_user_id='123'),
            RegistryItem("T2", "/one", info_hash=b'2', owner_user_id='123'),
            RegistryItem("T3", "/one", info_hash=b'3', owner_user_id='123'),
            RegistryItem("T4", "/two", info_hash=b'4', owner_user_id='123'),
            RegistryItem("T5", "/two/one", info_hash=b'5', owner_user_id='123'),
            RegistryItem("T6", "/two/one", info_hash=b'6', owner_user_id='123'),
            RegistryItem("T7", "/two/one/one", info_hash=b'7', owner_user_id='123'),
            RegistryItem("T7", "/two/two/one", info_hash=b'8', owner_user_id='123'),
            RegistryItem("T7", "/two/two/two", info_hash=b'9', owner_user_id='123'),
            RegistryItem("T8", "/three", info_hash=b'10', owner_user_id='123'),
            RegistryItem("T9", "/three", info_hash=b'11', owner_user_id='123'),
            RegistryItem("T10", "/three/four", info_hash=b'12', owner_user_id='123'),
            RegistryItem("T11", "/three", info_hash=b'13', owner_user_id='123'),
            RegistryItem("T12", "/", info_hash=b'14', owner_user_id='123'),
        ]

    table.insert_all([x.as_dict() for x in mock_items], pk='info_hash') 

insert_mock_data()


def get_by_path(path: str) -> list[RegistryItem]:
    """
    Returns registry items matching the exact path given
    """
    table = _get_table()
    items_at_path = table.rows_where("path = ?", [path]) 
    return [RegistryItem(
        name=x['name'],
        path=x['path'],
        info_hash=x['info_hash'],
        owner_user_id=x['owner_user_id']
    ) for x in items_at_path]