import database
import pandas as pd
import xlsxwriter as xl
import dill as pickle 
import configparser
import os
from io import BytesIO 


class Model: 
	# This function is used to predict any model the user uploads to the flask app.
	# Depending on user's settings the function returns a file with predicted values or 
	# displays the predicted values in a webpage.
	def predictModel(self, file_path,model_file_name, testing_data_name, download_prediction):
		config = configparser.ConfigParser() 
		config.read('config.ini')
		print("IN PREDICTMODELURL")
		os.chdir(file_path)
		xTestData = pd.read_csv(testing_data_name)
		xTestData = xTestData.values

		model = open(str(model_file_name), "rb")
		classifier = pickle.load(model)
		prediction = None
		try:
			prediction = classifier.predict(xTestData)
		except Exception: 
			raise("predict() does not exist for the provided model")

		if download_prediction: 
			output = BytesIO() 
			predictionFile = xl.Workbook(output)
			worksheet = predictionFile.add_worksheet() 
			col = 0 
			for row, pred in enumerate(prediction): 
				worksheet.write(row, col, pred)
			predictionFile.close() 

			output.seek(0)
			return output

		else: 
			return prediction
			
