import collab_filtering as cb
import pickle 
import json
import scipy
import implicit
import os
import process_recommendations as pr
from pprint import pprint


user_item_list_test = '../instacart_2017_05_01/user_products_test.json'
user_item_list = '../instacart_2017_05_01/user_products.json'
user_item_list_large = '../instacart_2017_05_01/user_products_large.json'
model_path = os.getcwd() + '/capstone_alg/capstone_alg/models/model.pickle'

pr.setup()
#Wrapper class around library
model = cb.collabFilteringModel()
#model.fit(user_item_list_large)
#model.test(K=2)


model.load(model_path)
recommendations = model.recommend(33)
pprint(recommendations)

recommendations = pr.get_processed_recommendations(recommendations)
pprint(recommendations)
#recs_output = sorted(recom)
for rec in recommendations:
    pprint((rec['product_id'], rec['final_score'], rec['product_name']))

#model.test(K = 1)

