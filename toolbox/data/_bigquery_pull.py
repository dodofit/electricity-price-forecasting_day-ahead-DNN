import os
import pandas as pd
from google.cloud import bigquery


def pull_data_from_bigquery(client, calibration_window, path_datasets_folder):
    

    dataset_id = f"{client.project}.epf"

    table_id = 'load_generation forecast'

    dataset = client.get_dataset(dataset_id)

    past_data = 365 * (calibration_window) + 30 # Number of days in the past to be used for training, plus a margin of 30 days

    query = f"""
        SELECT * from {dataset_id}.{table_id} ORDER BY date ASC LIMIT {str(past_data*24)}
        """

    df = client.query(query).to_dataframe()[['date', 'price',  'load_forecast', 'generation_forecast', 'solar_forecast','wind_forecast']]
    df = df[['date', 'price',  'load_forecast', 'generation_forecast', 'solar_forecast','wind_forecast']]
    df = df.set_index('date')
    df.index.name = None
    df.columns = ['Price','Load forecast','Generation forecast','Prévision J-1 Solaire','Prévision J-1 Eolien']
    df = df.sort_index()
    df.index = df.index + pd.Timedelta(hours=2) # Changing timezone to UTC+2 because the algorithm is design to take full days starting at 00:00

    df.to_csv(os.path.join(path_datasets_folder, 'FR_NEW_UTC_W_RENEW.csv'))

    return df.index[-1]