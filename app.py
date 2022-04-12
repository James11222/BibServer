import os
from flask import Flask, render_template, flash, request, redirect, url_for, abort, \
    send_from_directory
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
from pybtex.database import parse_file
import pandas as pd

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['MAX_CONTENT_LENGTH'] = 4096 * 4096
    app.config['UPLOAD_EXTENSIONS'] = ['.bib']
    app.config['UPLOAD_PATH'] = 'uploads' 
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///collections.sqlite3'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = "random string"

    db.init_app(app)

    return app

app = create_app()

# ------------------------------------------------------------
#                       File Uploading
# ------------------------------------------------------------



class Collections(db.Model):
   id = db.Column('collection_id', db.Integer, primary_key = True)
   collection_name = db.Column(db.String(100))
   title = db.Column(db.String(200))
   year = db.Column(db.Integer)
   volume = db.Column(db.Integer)
   journal = db.Column(db.String(50))
   pages = db.Column(db.String(50))
   authors = db.Column(db.String(200))
   ref_tag = db.Column(db.String(100))

   def __init__(self, collection_name, title, year, volume, journal, pages, authors, ref_tag):
        self.collection_name = collection_name
        self.title = title
        self.year = year
        self.volume = volume
        self.journal = journal
        self.pages = pages
        self.authors = authors
        self.ref_tag = ref_tag

def generate_collection(bib_data):
    """
    Helper function to generate a collection from a BibTeX file.
    """
    
    for entry in bib_data.entries.keys():
            #Make sure the data is well formatted
            try:
                 title_val = bib_data.entries[entry].fields["title"][1:-1]
            except:
                 title_val = "NONE"

            try:
                 year_val = bib_data.entries[entry].fields["year"]
            except:
                 year_val = 0

            try:
                 volume_val = bib_data.entries[entry].fields["volume"]
            except:
                 volume_val = 0

            try:
                 journal_val = bib_data.entries[entry].fields["journal"]
            except:
                 journal_val = "NONE"

            try:
                 pages_val = bib_data.entries[entry].fields["pages"]
            except:
                 pages_val = "NONE"

            try:
                author_val = ""
                for i, author in enumerate(bib_data.entries[entry].persons["author"]):
                    if i == len(bib_data.entries[entry].persons["author"]) - 1:
                        name = author.last_names[0][1:-1] + ", " + author.first_names[0]
                        author_val += name
                    else:
                        name = author.last_names[0][1:-1] + ", " + author.first_names[0]
                        author_val += name + " & "
                author_val = str(author_val)
            except:
                author_val= "NONE"

                


            collection = Collections(request.form.get("fname"), 
                                     title_val,
                                     year_val,
                                     volume_val,
                                     journal_val,
                                     pages_val,
                                     author_val,
                                     entry)

            db.session.add(collection)
            db.session.commit()

@app.template_filter('add_ext')
def add_extension(s):
    return s + '.bib'

@app.route('/')
def index():
    files = os.listdir(app.config['UPLOAD_PATH'])
    files = [os.path.splitext(file)[0] for file in files]
    if "__init__" in files:
        files.remove("__init__")
    return render_template('index.html', files=files)

@app.route('/', methods=['POST'])
def upload_files():
    uploaded_file = request.files['file']
    filename = secure_filename(request.form.get("fname") + '.bib')
    if filename != '':
        file_ext = os.path.splitext(filename)[1]
        if file_ext not in app.config['UPLOAD_EXTENSIONS']:
            abort(400)
        uploaded_file.save(os.path.join(app.config['UPLOAD_PATH'], filename))

        #add data to sql database:
        bib_data = parse_file(os.path.join(app.config['UPLOAD_PATH'], filename))
        generate_collection(bib_data)

    return redirect(url_for('index'))

@app.route('/uploads/<filename>')
def upload(filename):
    return send_from_directory(app.config['UPLOAD_PATH'], filename)

@app.route('/show_all')
def show_all():
    return render_template('show_all.html', collections=Collections.query.all())


# ------------------------------------------------------------

# ------------------------------------------------------------
#                       Querying
# ------------------------------------------------------------
def generate_results(query_string, con):
    if query_string == "None":
        results = ["Please enter a query to get results."]
    else:
        sql_cmd = "SELECT * FROM Collections WHERE " + str(query_string)
        try:
            df = pd.read_sql_query(sql_cmd, con)
            results = []
            for index, row in df.iterrows():
                result_string =  ("Collection Name: " + row['collection_name'] + "\n" + 
                                    "Title: " + row['title'] + "\n" +
                                    "Year: " + str(row['year']) + "\n" +
                                    "Volume: " + str(row['volume']) + "\n" +
                                    "Journal: " + row['journal'] + "\n" + 
                                    "Pages: " + row['pages'] + "\n" +
                                    "Authors List: " + row['authors'] + "\n" + 
                                    "Reference Tag: " + row['ref_tag'])

                result_string = result_string.replace('\n', '<br>')
                results.append(result_string)

        except:
            results = ["Your query was '" + query_string + "'. There are no results that match that query, please try something else."]

    return results


@app.route('/query', methods=["GET", "POST"])
def query():
    query_string = str(request.form.get("fname"))
    results = generate_results(query_string=query_string, con=db.engine)
    return render_template('query.html', results=results)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000)