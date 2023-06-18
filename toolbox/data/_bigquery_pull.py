import os
import pandas as pd
from google.cloud import bigquery


def pull_data_from_bigquery(client, calibration_window):
    
    #client = bigquery.Client(project='643838572067')

    dataset_id = f"{client.project}.epf"

    table_id = 'load_generation_forecast'

    dataset = client.get_dataset(dataset_id)

    past_data = 365 * (calibration_window) # Number of days in the past to be used for training, plus a margin of 30 days

    query = f"""
        SELECT * FROM `{dataset_id}.{table_id}` ORDER BY date DESC LIMIT {str(past_data*24)}
        """

    df = client.query(query).to_dataframe()[['date', 'price_',  'load_forecast_', 'generation_forecast_', 'solar_forecast_','wind_forecast_']]
    #df = df[['date', 'price',  'load_forecast', 'generation_forecast', 'solar_forecast','wind_forecast']]
    df = df.set_index('date')
    df.index.name = None
    df.columns = ['Price','Load forecast','Generation forecast','Prévision J-1 Solaire','Prévision J-1 Eolien']
    df = df.sort_index()
    df.index = df.index + pd.Timedelta(hours=2) # Changing timezone to UTC+2 because the algorithm is design to take full days starting at 00:00

    #df.to_csv(os.path.join(path_datasets_folder, 'FR_NEW_UTC_W_RENEW.csv'))

    return df, df.index[-1]

def transform_data(data, begin_pred_date, end_pred_date):
    """Function to read and import data from day-ahead electricity markets."""

    #data = data.set_index(data.columns[0])

    data.index = pd.to_datetime(data.index)

    columns = ['Price']
    n_exogeneous_inputs = len(data.columns) - 1

    for n_ex in range(1, n_exogeneous_inputs + 1):
        columns.append('Exogenous ' + str(n_ex))

    data.columns = columns

    try:
        begin_pred_date = pd.to_datetime(begin_pred_date, dayfirst=True)
        end_pred_date = pd.to_datetime(end_pred_date, dayfirst=True)
        print('\ntr\nbegin_pred_date: ', begin_pred_date)
        print('end_pred_date: ', end_pred_date)
    except ValueError:
        print("Provided values for dates are not valid")

    if begin_pred_date.hour != 0:
        raise Exception("Starting date for pred dataset should be midnight")
    if end_pred_date.hour != 23:
        if end_pred_date.hour == 0:
            end_pred_date = end_pred_date + pd.Timedelta(hours=23)
        else:
            raise Exception("End date for pred dataset should be at 0h or 23h")

    print('pred datasets: {} - {}'.format(begin_pred_date, end_pred_date))
    df_train = data.loc[:begin_pred_date - pd.Timedelta(hours=1), :]
    df_pred = data.loc[begin_pred_date:end_pred_date, :]

    return df_train, df_pred

def write_preds_bigquery(client, preds):
    dataset_id = f"{client.project}.epf"

    table_id = 'electricity_price_predictions'

    table = client.get_table(f"{dataset_id}.{table_id}")  # Make an API request.

    rows_to_insert = [
        {u"date": preds.index[i].strftime('%Y-%m-%d %H:%M:%S'), 
         u"price_prediction": float(preds.iloc[i, 0])} 
         
         for i in range(len(preds)-1)
    ]

    errors = client.insert_rows(table, rows_to_insert)  # Make an API request.

    return errors



    