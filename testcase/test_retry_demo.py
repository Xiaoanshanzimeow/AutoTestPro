import pytest

counter={"n":0}

def test_flaky_demo():
    counter["n"] += 1
    assert counter["n"] > 1