from flask import Flask, render_template, request, redirect, flash, send_from_directory, abort
from run import run
from flask_sqlalchemy import SQLAlchemy 
import pandas as pd
import numpy as np
import os
from datetime import datetime
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = "80uCjGPps100%"

app.config["CSV_UPLOADS"] = "C:/Users/jgerhartz/projects/survey_wiz/static/csv"
app.config["ALLLOWED_IMAGE_EXTENSIONS"] = ["CSV"]
app.config["MAX_IMAGE_FILE_SIZE"] = 1000000
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config["CLIENT_CSVS"] = 'C:/Users/jgerhartz/projects/survey_wiz/static/client/csv'


db = SQLAlchemy(app)

class File(db.Model):
	id = db.Column(db.Integer, primary_key = True)

	name = db.Column(db.String(50))

	path = db.Column(db.String(100))

	date_created = db.Column(db.DateTime, default = datetime.now)



csv = "Spring 2019 Classroom survey raw.csv"
old_doc = "2017_2018_new_clean.csv"
old_df = pd.read_csv(old_doc)


@app.route('/')
@app.route('/home')
def index():
    return render_template('index.html')


@app.route('/table')
def table():
	data = File.query.all()

	if len(data) == 0:
		message = "Upload Files to View Table"


	return render_template("table.html", data=data)


@app.route('/table/<file_id>', methods = ['GET'])
def table_id(file_id):

	data = File.query.all()
	active = File.query.filter_by(id = file_id).first()
	final_df = run(active.path, old_doc, old_df)
	final_df.to_csv(app.config["CLIENT_CSVS"]+"/war_"+active.name)

	return render_template(
		'table_view.html',
		tables=[final_df.to_html()], data = data, active = active
		)


@app.route('/table/get-file/<file_name>', methods = ['GET'])
def get_file(file_name):

	fn = "war_" + file_name
	try:
		return send_from_directory(app.config["CLIENT_CSVS"], filename=fn, as_attachment=True)

	except FileNotFoundError:
		abort(404)

@app.route('/graphs')
def view_graphs():
	final_df=run(csv,old_doc,old_df)
	return render_template('graphs.html', final_df=final_df)


@app.route('/instructions')
def view_instructions():
    return render_template('instructions.html')

def allowed_csv(filename):
	if not "." in filename:
		return False

	ext = filename.rsplit(".",1)[1]

	if ext.upper() in app.config["ALLLOWED_IMAGE_EXTENSIONS"]:
		return True

	else:
		return False


def allowed_csv_filesize(filesize):

	if int(filesize) <= app.config["MAX_IMAGE_FILE_SIZE"]:
		return True

	else:
		return False

@app.route('/upload-file', methods=["GET", "POST"])
def upload_file():
	error = None
	filename = "Choose File"
	if request.method == "POST":

		if request.files:

			if not allowed_csv_filesize(request.cookies.get("filesize")):
				error = ("File exceeded maximum size")
				#return redirect(request.url)

			csv = request.files["csv"]

			if csv.filename == "":
				error = ("csv must have a filename")
				#return redirect(request.url)

			if not allowed_csv(csv.filename):
				error = ("Please upload a file with a .csv extension")
				#return redirect(request.url)

			else:
				filename = secure_filename(csv.filename)
				file = File(name = filename, path = (app.config["CSV_UPLOADS"] + "/" + filename) )
				csv.save(os.path.join(app.config["CSV_UPLOADS"], filename))
				db.session.add(file)
				db.session.commit()
				flash(filename + ' Uploaded')
				return redirect(request.url)

		else:
			flash("Please Upload a File")

	return render_template('upload.html', filename=filename, error=error)


if __name__ == "__main__":
    app.run(debug=True)