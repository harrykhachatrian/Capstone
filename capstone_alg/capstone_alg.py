#import numpy as np
#import pandas as pd
#import matplotlib.pyplot as plt  
from apyori import apriori  
#from apyori2 import apriori  

import bottle 

import pyfpgrowth 

import pyodbc
#import random
#import csv



def do_machine_learning(records, output_filename):
	association_rules = apriori(records, min_support=0.007, min_confidence=0.2, min_lift=3, min_length=2)  
	
	association_results=[]
	for t in association_rules:
		association_results.append(t)

	cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=harryk;"
                      "Database=CapstoneDB;"
                      "Trusted_Connection=yes;")
	
	cursor = cnxn.cursor()

	for item in association_results: 
		item_pair = list(item[0])

		product_id = item_pair[0]
		match_id = item_pair[1]
		support = item[1]
		confidence = item[2][0][2]
		lift = item[2][0][3]

		cursor.execute("""
				MERGE
					association_pairs AS t
				USING
				(
					SELECT
						a.product_id AS product_id,
						b.product_id AS match_id,
						? AS support,
						? AS confidence,
						? AS lift
					FROM
						products a
					JOIN
						products b
					ON
						a.product_name = ?
						AND b.product_name = ?
				) AS x
				ON
					t.product_id = x.product_id
					AND t.match_id = x.match_id
				WHEN MATCHED THEN
					UPDATE SET
						t.support = x.support,
						t.confidence = x.confidence,
						t.lift = x.lift
				WHEN NOT MATCHED THEN
					INSERT (product_id, match_id, support, confidence, lift)
					VALUES (x.product_id, x.match_id, x.support, x.confidence, x.lift);
				""", support, confidence, lift, product_id, match_id)
	cnxn.commit()

	with open(output_filename,'w') as file:
		for item in association_results:
			# first index of the inner list
			# Contains base item and add item
			item_pair = list(item[0])

			file.write("Rule Found: {} --> {}\n".format(item_pair[0], item_pair[1]))
		
			#second index of the inner list
			
			support = item[1]
			confidence = item[2][0][2]
			lift = item[2][0][3]

			file.write("Support: {} \n".format(support))
			file.write("Confidence: {} \n".format(confidence))
			file.write("Lift: {} \n".format(lift))
			file.write("................................\n")
			 


def query_SQL (Server, Database):
	cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=" + Server + ";"
                      "Database=" + Database + ";"
                      "Trusted_Connection=yes;")


	cursor = cnxn.cursor()

	cursor.execute("""
						SELECT
							T.id_group
						FROM
						(
							SELECT DISTINCT
								string_agg(X.product_name, ',') WITHIN GROUP (ORDER BY x.product_name ASC) id_group,
								count(*) product_count
							FROM
							(
								SELECT 
									b.order_id, p.product_name
								FROM 
									order_products_train b, products p
								WHERE 
									p.product_id = b.product_id
									AND
									order_id < 10000
							)	X
							GROUP BY
								X.order_id
						)	T
						ORDER BY
							T.product_count DESC
					""")


	result = cursor.fetchall()
	return  result


def list_from_SQL(query):
	DB = []
	for row in query:
		x = row[0].split(",")
		DB.append(x)
	return DB


#just set the server and database name here, and call the query_SQL function 
server = 'harryk'
database = 'CapstoneDB'
result = query_SQL(server, database)

#this function just takes the SQL result and turns it into a list of lists in python so we can do machine learning on it
DB = list_from_SQL(result)

#with open('SQL_data_prior.csv','w') as file:
#	for rec in DB:
#		line = ','.join(rec)
#		file.write(line)
#		file.write('\n')                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          



do_machine_learning(DB, "test_output_train.txt")

