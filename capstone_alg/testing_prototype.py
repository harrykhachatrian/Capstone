
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt  
from apyori import apriori  
#from apyori2 import apriori  

import pyodbc 

import random
import csv

#only used for testing in initial stages. useless now.
def generate_data(basket_size = 16, num_transactions=100, rand_bask=True):
	with open('data.csv', newline='') as csvfile:
		inventory = list(csv.reader(csvfile))

		Rules = {
		"Coffee": "Milk",
		"Bleach" : "Laundry detergent",
		"Sugar": "Cream", 
		"Apples": "Mango",
		"Eggs": "Butter",
		"Almonds": "Peanuts",
		"Cashews": "Almonds",
		"Peanut butter": "Bread",
		"Grapes": "Banana",
		"Popcorn": "Butter",
		"Turkey stufing": "Cranberry sauce",
		"Baby Powder": "Diapers",
		"Cranberry sauce": "Turkey stuffing",
		"Peppers": "Tomatoes",
		"Asparagus": "Salmon",
		"Chicken": "Bread",
		"Milk": "Cereal",
		"Bagel": "Cream Cheese",
		"Salmon": "Asparagus",
		"Broccoli": "Cauliflower",
		"Cauliflower": "Broccoli",
		"Chips": "Salsa",
		"Chocolate": "Chocolate",
		"Wine": "Cheese",
		"Tuna": "Mayonnaise",
		"Burger": "Tomatoes",
		"Apples": "Banana",
		"Pumpin pie": "Cranberry sauce",
		"Steak": "Potato",
		"Ham": "Potato",
		"Roast Turkey": "Potato",
		"Rainbow Trout": "Asparagus",
		"Turkey": "Cranberry sauce",
		"Bacon": "Eggs",
		"Pork Sausage ": "Eggs",
		"Pasta": "Tomatoes",
		"Duck": "Asparagus",
		"Rib Roast": "Potato",
		"Scallops": "Pasta",
		"Cod": "Bread",
		"Ground Beef": "Bread",
		"Crab": "Mayonnaise",
		"Smoked Salmon": "Cream Cheese",
		"Shrimp": "Pasta",
		"Pork ribs": "Potato",
		"Pork chops": "Potato",
		"Lamb ": "Asparagus",
		"Mustard": "Ketchup",
		"Ketchup": "Mustard",
		"Mayonnaise": "Tuna",
		"Broth": "Carrots",
		"Kidney beans": "Onions",
		"Tea": "Milk",
		"Peanuts": "Almonds",
		
		"Spring mix": "Spinach",
		"Spinach": "Spring mix",
		"Tomatoes": "Asparagus",
		"Kale": "Spinach",
		"Peas": "Kidney beans",
		"Fennel": "Spinach",
		"Pickles": "Burger",
		"Avacado": "Bread",
		"Mushrooms": "Onions",
		"Cranberries ": "Turkey",
		"Grapes": "Banana",
		"Mango": "Apples",
		"Orange": "Pineapple",
		"Pineapple ": "Orange",
		"Cantalope": "Orange",
		"Pears": "Apples",
		"Figs": "Almonds",
		"Pomegranates": "Banana",
		"Apples": "Banana",
		"Frozen blueberries": "Banana",
		"Blueberries": "Rasberries",
		"Rasberries": "Blueberries",
		"Pumpkin": "Cranberry sauce",
		"Carrots": "Potato",
		"Sweet Potato": "Potato",
		"Potato": "Sweet Potato",
		"Onions": "Mushrooms",
		"Squash": "Pumpkin",
		"Brussel Sprouts": "Brocolli",
		"Cheese": "Wine",
		"Butter": "Eggs",
		"Almond Milk": "Cereal",
		"Cream Cheese": "Bagel",
		"Egg nog": "Turkey",
		"Yogurt": "Frozen blueberries",
		"Ice cream": "Blueberries",
		"Chocolate": "Chocolate",
		"Honey": "Tea",
		"Maple syrup": "Butter",
		"Orange juice": "Eggs",
		"Soda": "Chips",
		"Raisans": "Peanuts",
		"Flour": "Butter",
		"Crackers": "Salsa",
		"Chips": "Salsa",
		"Salsa": "Chipsj",
		"Cereal": "Milk",
		"Croissants": "Butter",
		"Oatmeal": "Frozen blueberries",
		"Rice": "Chicken",
		"Rosemary": "Thyme",
		"Thyme": "Rosemary",
		"Basil": "Oregano",
		"Oregano": "Basil",
		"Pumpkin pie": "Turkey stuffing",
		"Apple pie": "Tea",
		"Cheesecake": "Tea",
		"Bleach ": "Laundry detergent",
		"Laundry detergent": "Bleach",
		"Lysol wipes": "Toilet paper",
		"Fabric softener ": "Laundry detergent",
		"Parchment paper": "Flour",
		"Toilet paper": "Toilet paper",
		"Dish detergent": "Lysol wipes",
		"Diapers": "Baby Powder",
		"Banana": "Apples",
		"Cream": "Sugar",
		"Lamb" : "Potato",
		"Pork Sausage" : "Sausage Buns",
		"Pineapple" : "Blueberries",
		
		"Fabric softener" : "Laundry detergent",
		"Cranberries" : "Apples",
		"Bread" : "Butter",
		"Gravy" : "Turkey",
		"Almond butter" : "Banana"
		}
		Rules["Cream Cheese"] = "Bagels"
		
		Meat = ["Ham", "Roast Turkey", "Pork Sausage", "Duck", "Ground Beef", "Pork Chops", "Rainbow Trout", "Pork Ribs", "Lamb", "Rib Roast", "Steak"]
		
		DB = []

		for t in range(num_transactions):
			if(rand_bask == True):
				basket_size = random.randint(1,7)
			myCart = []
			for i in range(basket_size):
				item = inventory[random.randint(1,115)]
				item_str = ''.join(item)
				match = Rules[item_str]
				while(match in myCart or item_str in myCart or match in Meat):
					item = inventory[random.randint(1,104)]
					item_str = ''.join(item)
					match = Rules[item_str]

				myCart.append(item_str)
				myCart.append(match)
			DB.append(myCart)

		with open('output_table_test','w') as file:
			csv_out = csv.writer(file)
			for row in DB:
				csv_out.writerow(row)
				#for food_item in row:
					#item_pair = (row_number, food_item)
					#csv_out.writerow(row)
				

		association_rules = apriori(DB, min_support=0.05, min_confidence=0.501, min_lift=3, min_length=2)  
	
		association_results=[]

		for t in association_rules:
			association_results.append(t)

	
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

			#propogate the longest row up to be the first row
			#for the pandas function that reads the data for machine learning
			#because it takes the top row length as its max row length
			longest = 0
