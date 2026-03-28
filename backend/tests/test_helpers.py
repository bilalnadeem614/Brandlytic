from app.utils.helpers import is_url


def test_is_url_valid():
    assert is_url("https://example.com") is True
    assert is_url("http://tryholo.ai/pricing") is True


def test_is_url_invalid():
    assert is_url("A coffee shop in Karachi") is False
    assert is_url("just some text") is False
    assert is_url("") is False
