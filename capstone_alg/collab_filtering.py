#This file defines a wrapper class that loads/saves collab fib models,
#including mappings to user and products ids

import numpy as np
import json
import implicit
import scipy
import pyodbc 
import random
import csv
import os
import pickle
import time
import csv
from implicit.evaluation import precision_at_k, train_test_split


#implicit.evaluation.train_test_split()

#helper functions for saving/loadings models
def save_object(obj, file_path):
    with open(file_path, 'w+b') as obj_file:
        pickle.dump(obj, obj_file)

def load_object(file_path):
    obj = pickle.load(open(file_path, "rb"))
    return obj

cwd = os.getcwd()


instacart_products = '../instacart_2017_05_01/products.json'
default_model_save_path = cwd + '/capstone_alg/capstone_alg/models/model.pickle'

class collabFilteringModel:
    user_mappings={}    #mapping of user id to matrix index
    product_mappings={} #mapping of product id to matrix index
    index_to_product_id = {}
    save_path = None
    max_users = 206209  
    #max_users = 135000
    #hardcoding these for now because there's more products than orders
    #some products are not bought with the current data, so there could be
    #rows that are all 0. 
    max_products = 49688 

    product_user_matrix_lil = None
    product_user_matrix = None
    model = None
    product_list = None
    product_map = {}
   

  
    def __init__(self, save_path=default_model_save_path, user_item_list=None, max_users=None, max_products=None):
        if(max_users != None):
            self.max_users = max_users
        if(max_products != None):
            self.max_products = max_products

        self.save_path = save_path
        with open(instacart_products, encoding="utf8") as f:
            self.product_list = json.load(f)
            for p in self.product_list:
                pid = int(p['product_id'])
                self.product_map[pid] = p
        return
        

    #filename - path of a json file with a list of user-id to product id + other info
    # in the format
    # {
    #     user_id:
    #     product_id:
    #     order_id:
    #     ...other attributes (reordered, order sequence)
    # }
    # 

    #todo: move function elsewhere
    def create_item_user_matrix(self, filename, max_users, max_products, lil=None):
        #counters for mapping user id to the user item matrix indices
        unique_user_count = 0
        user_index = 0
        unique_product_count = 0
        product_index = 0
        
        user_mappings = {}
        product_mappings = {}

        max_score = 5;     
        #lil_matrix is a sparse matrix that can be efficiently resized
        product_user_matrix_lil = None 
        
        with open(filename) as f:
            products_bought_by_user = json.load(f)
            #first count unique products and unique users (yes this is not the best way of doing it)
            for index, row in enumerate(products_bought_by_user):
                user_id = int(row['user_id'])
                product_id = int(row['product_id'])

                #map user ids to indices, since user ids
                #can be any #, and since there's missing user ids
                #in the data (i.e it goes user1,user3,user6, etc...)
                if(user_id not in user_mappings):
                    user_mappings[user_id] = unique_user_count
                    unique_user_count+=1
           


            
            product_user_matrix_lil = scipy.sparse.lil_matrix((max_products, max_users))
                

            for index, row in enumerate(products_bought_by_user):
                user_id = int(row['user_id'])
                product_id = int(row['product_id'])
                user_index = user_mappings[user_id]
                product_index = product_mappings[product_id]
                reordered = int(row['reordered'])

                #skip users that havn't been mapped to an in-bounds index
                if(user_index >= max_users):
                    continue

                #Assign a score of 1 for every item a user has ever bought for now
                #this is the "likelihood that the person likes the item".
                #It would be better to play around with this and factor in things like
                #whether the item has been reordered.
                #score = 1.0
                # current_score = product_user_matrix_lil[product_index,user_index]
                # if(current_score < max_score):
                current_score = 1
                if(reordered):
                    current_score += 1
                    #print(current_score)
                product_user_matrix_lil[product_index,user_index] = current_score
                    # if(current_score > 1):
                    #     print((product_index, user_index), ":", current_score+1)
                
        
        if(lil == None):
            product_user_matrix = product_user_matrix_lil.tocsr()
        else:
            product_user_matrix = product_user_matrix_lil
     
        return product_user_matrix, user_mappings

    def create_item_user_matrix_light(self, filename, max_users, max_products, lil=None):
        ordersfile = '../instacart_2017_05_01/orders.csv'
        orderspriorfile = '../instacart_2017_05_01/order_products__prior.csv'
        #counters for mapping user id to the user item matrix indices
        unique_user_count = 0
        user_index = 0
        unique_product_count = 0
        product_index = 0
        
        user_mappings = {}
        product_mappings = {}

        max_score = 5;     
        #lil_matrix is a sparse matrix that can be efficiently resized

        #orders to use mapping:
        orders_to_user = {}
        product_user_matrix_lil = scipy.sparse.lil_matrix((max_products, max_users))
        with open(ordersfile, 'r', encoding = 'utf8') as o:
            orderid_col = 0
            userid_col = 1

            orders = csv.reader(o, delimiter=',', quotechar = '"')
            for index, row in enumerate(orders):
                if(index == 0):
                    continue
                orderid = int(row[orderid_col])
                userid = int(row[userid_col])
                orders_to_user[orderid] = userid

        with open(orderspriorfile, 'r', encoding = 'utf8') as op:
            ordersprior = csv.reader(op, delimiter=',', quotechar = '"')
            orderid_col = 0
            product_id_col = 1
            add_to_cart_col = 2
            reordered_col = 3
            #products_bought_by_user = json.load(f)
            #first count unique products and unique users (yes this is not the best way of doing it)
            for index, row in enumerate(ordersprior):
                if(index == 0):
                    continue
                order_id = int(row[orderid_col])
                user_id = orders_to_user[order_id]
                product_id = int(row[product_id_col])
                #product_id - 1
                #map user ids to indices, since user ids
                #can be any #, and since there's missing user ids
                #in the data (i.e it goes user1,user3,user6, etc...)
                if(user_id not in user_mappings):
                    user_mappings[user_id] = unique_user_count
                    unique_user_count+=1
                if(product_id not in product_mappings):
                    product_mappings[product_id] = unique_product_count
                    self.index_to_product_id[unique_product_count] = product_id
                    unique_product_count+=1

                user_index = user_mappings[user_id]
                product_index = product_mappings[product_id]
               
                 # current_score = product_user_matrix_lil[product_index,user_index]
                # if(current_score < max_score):
                current_score =  product_user_matrix_lil[product_index,user_index]
                current_score+=1
                #if(reordered):
                #    current_score += 1
                    #print(current_score)
                product_user_matrix_lil[product_index,user_index] = current_score
                    # if(current_score > 1):
                    #     print((product_index, user_index), ":", current_score+1)

            
            
                

        
        if(lil == None):
            product_user_matrix = product_user_matrix_lil.tocsr()
        else:
            product_user_matrix = product_user_matrix_lil
            
        self.product_mappings = product_mappings
        return product_user_matrix, user_mappings
        
    
    #organize list into user_id : [purchase1, purchase2...] etc
    #where purchases are sorted by order_id (assuming that lower order ids came before in time)
    def load_and_reorganize_list(self, filename, max_products, max_users):
        unique_user_count = 0
        user_index = 0
        unique_product_count = 0
        product_index = 0
        
        user_mappings = {}
        product_map = {}
        #max_products = sel
        user_to_product_lists = []
        with open(filename) as f:
            products_bought_by_user = json.load(f)
            #first count unique products and unique users (yes this is not the best way of doing it)
            for index, row in enumerate(products_bought_by_user):
                user_id = int(row['user_id'])
                product_id = int(row['product_id'])

                if(user_id not in user_mappings):
                    #if(unique_user_count < self.max_users):
                    user_mappings[user_id] = unique_user_count
                    user_to_product_lists.append({
                        'products_bought':[row]
                    })
                    #user_index = unique_user_count
                    unique_user_count+=1
                else:
                    user_index = user_mappings[user_id]
                    user_to_product_lists[user_index]['products_bought'].append(row)

                
                max_users = unique_user_count
                #max_products = max_products
            
            for index, row in enumerate(user_to_product_lists):
                sorted(row['products_bought'], key=lambda purchase : purchase['order_id'])

        return user_to_product_lists

    #call the implicit library function to build a predictive model
    #list_name: the name of the list of user-items bought, in json format
    #save:      whether to save the model
    #save_path: the save path
    def fit(self, list_name, save=True):
        self.product_user_matrix, self.user_mappings = self.create_item_user_matrix_light(list_name, self.max_users, self.max_products)

        #movies, ratings = implicit.datasets.movielens.get_movielens("1m")
        train, test = train_test_split(self.product_user_matrix,0.8)
        self.model = implicit.als.AlternatingLeastSquares(factors=100, iterations=15)

        # train the model on a sparse matrix of item/user/confidence weights
        #self.model.fit(self.product_user_matrix)
        self.model.fit(train)
        p = precision_at_k(self.model, train.T.tocsr(), test.T.tocsr(), K=10, num_threads=4)
        print(p)
        
        if(save):
            saveobj = {
                'product_user_matrix': self.product_user_matrix,
                'model': self.model,
                'user_mappings': self.user_mappings,
                'product_mappings': self.product_mappings,
                'max_users' : self.max_users,
                'index_to_product_id' : self.index_to_product_id,
                'max_products' : self.max_products
                #'product_user_matrix_lil' : self.
            }
            save_object(saveobj, self.save_path)
            
        return self.model
    
    def test(self, train_size=0.8, K=10):
        train, test = train_test_split(self.product_user_matrix,0.8)
        p = precision_at_k(self.model, train.T.tocsr(), test.T.tocsr(), K, num_threads=2)
        print ("precision at K =", K, ":", p)
 
    def test_initial(self, test_size=0.2):
        start_test_time = time.time()

        #get a lil matrix, because it can be reshaped more easily
        item_user_lil_test = self.product_user_matrix.tolil(copy=True)
        nonzeros = self.product_user_matrix.nonzero()
    
        #count how many non zeros there are which represent
        #total user item associations, and the test set size
        num_non_zeros = len(nonzeros[0])
        num_new_zeros = int(num_non_zeros * test_size)


        #here rows are products, columns are users
        for index, rowindex in enumerate(nonzeros[0]):
            #need to reshuffle probably
            if(index < num_new_zeros):
                colindex = nonzeros[1][index]
                #print(rowindex)
                item_user_lil_test[rowindex, colindex] = 0
            else:
                break

        item_user_csr_test = item_user_lil_test.tocsr()
        test_progress = 0
        true_postive = 0

        #count unique # of products per user
        user_items_csr_test = item_user_csr_test.T.tocsr()
        unique, counts = np.unique(nonzeros[1], return_counts=True)

        unique_items_per_user = dict(zip(unique, counts))

        #loop through all users
        for i in range(self.max_users):
            
            #test only if the user has more than some number of prooducts
            if i not in unique_items_per_user:
                continue

            total_unique_items_per_user = unique_items_per_user[i]
            if(total_unique_items_per_user > 0):

                #get recommendations, loop through them, and compare predictions against
                #actual values in the matrix
                recommendations = self.model.recommend(i, user_items_csr_test, recalculate_user=True)
                for index, j in enumerate(recommendations):
                    pid = j[0]
                    #compare against actual matrix
                    if(self.product_user_matrix[pid,i] > 0):
                        true_postive += 1
            if(i % 1000 == 0):
                print("Test progress : " + str(i / self.max_users))

        accuracy = true_postive/num_new_zeros

        end_test_time = time.time()
        total_test_time = end_test_time - start_test_time 


                
        print("The test result is " + str(accuracy) + "\n")
        print("The test time is " + str(total_test_time))
        #for all users with
        return accuracy


    #if list_name is provided it'll recommend items on a new user, who'se index
    #is in the matrix created from the list_name
    def recommend(self, user_id, csr_matrix=None, user_mappings=None, list_name = None, ):

        product_user_matrix = None
        if(csr_matrix is not None):
            product_user_matrix = csr_matrix
        elif(list_name is not None):
            product_user_matrix, user_mappings = self.create_item_user_matrix(list_name, self.max_users, self.max_products)
        else:
            product_user_matrix = self.product_user_matrix
            user_mappings = self.user_mappings

        product_mappings = self.product_mappings

        #get recommendations
        user_items = product_user_matrix.T.tocsr()
        recommendations = self.model.recommend(user_mappings[user_id], user_items, recalculate_user=True)

        #add the product names to the recommendations by reading
        #them from the products file
       
        for index,i in enumerate(recommendations):
            # i[1] is the prediction of how much a user would like the item
            if(i[1] > 0):
                
                index2 = np.asscalar(i[0])
                #Todo : need to fix this
                pid = self.index_to_product_id[index2]
                product = self.product_map[pid]
                tup = (product['product_id'], i[1], product['product_name'])
                #tup = recommendations[index]
                #tup[1] += 1
                #tup = tup + (self.product_list[index2]['product_name'],)
                #each tuple is in form (index_in_matrix, confidence user likes item, name of item)
                recommendations[index] = tup
                
            else:
                recommendations.remove(i)
        
        return recommendations

    def load(self, file_path = default_model_save_path):
        #probably not a good way of doing this...
        obj = load_object(file_path)
        self.product_user_matrix = obj['product_user_matrix']
        self.user_mappings = obj['user_mappings']
        self.product_mappings = obj['product_mappings']
        self.max_products = obj['max_products']
        self.max_users = obj['max_users']
        self.index_to_product_id = obj['index_to_product_id']
        self.model = obj['model']
            



                
                    

                
# def getconnectionstring():
# 	server = 'uoftcapstone3.database.windows.net'
# 	database = 'CapstoneDB'
# 	username = 'uoftcapstone'
# 	password = 'DoMachineLearning1'
# 	driver= '{SQL Server Native Client 11.0}'
# 	# '{ODBC Driver 17 for SQL Server}'
	
# 	cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
# 	cursor = cnxn.cursor()

# 	return cursor

# cursor = getconnectionstring()