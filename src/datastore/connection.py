from sqlite_utils import Database
import sqlite_utils

_con = sqlite_utils.Database('store.db')

def get_db() -> Database:
    return _con