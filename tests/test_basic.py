from tgalice.testing.testing_utils import make_context

from dm import StretchDM


def test_hello():
    dm = StretchDM()
    resp = dm.respond(make_context(text='Привет', new_session=True))
    assert '30' in resp.text
