import sys
import os

parent_dir = os.path.dirname(__file__)
module_dir = os.path.join(parent_dir, "..")
absolute_path = os.path.abspath(module_dir)
sys.path.insert(0, absolute_path)

from app import app, open_file, get_countries
import pytest


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_open_file():
    with pytest.raises(FileNotFoundError):
        open_file("nonexistent_file.json", "r")


def test_get_countries():
    mydict = {"Country1": {...}, "Country2": {...}}
    countries, keys = get_countries(mydict)
    assert len(countries) == 2
    assert "Country1" in countries
    assert "Country2" in countries
    assert "-----  COUNTRY " in keys
    assert "Country1" in keys
    assert "Country2" in keys
