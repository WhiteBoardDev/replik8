import threading

from sqlite_utils import Database
import sqlite_utils


_max_connections = 50
_db_cache: dict[int, Database] = {}

def get_db() -> Database:
    thread_id = threading.get_ident()
    if thread_id not in _db_cache:
        _con = sqlite_utils.Database("store.db")
        _con.enable_wal()
        _db_cache[thread_id] = _con
        assert len(_db_cache) < _max_connections
    return _db_cache[thread_id] 
