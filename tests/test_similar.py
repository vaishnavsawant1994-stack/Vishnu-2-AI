from evo.similar.design import review
from evo.similar.story import write_story
from evo.similar.work import assign, comment, create_task


def test_task_comment_and_assignment(tmp_path):
    task = create_task(tmp_path, 'Build the page')
    assert comment(tmp_path, task['id'], 'Started the form')['comments'] == 1
    assigned = assign(tmp_path, 'writer', 'copy', task['id'])
    assert assigned['status'] == 'doing'


def test_story_is_written_without_video(tmp_path):
    result = write_story(tmp_path, 'Launch', ['Open the app', 'Save a note'])
    assert result['scenes'] == 2
    assert result['video'] is False
    assert review('# Save\nThe user clicks save. Show an error if empty. Max 200 characters.')['ok'] is True
