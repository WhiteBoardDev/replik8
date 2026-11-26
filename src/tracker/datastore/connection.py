from shared_utils.app_logging import get_logger
import threading
from pathlib import Path
from sqlite_utils import Database
import sqlite_utils

_logger = get_logger("connection")
_max_connections = 50
_db_cache: dict[int, Database] = {}
_db_location = ""

def set_db_location(location: str):
    assert len(location) > 0
    _logger.info(f"Using database file location: {location}")
    parent_dir = Path(location).parent.resolve()
    parent_dir.mkdir(parents=True, exist_ok=True) 
    global _db_location
    _db_location = location

def get_db() -> Database:
    assert len(_db_location) > 0, "DB location not set!"
    thread_id = threading.get_ident()
    if thread_id not in _db_cache:
        _logger.info(f"opening new database connection {_db_location} for thread {thread_id}")
        _con = sqlite_utils.Database(_db_location)
        _db_cache[thread_id] = _con
        assert len(_db_cache) < _max_connections
    return _db_cache[thread_id] 
