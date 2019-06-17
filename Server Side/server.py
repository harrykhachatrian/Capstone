from bottle import route, run, get, post, response, request

import pyodbc
import json

from algs import get_collab_filter_result
import numpy as np


#def get_SQL_connection ():
#	cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
#                      "Server=harryk;"
#                      "Database=CapstoneDB;"
#                      "Trusted_Connection=yes;")
#	cursor = cnxn.cursor()
#	return cursor


def get_SQL_connection():
	server = 'uoftcapstone.database.windows.net'
	database = 'CapstoneDB'
	username = 'uoftcapstone'
	password = 'DoMachineLearning1'
	driver= '{SQL Server Native Client 11.0}'
	# '{ODBC Driver 17 for SQL Server}'
	
	cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
	cursor = cnxn.cursor()

	return cursor



@get('/product')
def get_products():
	cur = get_SQL_connection()
	cur.execute("SELECT product_id, product_name FROM products")
	products = []
	for row in cur:
		x = {"id": row[0], "name":row[1]}
		products.append(x)

	j_obj = json.dumps(products)
	response.content_type = 'application/json; charset=utf-8'
	return j_obj

def default(o):
	if isinstance(o, np.int64): return int(o)
	raise TypeError

@get('/suggestion_user/<user_id>')
def get_collab_results(user_id):
	print("this is ,", user_id)
	print("this is type ,", type(user_id))

	print("this is ,", int(user_id))
	print("this is type ,", type(int(user_id)))
	
	collab = get_collab_filter_result(int(user_id))
	j_obj = json.dumps(collab, default=default)
	response.content_type = 'application/json; charset=utf-8'
	return j_obj

@get('/suggestion/<product_id>')
def get_suggestion(product_id):
	cur = get_SQL_connection()
	cur.execute("SELECT match_id, product_id FROM association_pairs WHERE product_id = ? ORDER BY confidence desc", product_id)
	products = []
	for row in cur:
		x = {"id": row[0], "name":row[1]}
		products.append(x)

	j_obj = json.dumps(products)
	response.content_type = 'application/json; charset=utf-8'
	return j_obj


@get('/purchase_history/<user_id>')
def get_history_user(user_id):
	cur = get_SQL_connection()
	cur.execute("SELECT (product_id) FROM [dbo].[order_products_prior] as pp, [dbo].[orders] as o WHERE o.user_id = ? AND pp.order_id=o.order_id", user_id)
	pids = []
	for row in cur:
		pids.append(row[0])
	j_obj = json.dumps(pids)
	response.content_type = 'application/json; charset=utf-8'
	return j_obj
	
@post('/transaction')
def add_transaction():
	body = request.body.read()
	transaction = json.loads(body)

	for x in range(0, len(transaction)):
		transaction[x] = int(transaction[x])

	for x in transaction:
		pass

	response.content_type = 'application/json; charset=utf-8'
	 


@route('/')
def http_service():
	data = ""
	with open('page.html', 'r') as myfile:
		data=myfile.read()

	return data


@route('/hello')
def hello():
    return "Hello World!"

print("in server")
run(host='0.0.0.0',port=8080,debug=True) 