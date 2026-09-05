import routes
import routes
from dataclasses import dataclass
from pathlib import Path
_storage_location = 'data'



@dataclass
class DataEntry:
    name: Path
    download_href: Path


def is_safe_for_download(path: Path) -> bool:
    # TODO
    return True

def file_name_from_path(path: Path):
    return Path(path).parts[-1]

def list_contents(subpath: Path | None):
    return [DataEntry(x.name, routes.api_download_file(x.name)) for x in Path(_storage_location).iterdir()]

def get_path_from_public_path(path: Path) -> Path:
    return Path(f"{_storage_location}/{path}")