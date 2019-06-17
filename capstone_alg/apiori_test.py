
from apyori import apriori  
import pyodbc


def getconnectionstring():
	server = 'uoftcapstone.database.windows.net'
	database = 'CapstoneDB'
	username = 'uoftcapstone'
	password = 'DoMachineLearning1'
	driver= '{SQL Server Native Client 11.0}'
	# '{ODBC Driver 17 for SQL Server}'
	
	cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
	cursor = cnxn.cursor()

	return cursor


def do_apiori(start,end):
	cursor = getconnectionstring()
    #max order ID is 3421083
	cursor.execute("""
						SELECT
							T.id_group
						FROM
						(
							SELECT DISTINCT
								string_agg(cast(X.product_name as varchar(max)), ',') WITHIN GROUP (ORDER BY x.product_name ASC) id_group,
								count(*) product_count
							FROM
							(
								SELECT 
									b.order_id, p.product_name
								FROM 
									order_products_prior b, products p
								WHERE 
									p.product_id = b.product_id
                                AND 
		                    	    b.order_id > ?
		                        AND
		                    	    b.order_id < ?
							)	X
							GROUP BY
								X.order_id
						)	T
						ORDER BY
							T.product_count DESC
					""", start, end)
	result = cursor.fetchall()
	print(len(result))
	
	transactiontable = []
	for row in result:
		x = row[0].split(",")
		transactiontable.append(x)



	association_rules = apriori(transactiontable, min_support=0.001, min_confidence=0.2, min_lift=3, min_length=2)  
	
	association_results=[]
	for t in association_rules:
		association_results.append(t)
	
	cursor = getconnectionstring()

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
	cursor.commit()
	cursor.close()
	
	for item in association_results:
		# first index of the inner list
		# Contains base item and add item
		item_pair = list(item[0])

		print("Rule Found: {} --> {}\n".format(item_pair[0], item_pair[1]))
		
		#second index of the inner list
			
		support = item[1]
		confidence = item[2][0][2]
		lift = item[2][0][3]

		print("Support: {} \n".format(support))
		print("Confidence: {} \n".format(confidence))
		print("Lift: {} \n".format(lift))
		print("................................\n")

#THIS IS IMPORTANT
#PARTITION THE TABLE OF TRANSACTIONS INTO THE MAXIMUM UNIT THAT THE COMPUTER CAN PROCESS WITHOUT CRASHING
#CYCLE THROUGH THE DATA AND RUN THE MODEL ON THAT MANY TRANSACTIONS AT A TIME
#EACH TIME APPEND TO DATABASE 

for i in range(3421084):
    if i % 65000 == 0:
        do_apiori(i,i+65000)
