from evo.board import add_task, design_check, list_tasks, recall, retain, storyboard


def test_task_and_memory(tmp_path):
    add_task(tmp_path, 'Review the ledger')
    assert list_tasks(tmp_path)['tasks'][0]['title'] == 'Review the ledger'
    retain(tmp_path, 'ledger failed on empty input')
    assert recall(tmp_path, 'ledger')['hits']


def test_design_and_storyboard():
    assert design_check('# Save\nThe user clicks save.\nShow an error.')['ok'] is True
    assert storyboard('Launch')['rendered_video'] is False
