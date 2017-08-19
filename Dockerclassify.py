
# coding: utf-8

# In[4]:

import urllib
import json
import csv
import http
import io
from urllib.request import urlopen
from boto.s3.connection import S3Connection
from boto.s3.key import Key
import pandas as pd
import numpy as np
import time
from datetime import datetime,date,timedelta 
import requests
import logging
import time
import sklearn as sklearn
from sklearn import linear_model, metrics
from sklearn.metrics import classification_report, confusion_matrix, precision_recall_fscore_support, accuracy_score
from sklearn.cross_validation  import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier

log_file_name = "logger" + ".log"
logger = logging.getLogger(log_file_name)
hdlr = logging.FileHandler(log_file_name)
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.INFO)
bucket_name = "team_four_finals"

name_list = []

with open('config.json') as data_file:    
        data1 = json.load(data_file)

conn = S3Connection(data1['AWSAccess'], data1['AWSSecret'])
print("Established connection to S3")
logger.info("Established connection to S3")
file_name = '2008.csv'
df = []
nonexistent = conn.lookup(bucket_name)


def initialize_bucket():
    if nonexistent is None:
        logger.info("creating new bucket with name " + bucket_name)
        conn.create_bucket(bucket_name)
        existingbucket = conn.get_bucket(bucket_name)
   
        k = Key(existingbucket)
        k.key = file_name
        k.set_contents_from_filename(file_name)
    else:
        existingbucket = conn.get_bucket(bucket_name)
        for key in existingbucket.list():
            print("Bucket exists with name " + bucket_name)
            logger.info("Bucket exists with name " + bucket_name)

            new_data = Key(existingbucket)
            new_data.key = key.name     
            new_data.get_contents_to_filename(key.name)  
            flights = pd.read_csv(new_data)
            print(flights.shape)
            print("The data file is loaded in flights CSV")
    return flights

def azureMLrf(flights):
    
    min_delay = 15
    flights.dropna(subset=['CRSElapsedTime'], inplace=True)
    flights.dropna(subset=['DepDelay'], inplace=True)
    flights['CRSDepTimeinHr'] = flights['CRSDepTime']//100
    flights['CRSArrTimeinHr'] = flights['CRSArrTime']//100
    print('Data Cleaning Completed')
    direction = 'Origin'
    col2 = 'DepDelay'
    if direction == 'Origin':
        col1 = ['Month','DayOfWeek','CRSDepTimeinHr','CRSArrTimeinHr','UniqueCarrier','Dest','CRSElapsedTime','Distance']
    else:
        col1 = ['Month','DayOfWeek','CRSDepTimeinHr','CRSArrTimeinHr','UniqueCarrier','Origin','CRSElapsedTime','Distance']

    X = flights[flights[direction] == 'ATL'][col1]
    Y = flights[flights[direction] == 'ATL'][col2]
    X['UniqueCarrier'] = pd.factorize(X['UniqueCarrier'])[0]

    if direction == 'Origin':
        X['Dest'] = pd.factorize(X['Dest'])[0]
    else:
        X['Origin'] = pd.factorize(X['Origin'])[0]
    
    
    print('Performed Feature Engineering')

    random_rows = np.random.choice(X.index.values, 800000)
    random_X = X.ix[random_rows]
    random_Y = Y.ix[random_rows]

    Xtrain, Xtest, Ytrain, Ytest = train_test_split(random_X, random_Y, test_size=0.20, random_state=0)
    
    print('The data is split in 80% training data and 20% testing data')
    
    rf = RandomForestClassifier(n_estimators=50, n_jobs=-1)
    rf.fit(Xtrain,np.where(Ytrain >= min_delay,1,0) )
    pre = rf.predict(Xtest)
    conf_mat = confusion_matrix(np.where(Ytest >= min_delay,1,0), pre)
    
    No_of_actual_delays = conf_mat[1][0] + conf_mat[1][1]
    No_of_pred_delays = conf_mat[0][1] + conf_mat[1][1]
    No_of_records = conf_mat[0][1] + conf_mat[1][1] + conf_mat[1][0] + conf_mat[0][0]
    No_of_delays_properly_classified = conf_mat[1][1]
    No_of_nonDelays_improperly_classified_as_delys = conf_mat[0][1]
    
#     print(pd.DataFrame(conf_mat))
    rf_report = precision_recall_fscore_support(list(np.where(Ytest >= min_delay,1,0)), list(pre), average='micro')

    d = {'precision': [rf_report[0]],'recall':[rf_report[1]],'F1':[rf_report[2]],'accuracy':[ accuracy_score(list(np.where(Ytest >= min_delay,1,0)), list(pre))]
        ,'No_of_actual_delays':[No_of_actual_delays],'No_of_pred_delays': [No_of_pred_delays], 'No_of_records': [No_of_records], 'No_of_delays_properly_classified': [No_of_delays_properly_classified]
        ,'No_of_nonDelays_improperly_classified_as_delys': [No_of_nonDelays_improperly_classified_as_delys]}
    print(d)
    return d
   
flights = initialize_bucket()
azureMLrf(flights)


# In[ ]:



