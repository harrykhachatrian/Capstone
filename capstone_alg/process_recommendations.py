import collab_filtering as cb
import pickle 
import os
import pyodbc
import numpy as np
import csv
import random



instacart_path_test = '../instacart_2017_05_01/user_products_test.json'
user_item_list = '../instacart_2017_05_01/user_products.json'
model_path = os.getcwd() + '/capstone_alg/capstone_alg/models/model_large.pickle'
coupon_path = '../instacart_2017_05_01/coupons.csv'
product_table = '../instacart_2017_05_01/products_with_coupons.csv'

products_to_coupons = {}
coupon_table = {}

#load the product table and place coupons
def load_product_table():
    with open(product_table, 'r') as o:
        products = csv.reader(o, delimiter=',', quotechar = '"')
        for index, row in enumerate(products):
            if(index == 0):
                continue
            pid = int(row[0])
            cid = int(row[2])
            products_to_coupons[pid] = cid

#load the product table and place coupons
def load_coupon_table():
    with open(coupon_path, 'r') as o:
        coupons = csv.DictReader(o, delimiter=',', quotechar = '"')
        for index, row in enumerate(coupons):
            if(index == 0):
                continue
            cid = int(row['coupon_id'])
            c_rate = float(row['coupon_rate'])
            coupon_table[cid] = c_rate

def setup():
    load_product_table()
    load_coupon_table()
    print("loaded product and coupon table")

#gets the coupon for the product. 
#todo: implement as SQL queries?
def get_coupon_rate_for_product(pid):
    couponid = products_to_coupons[pid]
    return coupon_table[couponid]
    
#this currently reformats them for collab
#This file includes an extra step in giving recommendations.
#First the recommendations are reforated, they they are normalized,
#then a new score is computed, and then the recommendations are sorted.
def reformat_recommendations(recommendations):
    recommendations_reformated = []
    #if(type == "collab"):
    for i in recommendations:
        pid = i[0]
        conf = i[1]
        pname = i[2]
        recommendations_reformated.append(
                {
                    "product_id" : pid,
                    "confidence" : conf,
                    "product_name" : pname,
                    "coupon_rate" : get_coupon_rate_for_product(pid)
                }
            )
    return recommendations_reformated


def normalize_recommendations(recommendations):
    max_conf = 0
    max_coupon_rate = 0

    #renormalize confidence and coupon rates to be from 0 to 1
    for recommendation in recommendations:
        conf = recommendation['confidence']
        coupon_rate = recommendation['coupon_rate']
        if(conf > max_conf):
            max_conf = conf
        if(coupon_rate > max_coupon_rate):
            max_coupon_rate = coupon_rate

    for recommendation in recommendations:
        recommendation['normalized_confidence'] = recommendation['confidence'] / max_conf
        recommendation['normalized_coupon_rate'] = recommendation['coupon_rate'] / max_coupon_rate
    
    return recommendations

# coupon stuff
def process_recommendations(recommendations):

    #The weights are the importance of each thing
    weights = {
        'confidence' : 0.5,  #the confidence obtained from each algorithm
        'coupon_rate' : 0.5, #for items on sale
        'expiry' : 0.5,      #if the item will expire soon, not used currently
    }

    #expiry is a # from 0 to 1 (how close its to expiry date)
    #sale is from 0 to 1 (i.e 2% would be 0.02)
    for recommendation in recommendations:
        recommendation['final_score'] = \
        recommendation['normalized_confidence'] * weights['confidence'] \
        + recommendation['normalized_coupon_rate'] * weights['coupon_rate']

    #sort by final score
    sorted(recommendations, key=lambda x : x['final_score'])

    #another way to do it:
    #  for(i in recommendations)
    #     recommendations[i].finalScore = 
    #     (recommendations[i].confidence) * (recommendations[i].sale) * (recommendations[i].expiry)
    # sort(recommendations)

    return recommendations

#call this to process recommendations
def get_processed_recommendations(recommendations):
    recommendations = reformat_recommendations(recommendations)
    recommendations = normalize_recommendations(recommendations)
    recommendations = process_recommendations(recommendations)
    recommendations.sort(key= lambda x:x['final_score'], reverse = True)
    return recommendations


#this function generates coupons and places them into a csv file
def generate_coupons(): 
    num_coupons = 5000
    s = []
    
    #generate random values for coupons
    for i in range(num_coupons):
        rand_int = random.randint(5,50)
        percent = float(rand_int)/100
        s.append(percent)
    
    #create teh coupon csv table
    with open(coupon_path, 'w+') as o:
        colnames = ['coupon_id', 'coupon_rate']
        #csvwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csvwriter = csv.DictWriter(o, colnames)
        csvwriter.writeheader()
        for i in range(num_coupons):
            #doing +1 because all other tables start at 1
            csvwriter.writerow({'coupon_id': i+1, 'coupon_rate': s[i]})

    return
        
        