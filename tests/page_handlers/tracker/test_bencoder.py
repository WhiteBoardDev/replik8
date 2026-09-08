from page_handlers.tracker.bencoder import Bencoder


def test_decimal_and_dict():
    resp = Bencoder().withDict({
        "interval": 1800,
        "complete": 2,
        "incomplete": 0,
        "peers": [{
            "ip" : "1234",
            "port": 4567
        }]
    }).asBytes()

    assert resp == b''
    