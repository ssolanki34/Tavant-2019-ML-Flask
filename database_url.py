import sqlalchemy as sql 
import pandas as pd 
import psycopg2
import psycopg2
import os 
from psycopg2 import OperationalError, InternalError

"""
This class will be used to connect to the postgresql database and load the data
from the provided data file. A postgresql account should be created before 
using this class. 
"""

class Database:
	user = ""
	password = ""
	host = ""
	port = ""
	tableName = ""
	connection = None 

	def __init__(self): 
		self.__database = ""
		self.__dataFile = ""

	# Connect to database 
	def connect(self, user, password, host, port, databaseName, tableName):
		Database.user = str(user) 
		Database.password = str(password)
		Database.host = str(host)
		Database.port = str(port)
		Database.tableName = str(tableName).lower() 
		self.__databaseName = str(databaseName)
		
		try:
			Database.connection = psycopg2.connect(user = Database.user, password = Database.password, host = Database.host, port = Database.port, database = self.__databaseName)
		except OperationalError: 
			raise

	def getDataType(self, data): 
		if (str(data) == "object"):
			return sql.String
		if (str(data) == "int64"): 
			return sql.Integer
		if (str(data) == "float64"):
			return sql.Float
		if (str(data) == "bool"):
			return sql.Boolean
		if (str(data) == "datetime64"):
			return sql.DateTime
		else: 
			return sql.String
	
	# Creates a table with the file given by the user 
	def createTable(self, pathToFile, dataFile):
		self.__dataFile = str(dataFile)
		try:
			url = 'postgresql://' + Database.user + ':' + Database.password + "@" + Database.host + "/" + self.__databaseName
			engine = sql.create_engine(url)
			engineConnection = engine.connect()
			metadata = sql.MetaData()

			os.chdir(pathToFile)

			data = pd.read_csv(self.__dataFile)
			cols = data.dtypes.iteritems() # tuples of column data ('Column Name', data type) 

			columnNames = []
			columnTypes = []
			primaryKeyFlags =[True]

			for c in cols: 
				columnNames.append(c[0])
				columnTypes.append(self.getDataType(c[1]))
				primaryKeyFlags.append(False)

			try:
				table = sql.Table(Database.tableName, metadata, 
									*(sql.Column(columnName, columnType, primary_key=primaryKeyFlag) 
									for columnName, columnType, primaryKeyFlag in zip(columnNames, columnTypes, primaryKeyFlags)))
				metadata.create_all(engine)
			except Exception as e: 
				print("error in creating table with columns ")
				raise
			
			cursor = Database.connection.cursor() 

			# Remove header from data file 
			with open(self.__dataFile, 'r') as f: 
				with open("modified_file.csv", 'w') as no_header_data: 
					next(f)
					for line in f: 
						no_header_data.write(line)
					no_header_data.close()
					f.close()

			with open("modified_file.csv") as no_header_data:
				try:
					cursor.copy_from(no_header_data, table=Database.tableName, sep=',')
					cursor.execute 
				except psycopg2.IntegrityError: 
					Database.connection.rollback()
					raise 
				else: 
					Database.connection.commit()
					no_header_data.close()
		
		except psycopg2.errors.UniqueViolation as e:
			return 
		except Exception as e: 
			raise
	
	# returns list of tuples, each tuple is a row of the data 
	def getAllData(self): 
		try:
			cursor = Database.connection.cursor()
			if(Database.tableName != ""):
				table = "public."+ "\"" + Database.tableName + "\""
				query = """SELECT * from """
				try: 
					cursor.execute(query+table)
				except psycopg2.IntegrityError:
					Database.connection.rollback()
			else: 
				raise

		except psycopg2.InternalError as e: 
			raise  
		except Exception as e:  
			raise 
		else:   
			return cursor.fetchall() 

	# returns specific number of rows (user-specified) of data 
	def getPartData(self, num_rows): 
		try: 
			cursor = Database.connection.cursor()
			if(Database.tableName != ""): 
				table = "public."+ "\"" + Database.tableName + "\""
				query = """SELECT * from """
				try: 
					cursor.execute(query+table)
				except psycopg2.IntegrityError: 
					Database.connection.rollback()
			else: 
				raise

		except psycopg2.InternalError as e: 
			print("InternalError while retrieving data:")
			print(e)
			raise

		except Exception as e: 
			print("Error while retrieving data:")
			print(e)
			raise

		else:
			return cursor.fetchmany(num_rows)