"""			for row in DB:
				if (len(row) > longest):
					longest = len(row)
					longest_row = row
				
				if len(DB[0]) < longest:
					temp = DB[0]
					DB[0] = longest_row
					longest_row = temp 

			#write the generated data to a CSV file 
			with open('generated_data.csv','w') as file:
				for line in range(len(DB)):
					file.write(', '.join(DB[line]))
					file.write('\n')
"""
#not used at the moment, but could be used if needed. Just rotates a table to put it into SQL DB
def create_pivot(input_table, output_table):
	file_name = input_table #filename is argument 1

	with open(file_name, 'rU') as f:  #opens PW file
		reader = csv.reader(f)
		data = list(list(rec) for rec in csv.reader(f, delimiter=',')) #reads csv into a list of lists
	#print(type(data), type(data[0]), len(data), len(data[0]))
	pivot = []
	row_number = 0



	print("created pivoted data")

#This function isn't used anymore. Previously for propogating the longest row to top, but I just did that in SQL instead. Faster. 
#def longest_row_top(DB):

#	#propogate the longest row up to be the first row
#	#for the pandas function that reads the data for machine learning
#	#because it takes the top row length as its max row length
#	length_of_longest = 0
#	longest_row = []
#	index_of_longest = 0;
#	for row in DB:
#		if (len(row) > length_of_longest):
#			length_of_longest = len(row)
#			longest_row = row
#			index_of_longest = DB.index(longest_row)
				
#	if len(DB[0]) < length_of_longest:
#		temp = DB[0]
#		DB[0] = longest_row
#		DB[index_of_longest] = temp

#	return (DB, length_of_longest)






def do_machine_learning(records, output_filename, length_of_longest_row):
		

	print(len(records))
	association_rules = apriori(records, min_support=0.015, min_confidence=0.2, min_lift=3, min_length=2)  

	association_results = []
	for t in association_rules:
		association_results.append(t)

	with open(output_filename,'w') as file:
		for item in association_results:
			# first index of the inner list
			# Contains base item and add item
			pair = item[0] 
			items = [x for x in pair]
			file.write("Rule: " + items[0] + " -> " + items[1] + "\n")

			#second index of the inner list
			file.write("Support: " + str(item[1]) + "\n")

			#third index of the list located at 0th
			#of the third index of the inner list

			file.write("Confidence: " + str(item[2][0][2]) + "\n")
			file.write("Lift: " + str(item[2][0][3]) + "\n")
			file.write("=====================================\n")






"""

cnxn = pyodbc.connect("Driver={SQL Server Native Client 11.0};"
                      "Server=harryk;"
                      "Database=CapstoneDB;"
                      "Trusted_Connection=yes;")

cursor = cnxn.cursor()
#"""
#cursor.execute("""
#					SELECT
#						T.id_group
#					FROM
#					(
#						SELECT DISTINCT
#							string_agg(X.product_name, ',') WITHIN GROUP (ORDER BY x.product_name ASC) id_group,
#							count(*) product_count
#						FROM
#						(
#							SELECT 
#								b.order_id, p.product_name
#							FROM 
#								order_products_train b, products p
#							WHERE 
#								p.product_id = b.product_id
#								AND
#								order_id < 10000
#						)	X
#						GROUP BY
#							X.order_id
#					)	T
#					ORDER BY
#						T.product_count DESC
#				""")
#"""
#"""
#length_of_longest_row = 0
##result = cursor.fetchall() 
#DB = []
#for row in result:
#	x = row[0].split(",")
#	length_of_longest_row = max(len(x), length_of_longest_row)
#	DB.append(x)


#for t in DB:
#	print("\n")
#	print (t)

#write the generated data to a CSV file 
#with open('SQL_data.csv','w') as file:
#	for rec in DB:
#		line = ','.join(rec)
#		file.write(line)
#		file.write('\n')


#do_machine_learning(DB, "test_output.txt",length_of_longest_row)






#Rules = {}
#		with open("my_rules.txt") as f:
#				for line in f:
#					row = line.split(',')
#					for element in row:
#							(key,val) = element.split(':')
#							Rules[key] = val





generate_data()
x = input()







