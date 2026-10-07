from agent.planner import Planner


class Tools:
    def schema_text(self):
        return 'web_search'
    def all(self):
        return [type('T', (), {'name': 'web_search'})()]


class Models:
    def json(self, prompt, system, sensitivity, private_context):
        assert 'one next tool step' in private_context
        return {'goal': 'store records', 'steps': [
            {'tool': 'web_search', 'description': 'search', 'parameters': {}},
            {'tool': 'web_search', 'description': 'search again', 'parameters': {}},
        ]}


def test_main_planner_keeps_one_step_and_does_not_own_completion():
    plan = Planner(Models(), Tools()).plan_one('store records', context='ACTIVE GOAL\nmissing: count is 100')
    assert len(plan['steps']) == 1
    assert plan['completion_authority'] == 'mind'
