from evo.owner_tools import owner_code, owner_math, owner_search


def test_owner_tools_are_named():
    assert owner_math('6 * 7') == {'ok': True, 'result': 42, 'tool': 'owner_math', 'owner': 'vaishnav'}
    checked = owner_code('1 + 1')
    assert checked['tool'] == 'owner_code'
    assert checked['result'] == 2
    blocked = owner_code('open("secret")')
    assert blocked['safe'] is False
    assert owner_search('')['tool'] == 'owner_search'
