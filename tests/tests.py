from BibServer.app import generate_collection, add_extension, Collections
from flask_sqlalchemy import SQLAlchemy
from BibServer.app import create_app
import pytest

db = SQLAlchemy()

def test_add_extension():
	assert add_extension("test") == "test.bib"

@pytest.fixture()
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })

    # other setup can go here (What does this even mean?)

    yield app

    # clean up / reset resources here (What does this even mean?)

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_show_example(client): #this is a failing test
	try:
		response = client.get("/query")
		assert not b"Available Column names are" in response.data
	except:
		assert False

	

