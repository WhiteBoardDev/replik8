import dataclasses
import app_logging
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


    """
    Description
    """
    description: str

    def as_dict(self):
        return dataclasses.asdict(self)

def _get_table() -> Table:
    table = get_db().table('torrent_registry')
    return table

_mock_description = """
The Ford F-150 stands as the definitive benchmark of the American full-size pickup truck, famously holding its position as the best-selling vehicle in the United States for decades. Renowned for its exceptional versatility, it seamlessly bridges the gap between a rugged, high-capability workhorse and a refined, tech-forward family vehicle. The truck features a high-strength, military-grade aluminum-alloy body paired with a robust steel frame, offering impressive towing and payload capacities. Inside, modern generations transition from utilitarian comfort to near-luxury refinement, boasting advanced infotainment systems like Ford's SYNC, hands-free driving technology, and innovative features like the Pro Power Onboard generator. With a diverse powertrain lineup that ranges from traditional, throaty V8 engines and efficient EcoBoost V6s to the cutting-edge Full Hybrid PowerBoost and the all-electric F-150 Lightning, this iconic truck continues to adapt to the evolving demands of everyday drivers and commercial fleets alike.
"""

def insert_mock_data():
    """
    TODO ditch this when the add torrent feature is complete
    """
    table = _get_table()
    table.drop(ignore=True)


    mock_items = [
            RegistryItem("T1", "/one", info_hash=b'1', owner_user_id='123', description=_mock_description),
            RegistryItem("T2", "/one", info_hash=b'2', owner_user_id='123', description=_mock_description),
            RegistryItem("T3", "/one", info_hash=b'3', owner_user_id='123', description=_mock_description),
            RegistryItem("T4", "/two", info_hash=b'4', owner_user_id='123', description=_mock_description), 
            RegistryItem("T5", "/two/one", info_hash=b'5', owner_user_id='123', description=_mock_description),
            RegistryItem("T6", "/two/one", info_hash=b'6', owner_user_id='123', description=_mock_description),
            RegistryItem("T7", "/two/one/one", info_hash=b'7', owner_user_id='123', description=_mock_description),
            RegistryItem("T8", "/two/two/one", info_hash=b'8', owner_user_id='123', description=_mock_description),
            RegistryItem("T9", "/two/two/two", info_hash=b'9', owner_user_id='123', description=_mock_description),
            RegistryItem("T10", "/three", info_hash=b'10', owner_user_id='123', description=_mock_description),
            RegistryItem("T11", "/three", info_hash=b'11', owner_user_id='123', description=_mock_description),
            RegistryItem("T12", "/three/four", info_hash=b'12', owner_user_id='123', description=_mock_description),
            RegistryItem("T13", "/three", info_hash=b'13', owner_user_id='123', description=_mock_description),
            RegistryItem("T14", "/", info_hash=b'14', owner_user_id='123', description=_mock_description),
        ]

    table.insert_all([x.as_dict() for x in mock_items], pk='info_hash') 

insert_mock_data()


def _from_dict(row_dict: dict) -> RegistryItem:
    return RegistryItem(
        name=row_dict['name'],
        path=row_dict['path'],
        info_hash=row_dict['info_hash'],
        owner_user_id=row_dict['owner_user_id'],
        description=row_dict['description']
    ) 

def get_by_path(path: str) -> list[RegistryItem]:
    """
    Returns registry items matching the exact path given
    """
    table = _get_table()
    items_at_path = table.rows_where("path = ?", [path]) 
    return [ _from_dict(x) for x in items_at_path]


def get_by_info_hash(info_hash: bytes) -> RegistryItem:
    table = _get_table()
    record = table.get([info_hash])
    return _from_dict(record)
