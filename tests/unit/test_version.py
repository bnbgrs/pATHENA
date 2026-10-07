from athena.version import __version__


def test_version_is_v0_1_release_version() -> None:
    assert __version__ == "0.1.0"
