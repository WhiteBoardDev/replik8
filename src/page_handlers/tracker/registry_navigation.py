import dataclasses
from page_handlers.tracker.torrent_registry import RegistryItem, get_by_path
from dataclasses import dataclass
from datastore.connection import get_db
from typing import Set
from sqlite_utils.db import Table
import app_logging

_logger = app_logging.get_logger("torrent_registry")


def _get_table() -> Table:
    table = get_db().table('torrent_registry')
    return table

def _build_path_set() -> Set[str]:
    table = _get_table()
    unique_paths = table.rows_where(
        select="path",
        where="1=1 group by path"
    )
    paths = set(['/'])
    for path_row in unique_paths:
        path = path_row['path']
        if not isinstance(path, str):
            raise Exception('path should always be a string!!')

        paths.add(path)
        for i, char in enumerate(path):
            if char == '/' and i > 0:
                paths.add(path[0:i])

    _logger.info("Built registry paths", extra={
        "context" : {
            "paths" : sorted([x for x in paths])
        }
    }) 
    return paths


type NavigationTreeNode = dict[str,NavigationTreeNode]

@dataclass
class NavigationPath:
    full_path: str

    @property
    def leaf_path(self):
        if self.full_path == '/':
            return None
        return self.full_path.split('/')[-1]

    @property
    def html_safe_path(self):
        return self.full_path.replace('/', '-')

    def as_dict(self):
        return {
            'full_path': self.full_path,
            'leaf_path': self.leaf_path,
            'html_safe_path': self.html_safe_path

        }

@dataclass
class NavigationElementWithRegistryItems():

    navigation_path: NavigationPath

    """
    Relative child Paths
    """
    child_paths: list[NavigationPath]


    """
    Registry Items Located at `path`
    """
    registry_items: list[RegistryItem]


    def as_dict(self):
        return {
            'navigation_path': self.navigation_path.as_dict(),
            'child_paths': [x.as_dict() for x in self.child_paths],
            'registry_items': [x.as_dict() for x in self.registry_items]
        }


def _build_nav_tree(paths: set[str]) -> NavigationTreeNode:
    root: NavigationTreeNode = dict()
    for path in paths:
        if path != '/':
            path_parts = path.removeprefix('/').split('/')
            current_node = root
            for path_parth in path_parts:
                assert len(path_parth) > 0
                if path_parth not in current_node:
                    current_node[path_parth] = dict()
                current_node = current_node[path_parth] 
    return root



def _get_nav_children_of(path: str) -> list[str]:
    _registry_paths = _build_path_set()
    _nav_tree_root = _build_nav_tree(_registry_paths)
    path_parts = path.split('/') 
    current_node = _nav_tree_root
    for part in path_parts:
        if len(part) > 0:
            if part in current_node:
                current_node = current_node[part] 
            else:
                return []
    return [x for x in current_node.keys()]


def get_navigation_at_path(path: str) -> NavigationElementWithRegistryItems:
    return NavigationElementWithRegistryItems(
            navigation_path=NavigationPath(
                full_path=path),
            child_paths = [NavigationPath(f"{path}/{x}".replace('//','/')) for x in _get_nav_children_of(path)],
            registry_items = get_by_path(path)
    )