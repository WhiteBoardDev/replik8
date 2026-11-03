from tracker.TorrentFile import TorrentFile


def _get_known_torrent():
    return open("tests/tracker/hello.torrent", "rb")


def test_info_hash_compute():
    with _get_known_torrent() as known_torrent:
        torrent = TorrentFile("hello.torrent", known_torrent.readline())
        assert (
            "83d4dbacc5e531d8fe1555a71b5e35867aa08414"
            == torrent.compute_info_hash_v1().hex()
        )


def test_files_parsed():
    with _get_known_torrent() as known_torrent:
        torrent = TorrentFile("hello.torrent", known_torrent.readline())

        assert 229641 == torrent.files[0][1]
        assert "Screenshot from 2025-12-18 18-29-56.png" == torrent.files[0][0]
        assert len(torrent.files) == 7
