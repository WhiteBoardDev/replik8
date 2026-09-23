import dataclasses
from dataclasses import dataclass

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

    """
    Total size of the files in the torrent in bytes
    """
    total_size: int

    """
    The names of the files contained within the torrent
    """
    files: list[str]


    def as_dict(self):
        return dataclasses.asdict(self)
