import routes
import routes
from dataclasses import dataclass
from pathlib import Path
_storage_location = 'data'



@dataclass
class DataEntry:
    name: str
    download_href: str


def is_safe_for_download(path: str) -> bool:
    # TODO
    return True

def file_name_from_path(path: str):
    return Path(path).parts[-1]

def list_contents(subpath: str | None):
    return [DataEntry(x.name, routes.api_download_file(x.name)) for x in Path(_storage_location).iterdir()]