


import sys
import os

module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'.'))
sys.path.append(module_dir)

from _bigquery_pull import pull_data_from_bigquery, transform_data, write_preds_bigquery
#from data import read_data, pull_data_from_bigquery
#from models import DNN
#from evaluation import MAE, sMAPE
import argparse
import pandas as pd 
import numpy as np 
from google.cloud import bigquery

client = bigquery.Client(project='643838572067')
calibration_window = 1
    





data, last_date = pull_data_from_bigquery(client, calibration_window)
print('last_date: ', last_date)
print('data.shape: ', data.shape)
begin_test_date = last_date + pd.Timedelta(hours=1)
end_test_date = begin_test_date + pd.Timedelta(hours=23)

print('begin_test_date: ', begin_test_date)
print('end_test_date: ', end_test_date)



df_train, df_test = transform_data(data, begin_test_date, end_test_date)

print('df_train.shape: ', df_train.shape)
print('df_test.shape: ', df_test.shape)

print('df_train.head(): ', df_train.head(1))