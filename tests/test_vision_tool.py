from pathlib import Path

from PIL import Image

from evo.vision_tool import describe_image


class FakeVision:
    def vision(self, prompt, data_url):
        assert data_url.startswith('data:image/jpeg;base64,')
        return f'seen: {prompt}'


def test_vision_uses_the_configured_model(tmp_path: Path):
    path = tmp_path / 'dot.png'
    Image.new('RGB', (8, 8), (20, 20, 20)).save(path)
    result = describe_image(str(path), 'What color is this?', FakeVision())
    assert result['ok'] is True
    assert result['description'] == 'seen: What color is this?'


def test_missing_model_does_not_invent_a_caption(tmp_path: Path):
    path = tmp_path / 'dot.png'
    Image.new('RGB', (8, 8), (20, 20, 20)).save(path)
    result = describe_image(str(path), 'Describe', None)
    assert result['ok'] is False
    assert 'not configured' in result['reason']
