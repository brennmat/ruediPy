def test_import():
    import ruedipy
    assert hasattr(ruedipy, "__file__")
