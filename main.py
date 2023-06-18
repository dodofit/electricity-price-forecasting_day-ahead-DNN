"""
Example for using the DNN model for forecasting prices with daily recalibration
"""

# License: AGPL-3.0 License


import sys
import os

module_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),'toolbox'))
sys.path.append(module_dir)

from data import read_data, pull_data_from_bigquery, transform_data, write_preds_bigquery
from models import DNN
from evaluation import MAE, sMAPE
import argparse
import pandas as pd 
import numpy as np 
from google.cloud import bigquery
import base64


def main(request):

        # ------------------------------ EXTERNAL PARAMETERS ------------------------------------#

    parser = argparse.ArgumentParser()

    parser.add_argument("--nlayers", help="Number of layers in DNN", type=int, default=3)

    parser.add_argument("--dataset", type=str, default='FR_NEW_UTC_W_RENEW', 
                        help='Market under study. If it not one of the standard ones, the file name' +
                            'has to be provided, where the file has to be a csv file')

    parser.add_argument("--years_test", type=int, default=1, 
                        help='Number of years (a year is 364 days) in the test dataset. Used if ' +
                        ' begin_pred_date and end_pred_date are not provided.')

    parser.add_argument("--shuffle_train", type=int, default=1, 
                        help='Boolean that selects whether the validation and training datasets were' +
                        ' shuffled when performing the hyperparameter optimization.')

    parser.add_argument("--data_augmentation", type=int, default=0, 
                        help='Boolean that selects whether a data augmentation technique for DNNs is used')

    parser.add_argument("--new_recalibration", type=int, default=1, 
                        help='Boolean that selects whether we start a new recalibration or we restart an' +
                            ' existing one')

    parser.add_argument("--calibration_window", type=int, default=2, 
                        help='Number of years used in the training dataset for recalibration')

    parser.add_argument("--experiment_id", type=int, default=1, 
                        help='Unique identifier to read the trials file of hyperparameter optimization')

    parser.add_argument("--begin_pred_date", type=str, default=None, 
                        help='Optional parameter to select the pred dataset. Used in combination with ' +
                            'end_pred_date. If either of them is not provided, pred dataset is built ' +
                            'using the years_pred parameter. It should either be  a string with the ' +
                            ' following format d/m/Y H:M')

    parser.add_argument("--end_pred_date", type=str, default=None, 
                        help='Optional parameter to select the pred dataset. Used in combination with ' +
                            'begin_pred_date. If either of them is not provided, pred dataset is built ' +
                            'using the years_pred parameter. It should either be  a string with the ' +
                            ' following format d/m/Y H:M')

    args = parser.parse_args()

    nlayers = args.nlayers
    dataset = args.dataset
    years_test = args.years_test
    shuffle_train = args.shuffle_train
    data_augmentation = args.data_augmentation
    new_recalibration = args.new_recalibration
    calibration_window = args.calibration_window
    experiment_id = args.experiment_id
    begin_pred_date = args.begin_pred_date
    end_pred_date = args.end_pred_date

    path_datasets_folder = os.path.join('.', 'datasets')
    path_forecast_folder = os.path.join('.', 'forecast')
    path_hyperparameter_folder = os.path.join('.', 'hyperparameters')

    def make_predictions():

        # Pulling data from bigquery 
        client = bigquery.Client(project='643838572067')
        calibration_window = 1
        data, last_date = pull_data_from_bigquery(client, calibration_window)

        begin_pred_date = last_date + pd.Timedelta(hours=1)
        end_pred_date = begin_pred_date + pd.Timedelta(hours=24)

        print('begin_pred_date: ', begin_pred_date)
        print('end_pred_date: ', end_pred_date)



        df_train, df_pred = transform_data(data, begin_pred_date, end_pred_date)

        # Defining empty forecast array and the real values to be predicted in a more friendly format

        forecast_date = begin_pred_date
        print(forecast_date)


        model = DNN(
            experiment_id=experiment_id, path_hyperparameter_folder=path_hyperparameter_folder, nlayers=nlayers, 
            dataset=dataset, years_test=years_test, shuffle_train=shuffle_train, data_augmentation=data_augmentation,
            calibration_window=calibration_window)

        # For simulation purposes, we assume that the available data is
        # the data up to current date where the prices of current date are not known
        data_available = pd.concat([df_train, df_pred.loc[:forecast_date + pd.Timedelta(hours=23), :]], axis=0)

        # We extract real prices for current date and set them to NaN in the dataframe of available data

        print(data_available.loc[forecast_date:forecast_date + pd.Timedelta(hours=23), 'Price'].index)

        data_available.loc[forecast_date:forecast_date + pd.Timedelta(hours=23), 'Price'] = np.NaN

        print(data_available.tail(25))

        # Recalibrating the model with the most up-to-date available data and making a prediction
        # for the next day
        Yp = model.recalibrate_and_forecast_next_day(df=data_available, next_day_date=forecast_date)
        print(Yp)
        print(Yp.shape)
        preds = pd.DataFrame(Yp.T, columns=['price_prediction'], index=pd.date_range(start=forecast_date, periods=24, freq='H'))    

        errors = write_preds_bigquery(client, preds)
        if errors == []:
            print("New rows have been added.")
        else:
            print("Encountered errors while inserting rows: {}".format(errors))

    make_predictions()

    return("OK")




