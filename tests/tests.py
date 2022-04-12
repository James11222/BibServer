from BibServer.app import generate_collection, add_extension, query, index, upload_files, generate_results
from flask_sqlalchemy import SQLAlchemy
from BibServer.app import create_app
import pytest
from pybtex.database import parse_file

db = SQLAlchemy()

def test_add_extension():
	assert add_extension("test") == "test.bib"

@pytest.fixture()
def app():
	app1 = create_app()
	app1.config.update({
		"TESTING": True})
	db.init_app(app1)
	# other setup can go here (What does this even mean?)
	yield app1

	# clean up / reset resources here (What does this even mean?)

@pytest.fixture()
def client(app):
    return app.test_client()

@pytest.fixture()
def runner(app):
    return app.test_cli_runner()

def test_query_fail_example(client): #this is a failing test
	try:
		response = client.get("/query")
		assert not b"Available Column names are" in response.data
	except:
		assert False
	
def test_fail_make_collection():
	try:
		filename = "tests/test.bib"
		bib_data = parse_file(filename)
		generate_collection(bib_data)
		assert False

	except:
		assert True

def test_fail_query_func():
	try:
		query()
		assert False
	except:
		assert True


def test_fail_upload_files():
	try:
		upload_files()
		assert False
	except:
		assert True

def test_fail_index():
	try:
		index()
		assert False
	except:
		assert True

def test_generate_results():
	query_string = "year > 1900"
	try:
		results = generate_results(query_string, con=db.engine)
		assert False
	except:
		assert True


	





	

