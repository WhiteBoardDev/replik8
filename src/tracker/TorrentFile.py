from io import StringIO
from tracker.bencoder import parse_bencoded_message, Bencoder
import hashlib


class TorrentFile:
    def __init__(self, file_name: str, file_contents: bytes):
        torrent_dict = parse_bencoded_message(file_contents)
        assert isinstance(torrent_dict, dict)
        self.torrent_dict = torrent_dict
        self.file_name = file_name
        info_files = self._get_info_files()
        self.files: list[tuple[str, int]] = []
        self.file_lengths: list[int] = []
        self.total_size = 0
        if info_files is not None:
            for file in info_files:
                assert isinstance(file, dict)
                length = file[b"length"]
                assert isinstance(length, int)
                self.total_size = +length
                file_path = file[b"path"]
                assert isinstance(file_path, list)
                full_path = StringIO()
                for i, path in enumerate(file_path):
                    assert isinstance(path, bytes)
                    if i > 0:
                        full_path.write("/")
                    full_path.write(path.decode("utf-8"))
                self.files.append((full_path.getvalue(), length))
        piece_length = torrent_dict[b"info"][b"piece length"]
        assert isinstance(piece_length, int)
        self.piece_length = piece_length

        pieces = torrent_dict[b"info"][b"pieces"]
        assert isinstance(pieces, bytes)
        self.pieces = pieces

    def get_info(self) -> dict:
        info = self.torrent_dict[b"info"]
        assert isinstance(info, dict)
        return info

    def _get_info_files(self) -> list | None:
        if b"files" not in self.get_info():
            return None
        files = self.get_info()[b"files"]
        assert isinstance(files, list)
        return files

    def _meta_version(self) -> int:
        info = self.get_info()
        if b"meta version" in info and info[b"meta version"] == 2:
            return 2
        return 1

    def compute_info_hash_v1(self) -> bytes:
        info_bencoded = Bencoder().withDict(self.get_info()).asBytes()
        hash = hashlib.sha1(info_bencoded).digest()
        return hash

    def compute_info_hash_v2(self) -> bytes:
        info_bencoded = Bencoder().withDict(self.get_info()).asBytes()
        hash = hashlib.sha256(info_bencoded).digest()
        return hash[:20]

    def get_total_file_size(self):
        return self.total_size
