import database
import csv
import sklearn
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import xlsxwriter as xl
import dill as pickle 
from io import BytesIO 


class Model: 
	# This function is used to predict any model the user uploads to the flask app.
	# Depending on user's settings the function returns a file with predicted values or 
	# displays the predicted values in a webpage.
	def predictModel(self, x_test_file, model_file, download_prediction):
		xTestData = pd.read_csv(x_test_file)
		xTestData = xTestData.values

		model = open(str(model_file), "rb")
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
			
