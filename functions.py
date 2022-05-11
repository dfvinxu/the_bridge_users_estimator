import pickle
import pandas as pd
import numpy as np
from sktime.forecasting.arima import AutoARIMA
import pymysql

def do_train(data):
    data.columns = data.columns.str.lower()
    data.date = pd.to_datetime(data.date, dayfirst=True)
    data = data.set_index('date')
    weekly = data.groupby(pd.Grouper(freq='W')).sum()
    arima = AutoARIMA(
        start_p = 1, 
        start_q = 1,
        maxiter = 100,
        suppress_warnings=True
        )
    arima.fit(weekly)
    with open('arima.pickle', 'wb') as f:
        pickle.dump(arima, f)
    return "refit done"
    
def do_predict(n_weeks=1):
    with open('arima.pickle', 'rb') as f:
        model = pickle.load(f)
    predictions = model.predict(fh=list(range(1,n_weeks+1)))
    return predictions

def get_data(endpoint, password, user):
    """Conectarse a AWS y leer los datos"""
    db = pymysql.connect(host = endpoint,
                        user = user,
                        password = password,
                        cursorclass = pymysql.cursors.DictCursor)

def data_aws(endpoint, password, user): 
    db = pymysql.connect(host = endpoint,
                        user = user,
                        password = password,
                        cursorclass = pymysql.cursors.DictCursor
    )
    cursor = db.cursor()
    use_db = ''' USE users_web_db'''
    cursor.execute(use_db)
    sql = '''SELECT * FROM users_web'''
    cursor.execute(sql)
    mi_tabla = cursor.fetchall()
    data = pd.DataFrame(mi_tabla)
    db.close()
    return data