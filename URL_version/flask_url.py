import database_url
import Model_package_url
import psycopg2
import configparser  
from flask import Flask, render_template, request, send_file, url_for, flash, redirect, jsonify 
from flask_sqlalchemy import SQLAlchemy 
from psycopg2 import OperationalError, InternalError

app = Flask(__name__)
app.secret_key = 'mysecretkey'

config = configparser.ConfigParser() 
config.read('config.ini')
user = config['database_information']['DB_USER']
password = config['database_information']['DB_PASSWORD']
host = config['database_information']['DB_HOST']
port = config['database_information']['DB_PORT']
db_name = config['database_information']['DB_NAME']
table_name = config['database_information']['TABLE_NAME']
download_prediction = config['prediction']['PRED_FILE']

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://' + str(user) + ':' + str(password) + '@' + str(host) + ':' + str(port) + '/' + str(db_name)
db = SQLAlchemy(app)  

ALLOWED_EXTENSIONS = set(['csv', 'dill'])

def file_allowed(filename): 
	return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/create_database/<path:data_path>/<string:file_name>', methods=['POST', 'GET'])
def create_database(data_path, file_name): 
	if data_path == "": 
		return "Error: No path provided"
	if file_name == "":
		return "Error: No file provided"
	try: 
		db_py = database_url.Database() 
		db_py.connect(user, password, host, port, db_name, table_name)
		db_py.createTable(data_path, file_name)
	except Exception as e: 
		return str(e)
	else: 
		return "Database successfully created"

		# return render_template('display_table.html', data = part_of_data)

@app.route('/predict_model/<path:file_path>/<string:model_file_name>/<string:testing_data_name>', methods=['POST', 'GET'])
def predict_model(file_path, model_file_name, testing_data_name): 
	if file_path =="" or model_file_name =="" or testing_data_name== "": 
		return "No path or file provided"
		
	model_py = Model_package_url.Model()
	if str(download_prediction) == "True":
		try: 
			print("IN TRUE")
			prediction = model_py.predictModel(file_path, model_file_name, testing_data_name, True)
		except Exception as e:
			return render_template('return_homepage.html', error_message=str(e))
		else:
			return send_file(prediction, attachment_filename = "prediction.xlsx", as_attachment=True)
	else:
		try:
			print("IN FALSE")
			prediction = model_py.predictModel(file_path, model_file_name, testing_data_name, False)
		except Exception as e: 
			return render_template('return_homepage.html', error_message=str(e))
		else: 
			return jsonify(prediction.tolist())

if __name__ == '__main__': 
	app.run(debug=True)
