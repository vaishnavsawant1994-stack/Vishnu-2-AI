import pytest

from evo.hub import SURFACES, handle


def test_every_surface_has_a_handler():
    assert 'forge' in SURFACES
    assert handle('circuit', {'board': 'arduino-uno', 'part': 'dht11'})['known'] is True
    assert handle('geo', {'origin': 'Mumbai', 'destination': 'London'})['points']
    assert handle('music', {'text': 'play Starboy'})['action'] == 'play'
    assert handle('desktop', {'action': 'volume'})['executed'] is False
    assert handle('phone', {'caller': 'Ada', 'note': 'ask for a time'})['answered'] is False


def test_heal_will_not_patch_stop():
    note = handle('heal', {'error': 'boom', 'path': 'security/vault.py'})
    assert note['applied'] is False
    assert note['reason'] == 'protected file'


def test_home_rejects_an_unknown_action():
    with pytest.raises(ValueError):
        handle('home', {'device': 'lamp', 'action': 'unlock'})
