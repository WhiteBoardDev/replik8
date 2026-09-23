from tracker.TorrentFile import TorrentFile

known_torrent = open('tests/tracker/hello.torrent', 'rb') 

def test_info_hash_compute():
    torrent = TorrentFile('hello.torrent',known_torrent.readline())
    assert "83d4dbacc5e531d8fe1555a71b5e35867aa08414" == torrent.compute_info_hash().hex()