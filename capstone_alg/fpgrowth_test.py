
import pyfpgrowth 
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


def fp_growth():
	cursor = getconnectionstring()

	cursor.execute("""
				SELECT
					T.id_group
				FROM
				(
					SELECT DISTINCT
						string_agg(X.product_id, ',') WITHIN GROUP (ORDER BY x.product_id ASC) id_group,
						count(*) product_count
					FROM
					(
						SELECT 
							b.order_id, b.product_id
						FROM 
							order_products_train b
						WHERE 
							b.order_id < 1000
					)	X
					GROUP BY
						X.order_id
				)	T
				ORDER BY
					T.product_count DESC
				""")

	
	transactions_querey = cursor.fetchall()
	
	cursor2 = getconnectionstring()

	cursor2.execute("""
				SELECT
					product_id, product_name
				FROM 
					products
				ORDER BY
					product_name desc
				""")

	products_querey = cursor2.fetchall()

	product_dict = {}
	for row in products_querey:
		product_id = row[0]
		product_name = row[1] 
		product_dict[product_id] = product_name
		

	DB = []
	for row in transactions_querey:
		x = list([int(s) for s in row[0].split(",")])
		DB.append(x)

	patterns = pyfpgrowth.find_frequent_patterns(DB, 2)

	rules = pyfpgrowth.generate_association_rules(patterns, 0.6)
	
	bad_keys = set()

	for t in rules:
		for i in t:
			if i not in product_dict:
				bad_keys.add(t)
				

	for t in rules:
		if t in bad_keys:
			continue
		print (', '.join([product_dict[i] for i in t]))


	for t in rules:
		paired_to = rules[t][0]
		if len(paired_to) > 1:
			continue
		confidence = rules[t][1]
		product_id = t[0]
		for match_id in paired_to:	
			cursor.execute("""
						MERGE
							association_pairs AS t
						USING
						(
							SELECT
								? AS product_id,
								? AS match_id,
								NULL AS support,
								? AS confidence,
								NULL AS lift
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
						""",  product_id, match_id, confidence)


	cursor.commit()
	cursor.close()
	print("FP Growth finished")
	x = input()



fp_growth();
