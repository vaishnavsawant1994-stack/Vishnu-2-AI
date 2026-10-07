from evo.local import processes, snapshot


def test_snapshot_reads_this_machine():
    info = snapshot()
    assert info['system']
    assert info['python']


def test_process_list_runs_on_this_machine():
    listed = processes(limit=3)
    assert 'rows' in listed
    assert listed['system']
