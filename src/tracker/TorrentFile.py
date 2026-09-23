from tracker.bencoder import parse_bencoded_message, Bencoder
import hashlib


class TorrentFile:

    def __init__(self, file_name: str, file_contents: bytes):
        torrent_dict = parse_bencoded_message(file_contents)
        assert isinstance(torrent_dict, dict)
        self.torrent_dict = torrent_dict
        self.file_name = file_name
        info_files = self._get_info_files()
        self.file_names: list[str] = []
        self.total_size = 0
        for file in info_files:
            assert isinstance(file, dict)
            length = file['length']
            assert isinstance(length, int)
            self.total_size =+ length
            file_path = file['path']
            assert isinstance(file_path, list)
            for path in file_path:
                assert isinstance(path, bytes)
                self.file_names.append(path.decode('utf-8'))

    def _get_info(self) -> dict:
        info = self.torrent_dict['info']
        assert isinstance(info, dict)
        return info

    def _get_info_files(self) -> list:
        files = self._get_info()['files']
        assert isinstance(files, list)
        return files

    def compute_info_hash(self) -> bytes:
        info_bencoded = Bencoder().withDict(self._get_info()).asBytes()
        hash =hashlib.sha1(info_bencoded).digest()
        return hash


    def get_total_file_size(self):
        return self.total_size


