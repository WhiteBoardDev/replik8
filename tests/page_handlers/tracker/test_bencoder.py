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

    assert resp == b'd8:completei2e10:incompletei0e8:intervali1800e5:peersld2:ip4:12344:porti4567eeee'
    