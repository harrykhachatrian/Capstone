

import pyfpgrowth 
from apyori import apriori
import pyodbc
import time, operator

PROFLE_FUNCTION = True
PROFILE_RESULTS = {}


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


def profile(method):
    """ Profiling decorator. """
    def wrapper(*args, **kw):
        if PROFLE_FUNCTION is False:
            return method(*args, **kw)
        
        start = time.clock()
        #
        result = method(*args, **kw)
        #
        duration = time.clock() - start
        if method.__name__ not in PROFILE_RESULTS:
            PROFILE_RESULTS[method.__name__] = (duration, 1)
        else:
            runtimes = PROFILE_RESULTS[method.__name__][0] + duration
            calls = PROFILE_RESULTS[method.__name__][1] + 1
            average = runtimes / calls

            PROFILE_RESULTS[method.__name__] = (average, calls)
        
            print('Stats for method: {!r}'.format(method.__name__))
            print('  total calls: {}'.format(calls))
            print('  average run time: {}'.format(average))
        return result
    return wrapper  # Decorated method (need to return this).


#######################################################################################
#######################################################################################
#######################################################################################
###### FP GROWTH ALGORITHM ############################################################
@profile
def fp_growth():
	
	transaction_table_cursor = getconnectionstring()


	#cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
 #                     "Server=uoftcapstone3.database.windows.net;"
 #                     "Database=CapstoneDB;"
 #                     "Trusted_Connection=yes;")
	
	#cursor = cnxn.cursor()

	transaction_table_cursor.execute("""
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
							b.order_id < 10000
					)	X
					GROUP BY
						X.order_id
				)	T
				ORDER BY
					T.product_count DESC
				""")

	
	transactions_querey = transaction_table_cursor.fetchall()
	
	products_table_cursor = getconnectionstring()


	products_table_cursor.execute("""
				SELECT
					product_id, product_name
				FROM 
					products
				ORDER BY
					product_name desc
				""")

	products_querey = products_table_cursor.fetchall()

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

	rules_lst = []
	for key,value in rules.items():
		rules_lst.append((key,value))
	
	#bkup = rules_lst
	#for t in bkup:
	#	t[1] = t[1][0:-1]

	
	


	print("\n FP GROWTH RESULTS \n")
	#for t in rules:
	#	print (','.join(product_dict[i] for i in t))
	for x in rules:
		print(product_dict[x])
		for y in rules[product_dict[x]]:
			print(y , ':', product_dict[x][y])

	
	print("\n")




#######################################################################################
#######################################################################################
#######################################################################################
###### APIORI ALGORITHM ############################################################
@profile
def appriori():
		
	#cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
 #                     "Server=harryk;"
 #                     "Database=CapstoneDB;"
 #                     "Trusted_Connection=yes;")

	cursor = getconnectionstring()

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
	records = []
	for row in result:
		x = row[0].split(",")
		records.append(x)

	for t in records[:3]:
		print(t)
		print(type(t))
		print(type(t[0]))

	association_rules = apriori(records, min_support=0.045, min_confidence=0.2, min_lift=3, min_length=2)  

	#association_results = []
	print("apriori in")
	association_results = list(association_rules)
	print("ready")
	#for t in association_rules:
	#	association_results.append(t)

	print("\n APIORI RESULTS \n")
	for item in association_results:
		# first index of the inner list
		# Contains base item and add item
		pair = item[0] 
		items = [x for x in pair]
		print("Rule: " + items[0] + " -> " + items[1] + "\n")
	print("\n\n")





fp_growth()
appriori()

print('func_runtimes:', PROFILE_RESULTS)
