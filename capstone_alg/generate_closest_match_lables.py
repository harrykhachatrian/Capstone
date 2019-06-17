import diff_match_patch as dmp_module
import pickle 
import json
import os 

path = os.getcwd() + "\\capstone_alg\\capstone_alg\\"
#label to product id
closestDistance = {}
closestIndex = {}
labelToProductId = {}
comprehensive = {} #holds product_id, distance, string_start_index

#assuming products and labels in same folder
dmp = dmp_module.diff_match_patch()
dmp.Match_Distance = 100
dmp.Match_Threshold = 0

def closestProduct(label, products):
    for product in products:
        in_string = (label in product['product_name'])
        #index = dmp.match_main(product['product_name'], label, 0)
        #if(index != -1):
        if(in_string):
            diffs = dmp.diff_main(label, product['product_name'])
            distance = dmp.diff_levenshtein(diffs)
            if(label not in closestDistance):
                labelToProductId[label] = product['product_id']
                closestDistance[label] = distance
                #closestIndex[label] = index
                comprehensive[label] = [product['product_id'], distance]#, index]
            elif(distance < closestDistance[label]):
                labelToProductId[label] = product['product_id']
                closestDistance[label] = distance
                #closestIndex[label] = index
                comprehensive[label] = [product['product_id'], distance]#, index]

with open(path + 'labels.txt', 'r+') as labels_file:
    labels = [line.rstrip('\n') for line in labels_file]
    with open(path +'products.json', 'r+',  encoding = 'utf8') as products_file:
        products = json.load(products_file)
        for label in labels:
            closestProduct(label, products)

print(labelToProductId)
with open(path+'labelsToProductsV2.json', 'w') as outfile:
    json.dump(labelToProductId, outfile)

with open(path+'labelsToProductsV2comprehensive.json', 'w') as outfile:
    json.dump(comprehensive, outfile)
# Result: [(-1, "Hell"), (1, "G"), (0, "o"), (1, "odbye"), (0, " World.")]
#dmp.diff_cleanupSemantic(diff)
# Result: [(-1, "Hello"), (1, "Goodbye"), (0, " World.")]

#print(diff)
