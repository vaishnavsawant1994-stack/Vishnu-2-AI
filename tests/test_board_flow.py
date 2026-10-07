from evo.board import add_agent, add_task, list_agents, update_task


def test_task_can_move_and_agents_can_be_listed(tmp_path):
    task = add_task(tmp_path, 'Ship the page')
    moved = update_task(tmp_path, task['id'], 'done')
    assert moved['status'] == 'done'
    add_agent(tmp_path, 'writer', 'copy')
    assert list_agents(tmp_path)['agents'][0]['name'] == 'writer'
