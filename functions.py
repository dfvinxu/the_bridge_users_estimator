import pickle
import pandas as pd
import numpy as np
from sktime.forecasting.arima import AutoARIMA
import pymysql

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

    # El objeto cursor es el que ejecutará las queries y devolverá los resultados
    cursor = db.cursor()

    cursor.connection.commit()
    use_db = ''' USE users_web_db'''
    cursor.execute(use_db)

    sql = '''SELECT * FROM users_web'''
    cursor.execute(sql)
    mi_tabla = cursor.fetchall()

    data = pd.DataFrame(mi_tabla)

    db.close()

    return data