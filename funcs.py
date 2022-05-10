import pickle
import pandas as pd
import numpy as np
from sktime.forecasting.arima import AutoARIMA
from sklearn.metrics import mean_absolute_percentage_error

def do_train(data):
    """Comprobar el MAPE y hacer retrain con autoarima si el mayor de 0.2"""
    data.Date = pd.to_datetime(data.Date, dayfirst=True)
    data = data.set_index('Date')
    weekly = data.groupby(pd.Grouper(freq='W')).sum()
    arima = AutoARIMA(start_p = 1, start_q = 1)
    arima.fit(weekly)
    with open('arima.pickle', 'wb') as f:
        pickle.dump(arima, f)
    return "refit done"
    

def do_predict(n_weeks=1):
    with open('arima.pickle', 'rb') as f:
        model = pickle.load(f)
    predictions = model.predict(fh=list(range(1,n_weeks+1)))
    return predictions